# JARVIS

JARVIS is a local-first desktop AI assistant for Windows. It exposes a FastAPI daemon, a voice loop, an extensible tool/plugin framework, SQLite memory, action auditing, and safety gates for sensitive desktop and file-system operations.

This project is implementation-ready, but desktop automation is powerful. Start with `dry_run=true`, verify commands through the API/dashboard, then enable live execution deliberately.

## Capabilities

- Wake-word voice interface: "Jarvis"
- Speech-to-text via faster-whisper, with text input fallback
- Text-to-speech via Piper command-line binary, pyttsx3 fallback, or console output
- Natural-language command routing and multi-step planning
- Windows app detection and launch by natural name
- Desktop control through PyAutoGUI and pygetwindow
- File create/read/update/delete/move/copy/search with confirmation for destructive actions
- Browser automation through Playwright
- Clipboard history
- Screenshot and optional OCR
- SQLite conversation memory, preferences, and audit log
- Plugin system for app-specific automations

## Folder Structure

```text
jarvis/
  agent/              Planner, intent router, execution loop
  api/                FastAPI app and schemas
  apps/               Windows application registry
  audio/              Wake word, STT, TTS, voice loop
  automation/         Desktop, browser, clipboard, screen/OCR tools
  core/               Config, logging, audit, safety policies
  filesystem/         File-system agent and semantic-ish search
  memory/             SQLite persistence
  plugins/            Plugin loader and built-in plugins
  tools/              Tool protocol, registry, built-in tool adapters
scripts/              Windows helper scripts
tests/                Smoke tests
```

## Quick Start

1. Create and activate a virtual environment.

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Copy the environment template.

   ```powershell
   Copy-Item .env.example .env
   ```

3. Start in safe dry-run mode.

   ```powershell
   python -m jarvis.api.server
   ```

4. In another terminal, try commands through the CLI.

   ```powershell
   python -m jarvis.cli "open notepad"
   python -m jarvis.cli "create a file called notes.txt on my desktop with hello world"
   python -m jarvis.cli "search my documents for project proposal"
   ```

5. Start the voice loop.

   ```powershell
   python -m jarvis.audio.voice_loop
   ```

## Configuration

The most important settings live in `.env`.

- `JARVIS_DRY_RUN=true`: log actions without performing desktop/file writes.
- `JARVIS_PERMISSION_MODE=confirm`: require confirmation for sensitive actions.
- `JARVIS_WORKSPACE_ROOTS`: comma-separated allowed file roots.
- `JARVIS_STT_BACKEND=faster_whisper|console`
- `JARVIS_TTS_BACKEND=piper|pyttsx3|console`
- `JARVIS_LOCAL_LLM_URL`: optional OpenAI-compatible local model endpoint.

## API

Start the daemon:

```powershell
uvicorn jarvis.api.server:app --host 127.0.0.1 --port 8765
```

Endpoints:

- `POST /v1/command`: plan and execute a command.
- `GET /v1/apps`: list detected apps.
- `GET /v1/audit`: recent audited actions.
- `GET /v1/memory/conversation`: recent conversation turns.
- `POST /v1/confirm/{confirmation_id}`: approve a pending sensitive action.
- `POST /v1/deny/{confirmation_id}`: deny a pending sensitive action.

## Example Workflows

- "Jarvis, open VS Code."
- "Jarvis, create a folder called invoices on my desktop."
- "Jarvis, find files about Q4 planning in Documents."
- "Jarvis, open Chrome and search for Python FastAPI docs."
- "Jarvis, take a screenshot and tell me what text is visible."
- "Jarvis, rename draft.txt to final-draft.txt." Requires confirmation.
- "Jarvis, delete the temp folder." Requires confirmation, and is blocked outside allowed roots.

## Security Model

JARVIS classifies actions into three levels:

- `safe`: read-only or reversible actions, auto-executable.
- `sensitive`: file writes, app/window control, browser actions, clipboard changes. These require confirmation when `JARVIS_PERMISSION_MODE=confirm`.
- `dangerous`: destructive broad operations, system directories, credential files, shell execution, registry edits. These are blocked by default.

Every planned and executed action is written to the audit log with timestamp, command, tool, arguments, result, and safety classification.

## Production Notes

- Keep `JARVIS_DRY_RUN=true` until you trust the behavior.
- Restrict `JARVIS_WORKSPACE_ROOTS` to folders you are comfortable automating.
- Use a local LLM endpoint for private planning, or leave it unset to use the deterministic router.
- Run as a normal user, not Administrator.
- Do not store API keys in memory preferences or command history.

## Future Scaling

- Add a React/Tauri dashboard for live confirmations and plugin management.
- Add Windows UI Automation via `uiautomation` for richer accessibility-tree interaction.
- Replace simple semantic search with ChromaDB embeddings when a local embedding model is available.
- Add per-plugin permission manifests.
- Add signed plugin packages and sandboxed plugin execution.
- Add multi-agent workers for code editing, research, browser operations, and file operations.
