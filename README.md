# Antigravity Conversation Exporter & Profile Manager

A collection of Python utilities for power-users of **[Google Antigravity IDE](https://antigravity.google.com)**.

| Script | Purpose |
|---|---|
| [`export_chat.py`](#1-export_chatpy--conversation-exporter) | Export any Antigravity conversation to a clean Markdown file |
| [`antigravity_profile_manager.py`](#2-antigravity_profile_managerpy--profile-manager) | Create isolated IDE profiles and desktop shortcuts per user/project |

---

## Requirements

- **Python 3.8+**
- **Windows** (both scripts are Windows-only)
- **`rich` library** (required only by `antigravity_profile_manager.py`)

```bash
pip install rich
```

---

## 1. `export_chat.py` — Conversation Exporter

### Overview

Antigravity IDE stores all conversation data in binary Protobuf SQLite `.db` files located at:

```
%USERPROFILE%\.gemini\antigravity-ide\conversations\
```

These `.db` files are not human-readable. However, the IDE also maintains a clean, structured `transcript_full.jsonl` log for every conversation inside the `brain/` directory. This script locates and parses that log, stripping away internal tool calls and system noise, and produces a clean Markdown transcript of your prompts and the AI's responses.

### Output Location

Exported files are saved to an **`exported-conversations/`** folder created **next to the script itself** — regardless of which directory you run Python from. This makes the script fully portable and shareable.

```
antigravity-conversation-exporter/
├── export_chat.py
├── exported-conversations/       <- auto-created
│   ├── 001 - My First Chat.md
│   ├── 002 - Architecture Review.md
│   └── ...
```

### Sequential Numbering

Files are automatically numbered with a 3-digit prefix (`001 -`, `002 -`, ...) by scanning the output directory for existing exports and incrementing the highest number found. **Existing exports are never overwritten.**

### Transcript Filtering

The exporter reads every JSON line in the transcript and only keeps entries where:

- `source == "USER_EXPLICIT"` and `type == "USER_INPUT"` → rendered as `### User`
- `source == "MODEL"` and `type == "PLANNER_RESPONSE"` → rendered as `### Antigravity`

All internal tool calls, system messages, background task outputs, and other noise are silently discarded.

### Usage

```bash
# Export the most recently modified conversation (no arguments needed)
python export_chat.py

# Export the active conversation with a custom human-readable name
python export_chat.py "My Cool Chat Name"

# Export a specific .db file (name defaults to the UUID)
python export_chat.py "C:\path\to\conversation.db"

# Export a specific .db file with a custom name
python export_chat.py "My Cool Chat Name" "C:\path\to\conversation.db"
```

#### Argument Resolution Logic

| Arguments passed | `chat_name` | `.db` file used |
|---|---|---|
| None | UUID of latest `.db` | Latest modified `.db` in conversations dir |
| `"My Name"` | `"My Name"` | Latest modified `.db` in conversations dir |
| `"path/to/file.db"` | UUID from filename | The specified `.db` file |
| `"My Name"` `"path/to/file.db"` | `"My Name"` | The specified `.db` file |

### PowerShell Shortcut (Recommended)

Add this function to your PowerShell profile (`$PROFILE`) to call the exporter from any terminal without typing the full path:

```powershell
function export-chat {
    python "C:\path\to\antigravity-conversation-exporter\export_chat.py" $args
}
```

Reload your terminal and use:

```powershell
export-chat "Architecture Decision - Auth Module"
```

### How It Works (Internals)

1. **Resolve the `.db` file** — either from the command-line argument or by finding the most recently modified `.db` in `~\.gemini\antigravity-ide\conversations\`.
2. **Extract the UUID** from the `.db` filename (the filename *is* the conversation UUID).
3. **Locate the transcript** at:
   ```
   ~\.gemini\antigravity-ide\brain\<UUID>\.system_generated\logs\transcript_full.jsonl
   ```
   Falls back to `transcript.jsonl` if the `_full` variant doesn't exist.
4. **Parse and filter** each JSON line, keeping only user and model turns.
5. **Write Markdown** to `exported-conversations/<NNN> - <name>.md` next to the script.

---

## 2. `antigravity_profile_manager.py` — Profile Manager

### Overview

Antigravity IDE supports launching with a `--user-data-dir` flag, which completely isolates the IDE session (settings, extensions, conversation history) per directory. This is extremely useful when:

- You manage **multiple users** or **clients** on the same machine.
- You want **separate conversation histories** per project.
- You need to provide **pre-configured desktop shortcuts** for a set of users.

This script provides an interactive wizard and a CLI to create `.lnk` Windows shortcuts that launch Antigravity with a named, isolated profile pointing at a specific project folder.

### First-Run Setup

On first launch, the script runs a **setup wizard** that:

1. **Detects** the Antigravity IDE executable (defaults to `%LOCALAPPDATA%\Programs\Antigravity IDE\Antigravity.exe`).
2. **Prompts** for a default destination folder for shortcuts (defaults to `%USERPROFILE%\Desktop\Users`).
3. **Saves** the configuration to `~/.agy_profiles.json` for future runs.
4. **Optionally installs** the `agy-profiles` global CLI command (see [CLI Installation](#cli-installation)).

### Usage

```bash
# Launch the interactive wizard
python antigravity_profile_manager.py

# Re-run the setup wizard to change paths
python antigravity_profile_manager.py --reconfigure
```

### Interactive Wizard Flow

Once set up, the wizard loops and asks:

| Prompt | Description |
|---|---|
| **Base Profile/Shortcut Name** | The name used for both the profile (e.g., `User1`) and the `.lnk` file |
| **How many shortcuts to generate?** | Enter `1` for a single shortcut, or `N` to generate `User1.lnk`, `User2.lnk`, ... `UserN.lnk` |
| **Project Path** | The folder Antigravity will open. Defaults to `cwd` |
| **Destination folder** | Where the `.lnk` files are saved. Defaults to the configured desktop path |

#### Batch Shortcut Generation Example

```
Base Profile Name: Client
How many shortcuts: 5
Project Path: C:\Projects\client-app
Destination: C:\Users\adouma\Desktop\Clients
```

Creates `Client1.lnk` through `Client5.lnk`, each launching Antigravity with a fully isolated profile stored at:

```
%LOCALAPPDATA%\AntigravityProfiles\Client1\
%LOCALAPPDATA%\AntigravityProfiles\Client2\
...
%LOCALAPPDATA%\AntigravityProfiles\Client5\
```

### What a Generated Shortcut Contains

Each `.lnk` shortcut is created via a PowerShell `WScript.Shell` call and encodes:

```
Target:    C:\...\Antigravity.exe
Arguments: --user-data-dir="C:\Users\...\AntigravityProfiles\<ProfileName>" "<ProjectPath>"
```

This ensures each shortcut opens a completely sandboxed IDE instance.

### CLI Installation

During setup, you are offered the option to install a global `agy-profiles` command. This:

1. Creates `~\bin\agy-profiles.bat` — a wrapper that calls `python antigravity_profile_manager.py`.
2. Adds `~\bin` to the **user-level `PATH`** environment variable via the Windows Registry (`HKEY_CURRENT_USER\Environment`).
3. Broadcasts a `WM_SETTINGCHANGE` message to notify running processes (Explorer, terminals) of the PATH change — a terminal restart is usually sufficient.

After installation:

```powershell
agy-profiles               # launch the interactive wizard from anywhere
agy-profiles --reconfigure # re-run setup
```

### Configuration File

Settings are persisted to `~/.agy_profiles.json`:

```json
{
    "ide_path": "C:\\Users\\...\\Antigravity IDE\\Antigravity.exe",
    "dest_path": "C:\\Users\\...\\Desktop\\Users",
    "installed": true
}
```

---

## File Structure

```
antigravity-conversation-exporter/
├── export_chat.py                  # Conversation exporter
├── antigravity_profile_manager.py  # Profile & shortcut manager
├── README.md
└── exported-conversations/         # Auto-created by export_chat.py
    ├── 001 - First Export.md
    └── 002 - Second Export.md
```

## Related Windows Paths

| Path | Purpose |
|---|---|
| `~\.gemini\antigravity-ide\conversations\` | Raw Antigravity `.db` conversation files |
| `~\.gemini\antigravity-ide\brain\<UUID>\.system_generated\logs\` | Human-readable JSONL transcripts |
| `%LOCALAPPDATA%\AntigravityProfiles\<name>\` | Isolated IDE profile data per shortcut |
| `~\.agy_profiles.json` | Profile manager configuration |
| `~\bin\agy-profiles.bat` | Installed global CLI wrapper |
