# MP3 ID3 Metadata Tool

This project applies ID3 metadata to MP3 files using a CSV track list. It can
write the artist, title, album, track number, and optional album artwork.

## Requirements

- Windows
- Python 3
- The `mutagen` Python package

Install the dependency from PowerShell:

```powershell
python -m pip install mutagen
```

If `python` is not available on your PATH, use the full path to your Python
executable, for example:

```powershell
C:\Users\julia\AppData\Local\Programs\Python\Python313\python.exe -m pip install mutagen
```

## CSV format

The CSV must contain these columns:

```csv
track_number,artist,title,album,old_filename,new_filename,image
1,The Smiths,The Queen Is Dead,Rank,02 Track 2.mp3,01 - The Queen Is Dead.mp3,cover.jpg
2,The Smiths,Panic,Rank,03 Track 3.mp3,02 - Panic.mp3,cover.jpg
```

Required columns:

- `track_number`: Positive integer written to the `TRCK` ID3 tag.
- `artist`: Written to the artist tag.
- `title`: Written to the title tag.
- `album`: Written to the album tag.
- `old_filename`: Existing MP3 filename to process.
- `image`: Album-art filename. Leave empty to skip artwork.
- `new_filename`: Destination filename for the processed MP3.

Place the CSV and album-art file in the MP3 directory, or use paths that are
relative to that directory. Absolute paths are also supported.

## Configure paths

Create or edit `info.txt` in the repository directory:

```text
MP3_DIR=C:\Music\Rank
CSV_FILE=C:\Music\Rank\tracks.csv
```

`MP3_DIR` is the directory containing the MP3 files and album artwork.
`CSV_FILE` is the CSV metadata file. Paths may contain spaces and may be
absolute or relative to the current working directory.

## Run from PowerShell

From the repository directory, run:

```powershell
python apply_csv_metadata.py
```

The script updates each MP3 named by `old_filename`, then renames it to
`new_filename`. After all rows succeed, it renames the MP3 directory to the
album name from the CSV. Existing album-art tags are replaced when an `image`
is provided. The script will not overwrite an existing destination file or
album directory.

All rows must use the same album name. The album name must be a valid single
directory name, not a path.

## Run with the Windows batch file

Edit the paths in `info.txt`, then double-click
`run_apply_csv_metadata.bat`. The batch file runs the Python script and keeps
the window open so that you can read the results.

If Python is not available through the `python` command, replace:

```bat
set "PYTHON=python"
```

with the full path to your Python executable:

```bat
set "PYTHON=C:\Users\julia\AppData\Local\Programs\Python\Python313\python.exe"
```

## Results and errors

The script prints one result for each CSV row and a final summary, for example:

```text
Completed: 14 updated, 0 errors
```

If any row fails, the script exits with a non-zero status. Common causes are:

- The `old_filename` does not exist in the MP3 directory.
- The `new_filename` already exists in the MP3 directory.
- The album directory name is unsafe or already exists.
- The artwork file in `image` does not exist.
- The `track_number` is not a positive integer.
- The file is not a valid or readable MP3.

Back up your MP3 files before running the tool, because ID3 metadata changes
are written directly to the files.
