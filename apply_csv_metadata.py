#!/usr/bin/env python
"""Apply ID3 metadata from a CSV track list to MP3 files."""

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


def load_config(config_file):
    values = {}
    with config_file.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid setting on line {line_number}; expected NAME=VALUE"
                )
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"')
            if name not in {"MP3_DIR", "CSV_FILE"}:
                raise ValueError(f"Unknown setting on line {line_number}: {name}")
            values[name] = value

    missing = {"MP3_DIR", "CSV_FILE"} - values.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"info.txt is missing required settings: {names}")
    return Path(values["MP3_DIR"]), Path(values["CSV_FILE"])


def load_rows(csv_file):
    with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("CSV must contain a header row")

        reader.fieldnames = [
            field.strip() if field else field for field in reader.fieldnames
        ]
        columns = set(reader.fieldnames)
        missing = REQUIRED_COLUMNS - columns
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {names}")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            if all(not (value or "").strip() for value in row.values()):
                continue
            if None in row:
                raise ValueError(f"CSV row {line_number} has too many columns")
            rows.append(
                {
                    key: value.strip() if isinstance(value, str) else value
                    for key, value in row.items()
                }
            )
        return rows


def resolve_path(directory, filename):
    path = Path(filename)
    return path if path.is_absolute() else directory / path


def embed_image(tags, image_path):
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported album-art file type: {image_path}")

    with image_path.open("rb") as image_file:
        image_data = image_file.read()

    for tag_key in list(tags.keys()):
        if tag_key.startswith("APIC"):
            del tags[tag_key]
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

    new_filename = row["new_filename"].strip()
    if not new_filename:
        raise ValueError("new_filename must not be empty")
    new_mp3_path = resolve_path(directory, new_filename)
    if new_mp3_path != mp3_path and new_mp3_path.exists():
        raise FileExistsError(f"Target filename already exists: {new_mp3_path}")

    image_name = row["image"].strip()
    image_path = resolve_path(directory, image_name) if image_name else None
    if image_path and not image_path.is_file():
        raise FileNotFoundError(f"Album-art file not found: {image_path}")

    audio = MP3(mp3_path, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()

    audio.tags["TPE1"] = TPE1(encoding=3, text=[row["artist"]])
    audio.tags["TIT2"] = TIT2(encoding=3, text=[row["title"]])
    audio.tags["TALB"] = TALB(encoding=3, text=[row["album"]])
    audio.tags["TRCK"] = TRCK(encoding=3, text=[str(track_number)])

    if image_path:
        embed_image(audio.tags, image_path)

    audio.save()
    if new_mp3_path != mp3_path:
        mp3_path.rename(new_mp3_path)
        return new_mp3_path
    return mp3_path


def main():
    config_file = Path(__file__).with_name("info.txt")
    if not config_file.is_file():
        print(f"Error: configuration file not found: {config_file}", file=sys.stderr)
        return 1

    try:
        directory, csv_file = load_config(config_file)
    except (OSError, ValueError) as error:
        print(f"Error reading configuration: {error}", file=sys.stderr)
        return 1

    if not directory.is_dir():
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        return 1
    if not csv_file.is_file():
        print(f"Error: CSV file not found: {csv_file}", file=sys.stderr)
        return 1

    try:
        rows = load_rows(csv_file)
    except (OSError, csv.Error, ValueError) as error:
        print(f"Error reading CSV: {error}", file=sys.stderr)
        return 1

    if not rows:
        print("Error: CSV contains no track rows", file=sys.stderr)
        return 1
    print(f"Loaded {len(rows)} track rows from {csv_file}")

    processed = 0
    errors = 0
    for row_number, row in enumerate(rows, start=2):
        try:
            final_path = apply_row(directory, row)
            print(f"Updated and renamed row {row_number}: {final_path.name}")
            processed += 1
        except (OSError, MutagenError, ValueError, TypeError) as error:
            print(f"Error on CSV row {row_number}: {error}", file=sys.stderr)
            errors += 1

    print(f"Completed: {processed} updated, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
