# Antigravity Chat Exporter

A simple, automated Python script to export your local [Google Antigravity IDE](https://antigravity.google.com) conversations directly into beautifully formatted Markdown files.

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

By default, the script exports the **currently active** Antigravity IDE conversation. Just run:

```bash
python export_chat.py
```

Or if you've added the PowerShell profile shortcut (see below), simply:

```powershell
export "My Cool Name"
```

The output is saved to an `exported conversations` folder inside the script's directory, automatically numbered (e.g., `001 - My Cool Name.md`, `002 - ...`).

### Arguments

```bash
# Export the active chat with a custom name
python export_chat.py "My Cool Name"

# Export a specific .db file
python export_chat.py "C:\path\to\your\conversation.db"

# Export a specific .db file with a custom name
python export_chat.py "My Cool Name" "C:\path\to\your\conversation.db"
```

### PowerShell Shortcut (optional)

To use the short `export "name"` command directly from your project root without typing `python export_chat.py`, add this function to your PowerShell profile (`$PROFILE`):

```powershell
function export { python "$pwd\export_chat.py" $args }
```

Then reload your terminal and run from your project root:

```powershell
export "My Cool Name"
```

## How it works
Antigravity IDE stores chat databases locally in `%APPDATA%\.gemini\antigravity-ide\conversations\`. However, the messages inside are binary. This script extracts the UUID from the `.db` file and uses it to locate the human-readable conversation transcript stored in the `brain/` directory logs, converting it seamlessly to Markdown.
