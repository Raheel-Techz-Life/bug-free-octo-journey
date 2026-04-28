# Security Considerations

JARVIS can control your desktop and files. Treat it like a local automation service with meaningful privileges.

## Defaults

- Dry-run mode is enabled by default.
- Sensitive actions require confirmation by default.
- Broad destructive actions and protected system paths are blocked.
- Audit logging is always on.

## Recommended Production Posture

- Run as a normal user, not Administrator.
- Keep the API bound to `127.0.0.1`.
- Limit `JARVIS_WORKSPACE_ROOTS` to specific folders.
- Require confirmation for file writes, app control, clipboard writes, browser actions, and plugin actions.
- Review plugins before installing them.
- Do not expose the FastAPI port to a LAN or the public internet.
- Do not put secrets in commands, memory preferences, or plugin files.

## Blocked by Policy

- Windows and System32 writes.
- Program Files writes.
- SSH/GPG key modification.
- Registry editing.
- Shell command execution from natural-language commands.
- Recursive destructive operations outside allowed roots.
