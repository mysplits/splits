# Connecting TrainingPeaks

TrainingPeaks has no official Claude connector, and its official API is approval-gated. SPLITS uses the open-source **TrainingPeaks MCP server** by James McAulay: https://github.com/JamsusMaximus/trainingpeaks-mcp (MIT). It authenticates with the athlete's own browser session cookie, stores it encrypted in the system keyring and never shows it to Claude.

You need a shell on the athlete's computer: this runs from **Claude Code** (the Code tab of Claude Desktop, or the `claude` CLI). If you have no shell, tell the athlete to open the Code tab in Claude Desktop and say "Set up SPLITS" there.

Explain each step in one plain sentence before running it. The athlete never needs to type commands.

The athlete has already been told, in step 0 of `SKILL.md`, that this connection is unofficial and could be blocked, and has given their OK. Do not install anything without that OK.

## 1. Check what is there

- Python 3.10 or newer: `python3 --version` (macOS, Linux) or `py --version` / `python --version` (Windows). If it is missing, guide the athlete to install it from python.org (on Windows, tick "Add python.exe to PATH") and continue after.
- Git: `git --version`. If it is missing, download the repository as a zip from GitHub instead of cloning.
- If `~/trainingpeaks-mcp` already exists, skip to step 3.

## 2. Install

```bash
git clone https://github.com/JamsusMaximus/trainingpeaks-mcp.git ~/trainingpeaks-mcp
cd ~/trainingpeaks-mcp
python3 -m venv .venv
.venv/bin/pip install -e ".[browser]"            # macOS, Linux
.venv\Scripts\pip install -e ".[browser]"        # Windows
```

## 3. Authenticate

Ask the athlete to log into https://app.trainingpeaks.com in their usual browser first. Then:

```bash
.venv/bin/tp-mcp auth --from-browser auto        # Windows: .venv\Scripts\tp-mcp auth --from-browser auto
```

On macOS the system may ask for Keychain access: that is expected, browser cookies are encrypted.

If reading from the browser fails, use the manual way. The athlete does it, not you:
1. In TrainingPeaks, open the browser's developer tools (F12) → Application (Chrome, Edge) or Storage (Firefox) → Cookies → `https://app.trainingpeaks.com`.
2. Copy the value of `Production_tpAuth`.
3. Run `tp-mcp auth` **in their own terminal** and paste it there. Never ask them to paste the cookie into the chat.

Check with `tp-mcp auth-status`.

## 4. Register the server

For Claude Code (user scope, available in every project):

```bash
claude mcp add trainingpeaks -s user -- ~/trainingpeaks-mcp/.venv/bin/tp-mcp serve
# Windows: claude mcp add trainingpeaks -s user -- %USERPROFILE%\trainingpeaks-mcp\.venv\Scripts\tp-mcp.exe serve
```

For the Chat tab of Claude Desktop, run `tp-mcp config` and merge its snippet into `mcpServers` in:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Read the file first and keep every server already there.

## 5. Restart and verify

Ask the athlete to restart Claude Desktop (or start a new Claude Code session). Then call `tp_auth_status` and `tp_get_profile`. When the profile comes back, setup can continue.

## Later

- The session cookie expires after a few weeks. When `tp_*` calls start failing with auth errors, call `tp_refresh_auth` or run `tp-mcp auth` again.
- `scripts/build_workout.py` needs Python. Run it with the MCP's own interpreter: `~/trainingpeaks-mcp/.venv/bin/python` (Windows: `%USERPROFILE%\trainingpeaks-mcp\.venv\Scripts\python.exe`).
- To disconnect: `tp-mcp auth-clear` and remove the server from the config.
