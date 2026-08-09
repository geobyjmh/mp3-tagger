#!/usr/bin/env python
"""
mp3-tagger: Rename MP3 files and manage ID3 metadata.
"""

import click
from pathlib import Path


@click.group()
def cli():
    """MP3 tagger CLI."""
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path):
    """Show metadata for an MP3 file."""
    click.echo(f"Reading metadata from: {file_path}")
    # TODO: implement ID3 tag reading


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--title', help='Set title tag')
@click.option('--artist', help='Set artist tag')
@click.option('--album', help='Set album tag')
def set_metadata(file_path, title, artist, album):
    """Set metadata tags on an MP3 file."""
    click.echo(f"Setting metadata on: {file_path}")
    # TODO: implement ID3 tag writing


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', default='{artist} - {title}', help='Rename pattern')
def batch_rename(directory, pattern):
    """Batch rename MP3 files in a directory."""
    click.echo(f"Batch renaming MP3s in: {directory}")
    click.echo(f"Pattern: {pattern}")
    # TODO: implement batch renaming


if __name__ == '__main__':
    cli()
