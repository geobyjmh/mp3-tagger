#!/usr/bin/env python
"""
mp3-tagger: Rename MP3 files and manage ID3 metadata.
"""

import click
from pathlib import Path
import yaml
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TRCK
from mutagen.mp3 import MP3
import sys


def load_metadata(yaml_path):
    """Load metadata from YAML file."""
    try:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Error: YAML file not found: {yaml_path}", err=True)
        sys.exit(1)
    except yaml.YAMLError as e:
        click.echo(f"Error: Invalid YAML file: {e}", err=True)
        sys.exit(1)


def validate_files(directory, metadata, album_art_path=None):
    """Validate that all files exist before processing."""
    errors = []
    dir_path = Path(directory)
    
    if not dir_path.is_dir():
        errors.append(f"Directory not found: {directory}")
    
    if album_art_path and album_art_path.strip():
        art_path = Path(album_art_path)
        if not art_path.exists():
            errors.append(f"Album art file not found: {album_art_path}")
    
    for track in metadata.get('tracks', []):
        old_filename = None
        # Find the original file in the directory
        dir_path = Path(directory)
        mp3_files = list(dir_path.glob('*.mp3'))
        
        # Track file by track number (01 Track 1.mp3 style)
        track_num = track.get('track_number')
        found = False
        for mp3_file in mp3_files:
            # Try to match by finding the file (simple heuristic)
            if mp3_file.exists():
                found = True
                break
        
        if not found and mp3_files:
            # If we can't match specifically, we'll handle during processing
            continue
    
    return errors


def embed_album_art(audio, album_art_path):
    """Embed album art into ID3 tags."""
    if not album_art_path or not album_art_path.strip():
        return
    
    art_path = Path(album_art_path)
    if not art_path.exists():
        click.echo(f"Warning: Album art not found: {album_art_path}")
        return
    
    try:
        with open(art_path, 'rb') as f:
            audio.tags.add(APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # Front cover
                desc='',
                data=f.read()
            ))
    except Exception as e:
        click.echo(f"Warning: Could not embed album art: {e}", err=True)


@click.group()
def cli():
    """MP3 tagger CLI."""
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.argument('yaml_file', type=click.Path(exists=True))
def process(directory, yaml_file):
    """Process MP3 files: rename and write ID3 metadata from YAML."""
    
    click.echo(f"Loading metadata from: {yaml_file}")
    metadata = load_metadata(yaml_file)
    
    album_art_path = metadata.get('album_art', '').strip()
    tracks = metadata.get('tracks', [])
    
    if not tracks:
        click.echo("Error: No tracks found in YAML file", err=True)
        sys.exit(1)
    
    # Validate files exist
    click.echo("Validating files...")
    errors = validate_files(directory, metadata, album_art_path)
    if errors:
        for error in errors:
            click.echo(f"Error: {error}", err=True)
        sys.exit(1)
    
    # Get album name from first track
    album_name = tracks[0].get('album')
    if not album_name:
        click.echo("Error: Album name not found in metadata", err=True)
        sys.exit(1)
    
    dir_path = Path(directory)
    new_dir_path = dir_path.parent / album_name
    
    # Rename directory if needed
    if dir_path != new_dir_path:
        click.echo(f"Renaming directory: {dir_path.name} -> {album_name}")
        try:
            dir_path.rename(new_dir_path)
            dir_path = new_dir_path
        except Exception as e:
            click.echo(f"Error renaming directory: {e}", err=True)
            sys.exit(1)
    
    processed_count = 0
    error_count = 0
    
    # Process each track
    for track in tracks:
        track_number = track.get('track_number')
        artist = track.get('artist')
        title = track.get('title')
        album = track.get('album')
        new_filename = track.get('new_filename')
        
        if not all([artist, title, album, new_filename]):
            click.echo(f"Warning: Incomplete metadata for track {track_number}", err=True)
            error_count += 1
            continue
        
        # Find the original MP3 file for this track
        # Simple strategy: find any unprocessed mp3 in order
        mp3_files = sorted(dir_path.glob('*.mp3'))
        if not mp3_files:
            click.echo(f"Error: No MP3 files found in {dir_path}", err=True)
            error_count += 1
            continue
        
        old_file = mp3_files[track_number - 1] if track_number - 1 < len(mp3_files) else None
        
        if not old_file or not old_file.exists():
            click.echo(f"Error: Could not find original file for track {track_number}", err=True)
            error_count += 1
            continue
        
        new_file = dir_path / new_filename
        
        try:
            # Load or create ID3 tags
            try:
                audio = MP3(str(old_file), ID3=ID3)
            except Exception:
                # Create new ID3 tag if it doesn't exist
                audio = MP3(str(old_file))
                audio.add_tags()
            
            # Write metadata tags
            audio.tags[TIT2.FrameID] = TIT2(encoding=3, text=[title])
            audio.tags[TPE1.FrameID] = TPE1(encoding=3, text=[artist])
            audio.tags[TALB.FrameID] = TALB(encoding=3, text=[album])
            audio.tags[TRCK.FrameID] = TRCK(encoding=3, text=[str(track_number)])
            
            # Embed album art if provided
            if album_art_path:
                embed_album_art(audio, album_art_path)
            
            # Save tags
            audio.save()
            
            # Rename file
            old_file.rename(new_file)
            
            click.echo(f"✓ Track {track_number}: {new_filename}")
            processed_count += 1
        
        except Exception as e:
            click.echo(f"✗ Error processing track {track_number}: {e}", err=True)
            error_count += 1
    
    # Summary
    click.echo(f"\nProcessing complete:")
    click.echo(f"  Processed: {processed_count}")
    if error_count > 0:
        click.echo(f"  Errors: {error_count}", err=True)
        sys.exit(1)
    else:
        click.echo(f"  All {processed_count} tracks successfully processed!")


if __name__ == '__main__':
    cli()
