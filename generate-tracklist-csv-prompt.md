# Generate an Album Tracklist CSV

Please generate a CSV table for the tracklist of the album **"[ALBUM NAME]"** by **"[ARTIST NAME]"**.

Include the following columns:

- `track_number`: The track number as an integer.
- `artist`: The artist name (use **"[ARTIST NAME]"** for all tracks).
- `title`: The official track title.
- `album`: The album name (use **"[ALBUM NAME]"** for all tracks).
- `old_filename`: Sequential default filename formatted as `01 Track 1.mp3`, `02 Track 2.mp3`, etc., matching the overall row index.
- `new_filename`: Formatted as `XX - [Track Title].mp3`, where `XX` is the 2-digit zero-padded track number. Replace any invalid file path characters, such as `/`, `?`, or `:`, with underscores or clean text.
- `image`: Default string value `cover.jpg` for all rows.

Please output the result strictly in raw CSV format inside a code block so I can copy and save it as a `.csv` file.
