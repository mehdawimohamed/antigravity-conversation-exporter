# Antigravity Chat Exporter

A simple, automated Python script to export your local [Google Antigravity IDE](https://gemini.google.com) conversations directly into beautifully formatted Markdown files.

Since Antigravity stores conversation payloads in a binary Protobuf SQLite format that isn't easily human-readable, this script automatically locates the clean, internal `transcript_full.jsonl` files and parses them into standard Markdown.

## Features
- **Automatic Discovery:** Automatically finds the correct `transcript_full.jsonl` file associated with a given Antigravity IDE SQLite database (`.db`) file.
- **Smart Naming:** Automatically names the output Markdown file using the conversation's UUID or a custom chat name you provide.
- **Sequential Exporting:** Prevents overwriting past exports by automatically prepending an incrementing sequence number (e.g., `001 - ...`, `002 - ...`).
- **Clean Markdown Formatting:** Filters out background tool outputs and internal system messages, leaving just a clean transcript of your prompts and the AI's responses.

## Installation

1. Ensure you have Python installed.
2. Clone this repository.

## Usage

Run the script from your terminal:

```bash
python export_chat.py
```

By default, the script looks for your currently active Antigravity chat ID and exports it to a folder named `exported conversations` inside the script's directory.

### Custom Arguments

You can optionally pass a custom chat name, or a path to a specific `.db` file:

```bash
# Provide a custom title for the exported Markdown file
python export_chat.py "My Cool Project"

# Provide a specific Antigravity .db file path
python export_chat.py "C:\path\to\your\conversation.db"

# Provide both
python export_chat.py "My Cool Project" "C:\path\to\your\conversation.db"
```

## How it works
Antigravity IDE stores chat databases locally in `%APPDATA%\.gemini\antigravity-ide\conversations\`. However, the messages inside are binary. This script extracts the UUID from the `.db` file and uses it to locate the human-readable conversation transcript stored in the `brain/` directory logs, converting it seamlessly to Markdown.
