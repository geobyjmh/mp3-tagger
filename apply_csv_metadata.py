#!/usr/bin/env python
"""Apply ID3 metadata from a CSV track list to MP3 files."""

import argparse
import csv
import mimetypes
import sys
from pathlib import Path

from mutagen import MutagenError
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1, TRCK
from mutagen.mp3 import MP3


REQUIRED_COLUMNS = {
    "track_number",
    "artist",
    "title",
    "album",
    "old_filename",
    "image",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply ID3 metadata from a CSV file to MP3 files."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing the MP3 files and album artwork",
    )
    parser.add_argument("csv_file", type=Path, help="CSV metadata file")
    return parser.parse_args()


def load_rows(csv_file):
    with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {names}")
        return list(reader)


def resolve_path(directory, filename):
    path = Path(filename)
    return path if path.is_absolute() else directory / path


def embed_image(tags, image_path):
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported album-art file type: {image_path}")

    with image_path.open("rb") as image_file:
        image_data = image_file.read()

    tags.delall("APIC:")
    tags.add(
        APIC(
            encoding=3,
            mime=mime_type,
            type=3,
            desc="",
            data=image_data,
        )
    )


def apply_row(directory, row):
    track_number = int(row["track_number"])
    if track_number < 1:
        raise ValueError("track_number must be at least 1")

    mp3_path = resolve_path(directory, row["old_filename"])
    if not mp3_path.is_file():
        raise FileNotFoundError(f"MP3 file not found: {mp3_path}")

    image_name = row["image"].strip()
    image_path = resolve_path(directory, image_name) if image_name else None
    if image_path and not image_path.is_file():
        raise FileNotFoundError(f"Album-art file not found: {image_path}")

    audio = MP3(mp3_path, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()

    audio.tags[TPE1.FrameID] = TPE1(encoding=3, text=[row["artist"]])
    audio.tags[TIT2.FrameID] = TIT2(encoding=3, text=[row["title"]])
    audio.tags[TALB.FrameID] = TALB(encoding=3, text=[row["album"]])
    audio.tags[TRCK.FrameID] = TRCK(encoding=3, text=[str(track_number)])

    if image_path:
        embed_image(audio.tags, image_path)

    audio.save()


def main():
    args = parse_args()

    if not args.directory.is_dir():
        print(f"Error: directory not found: {args.directory}", file=sys.stderr)
        return 1
    if not args.csv_file.is_file():
        print(f"Error: CSV file not found: {args.csv_file}", file=sys.stderr)
        return 1

    try:
        rows = load_rows(args.csv_file)
    except (OSError, csv.Error, ValueError) as error:
        print(f"Error reading CSV: {error}", file=sys.stderr)
        return 1

    if not rows:
        print("Error: CSV contains no track rows", file=sys.stderr)
        return 1

    processed = 0
    errors = 0
    for row_number, row in enumerate(rows, start=2):
        try:
            apply_row(args.directory, row)
            print(f"Updated row {row_number}: {row['old_filename']}")
            processed += 1
        except (OSError, MutagenError, ValueError, TypeError) as error:
            print(f"Error on CSV row {row_number}: {error}", file=sys.stderr)
            errors += 1

    print(f"Completed: {processed} updated, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
