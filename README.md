# xswarm

**Multi-agent orchestration for Antigravity chat automation**

## Overview

xswarm automates interaction with multiple Antigravity chat windows, enabling parallel agent execution with file-based communication. Each agent operates in its own chat window and writes responses to dedicated files.

## Features

- ✅ **Auto-duplicate workspace** - Automatically creates second Antigravity window
- ✅ **Multi-window targeting** - Reliably switches between windows using win32gui
- ✅ **File-based responses** - Agents write to `.agent/{AGENT_ID}/responses.txt`
- ✅ **Message tracking** - Unique message IDs for request/response correlation
- ✅ **Absolute paths** - Works regardless of workspace configuration

## Requirements

- Windows
- Antigravity (Electron app)
- Python 3.7+
- Dependencies:
  ```bash
  pip install pyautogui pyperclip pywinauto pywin32
  ```

## Usage

1. **Open one Antigravity window**
2. **Run the script:**
   ```bash
   python xwarm2.py
   ```
3. Script will:
   - Duplicate workspace to create 2nd window
   - Spawn AGENT001 in window 1
   - Spawn AGENT002 in window 2
   - Each agent writes responses to `.agent/{ID}/responses.txt`

## How It Works

### Agent Protocol

Each agent receives an initialization message:
```
Take your role as AGENT001. Never write anything in chat except AGENT001MSG123456. 
Write your actual response into the file @c:/path/to/.agent/AGENT001/responses.txt and end with [MSG123456]. 
Never read or analyse any other file unless asked.
```

Agents respond in two places:
1. **Chat**: Magic string only (`AGENT001MSG123456`)
2. **File**: Full response ending with `[MSG123456]`

### File Structure

```
xwarm2/
├── .agent/
│   ├── directives/          # Task definitions
│   │   └── analyze_snapshot.md
│   ├── AGENT001/
│   │   └── responses.txt
│   └── AGENT002/
│       └── responses.txt
└── xwarm2.py
```

### Directive System

Send tasks to specific agents using directives:

```python
from xwarm2 import send_directive

# Send directive to AGENT001
result = send_directive("AGENT001", "analyze_snapshot")
print(result)
```

**Directive file** (`.agent/directives/analyze_snapshot.md`):
```markdown
# Directive: Analyze Snapshot

## Task
Analyze the provided snapshot and provide insights.

## Instructions
1. Review the snapshot content
2. Identify key patterns
3. Provide recommendations

## Snapshot
[paste content here]
```

**Agent workflow:**
1. Receives: `Execute directive @.agent/directives/analyze_snapshot.md`
2. Reads directive file
3. Executes task
4. Writes response to `.agent/{AGENT_ID}/responses.txt`

## Code Structure

- `duplicate_workspace()` - Uses command palette to clone Antigravity window
- `focus_window_by_handle()` - Switches active window using win32gui
- `spawn_agent()` - Initializes agent with new conversation
- `wait_response()` - Polls file for completion signal

## Version History

- **v30**: Auto-duplicate workspace via command palette
- **v29**: Absolute paths for cross-workspace compatibility
- **v28**: Multi-window spawning (deprecated)
- **v27**: win32gui for reliable window switching
- **v26**: File-based communication with message IDs

## Limitations

- Antigravity is single-instance - requires workspace duplication
- Relies on UI automation (keyboard shortcuts, clicks)
- Windows-only (uses win32gui)

## Future Enhancements

- [ ] Support for N agents (currently hardcoded to 2)
- [ ] Task dispatch to specific agents
- [ ] Response parsing and action execution
- [ ] Agent state persistence
- [ ] Cross-platform support

## License

MIT

## Author

wk23aau
