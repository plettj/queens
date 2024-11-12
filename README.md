## LinkedIn Queens Parser

This repository contains a `chat-parser.py` file that intakes a `.txt` file copy-pasted from a Linkedin Chat, and parses out a `.csv` file full of the Queens results of each person specified.

## Usage

1. Copy-paste your entire LinkedIn chat with the queens information you want to process, and put it in `data/full-chat.txt`.

2. Update the names found in `parse-chat.py` to reflect the names of the people in your chat.

3. Ensure the dependencies are installed.

```bash
pip i os re csv collections
```

3. Run the processing file.

```bash
python parse-chat.py
```

And voila! You'll find all the data in `data/queens-times.csv`.
