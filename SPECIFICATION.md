# mp3-tagger Specification

## Goal
Rename MP3 files, rename containing folder to album name, and write ID3 metadata from a YAML file.

## Must Have Features

- Read YAML metadata file with track info and optional album_art path
- Rename the directory to the album name (from YAML)
- For each track:
  - Write ID3 tags (artist, title, album, track number, album art if specified)
  - Rename file to the name specified in YAML
- Batch process all tracks in a directory in one command
- Verify files and album art exist; report errors clearly

## YAML Schema

```yaml
album_art: "path/to/album.jpg"  # Optional
tracks:
  - track_number: 1
    artist: "Artist Name"
    title: "Track Title"
    album: "Album Name"
    new_filename: "01 - Artist - Track Title.mp3"
  - track_number: 2
    artist: "Artist Name"
    title: "Track Title 2"
    album: "Album Name"
    new_filename: "02 - Artist - Track Title 2.mp3"
```

## CLI Usage

```bash
python mp3_tagger.py process <directory> <metadata.yaml>
```

## Expected Behavior

1. Read metadata from YAML file
2. Validate that all MP3 files listed in YAML exist in the target directory
3. Validate that album_art file exists (if specified)
4. Rename directory to album name
5. For each track:
   - Write ID3 tags: artist, title, album, track number
   - Embed album art if specified
   - Rename file to new_filename
6. Report results: files processed, errors (if any)

## Error Handling

- Report missing MP3 files with clear error messages
- Report missing album art file with clear error messages
- Exit with non-zero status if any errors occur
- Provide descriptive feedback on successful completion
