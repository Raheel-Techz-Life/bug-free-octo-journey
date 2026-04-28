# Example Voice Commands

```text
Jarvis, open notepad
Jarvis, open VS Code
Jarvis, switch to Chrome
Jarvis, close Notepad
Jarvis, search web for FastAPI lifespan handlers
Jarvis, create a folder called desktop/invoices
Jarvis, create a file called desktop/todo.txt with Review the JARVIS audit log
Jarvis, read file desktop/todo.txt
Jarvis, search documents for tax receipt
Jarvis, copy desktop/todo.txt to documents/todo-backup.txt
Jarvis, rename desktop/draft.txt to desktop/final.txt
Jarvis, delete desktop/temp.txt
Jarvis, copy to clipboard Meeting notes are ready
Jarvis, read clipboard
Jarvis, take a screenshot
Jarvis, read the screen
```

Sensitive commands return a confirmation id when dry-run is disabled and confirmation mode is on. Approve them through:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8765/v1/confirm/<confirmation_id>
```
