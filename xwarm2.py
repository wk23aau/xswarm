"""
xwarm2 v27 - Improved window switching with win32gui
"""

import time
import os
import uuid
import pyautogui
import pyperclip
import pywinauto
from pywinauto.findwindows import find_windows
from pywinauto import Application
import win32gui
import win32con
import json

# Import browser controller
try:
    from browser_controller import BrowserController
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    print("⚠️  Browser controller not available")

pyautogui.FAILSAFE = False

WORKSPACE_DIR = r"c:\Users\wk23aau\Documents\xauto\xwarm2"
AGENTS = {}
BROWSER = None  # Shared browser instance


def get_agent_dir(agent_id):
    return os.path.join(WORKSPACE_DIR, ".agent", agent_id)

def get_response_file(agent_id):
    return os.path.join(get_agent_dir(agent_id), "responses.txt")

def ensure_agent_dir(agent_id):
    """Create agent folder if it doesn't exist"""
    agent_dir = get_agent_dir(agent_id)
    os.makedirs(agent_dir, exist_ok=True)
    return agent_dir

def generate_msg_id():
    return f"MSG{uuid.uuid4().hex[:6].upper()}"

def build_init_message(agent_id, msg_id):
    # Use absolute path so agent writes to correct location regardless of workspace
    abs_path = f"c:/Users/wk23aau/Documents/xauto/xwarm2/.agent/{agent_id}/responses.txt"
    return f"Take your role as {agent_id}. Never write anything in chat except {agent_id}{msg_id}. Write your actual response into the file @{abs_path} and end with [{msg_id}]. Never read or analyse any other file unless asked."

def focus_window_by_handle(handle):
    """Focus window using win32gui for reliable switching"""
    try:
        # Restore if minimized
        if win32gui.IsIconic(handle):
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        
        # Bring to foreground
        win32gui.SetForegroundWindow(handle)
        time.sleep(0.5)
        
        # Click inside window to ensure focus
        rect = win32gui.GetWindowRect(handle)
        click_x = rect[0] + 200
        click_y = rect[1] + 200
        pyautogui.click(click_x, click_y)
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"  Focus error: {e}")
        return False

def send_message_to_window(handle, message):
    """Send message to specific window handle"""
    if not focus_window_by_handle(handle):
        return False
    
    # Ensure chat is open
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Type and send
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')
    return True

def wait_response(agent_id, msg_id, timeout=60):
    """Wait for response in file"""
    file = get_response_file(agent_id)
    start = time.time()
    
    while time.time() - start < timeout:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for msg_id in file
                    if msg_id in content:
                        return content
            except:
                pass 
        print(f"  {int(time.time()-start)}s...")
        time.sleep(2)
    return None

def spawn_agent(agent_id, handle):
    """Initialize agent in specific window"""
    print(f"\n--- {agent_id} ---")
    
    # Ensure agent dir exists and clear file
    ensure_agent_dir(agent_id)
    file = get_response_file(agent_id)
    if os.path.exists(file):
        os.remove(file)
    
    # New chat
    focus_window_by_handle(handle)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(1.5)
    
    # Send init message
    msg_id = generate_msg_id()
    message = build_init_message(agent_id, msg_id)
    print(f"  [{msg_id}]")
    
    if send_message_to_window(handle, message):
        resp = wait_response(agent_id, msg_id)
        if resp:
            print(f"  {agent_id} OK: {resp.strip()}")
            AGENTS[agent_id] = {"handle": handle, "status": "ready"}
            return True
    
    print(f"  {agent_id} FAIL")
    return False

def duplicate_workspace(handle):
    """Duplicate workspace in new window via command palette"""
    print("  Duplicating workspace...")
    focus_window_by_handle(handle)
    time.sleep(0.5)
    
    # Open command palette
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(0.5)
    
    # Type duplicate command
    pyautogui.write('duplicate workspace', interval=0.02)
    time.sleep(0.3)
    pyautogui.press('enter')
    
    # Wait for new window
    print("  Waiting for new window...")
    time.sleep(5)

def send_directive(agent_id, directive_name, msg_id=None, dir_id=None):
    """Send a directive task to a specific agent"""
    if agent_id not in AGENTS:
        print(f"ERROR: {agent_id} not initialized")
        return False
    
    if msg_id is None:
        msg_id = generate_msg_id()
    
    if dir_id is None:
        # Generate directive ID
        dir_id = f"DIR{uuid.uuid4().hex[:6].upper()}"
    
    # Build directive message
    directive_path = f"c:/Users/wk23aau/Documents/xauto/xwarm2/.agent/directives/{directive_name}.md"
    message = f"[{dir_id}] Execute directive @{directive_path}. Write your response to @c:/Users/wk23aau/Documents/xauto/xwarm2/.agent/{agent_id}/responses.txt starting with [{dir_id}][{msg_id}] and ending with [{msg_id}]."
    
    print(f"\n>>> Sending directive '{directive_name}' to {agent_id}")
    print(f"    DIR: {dir_id}")
    print(f"    MSG: {msg_id}")
    
    # Clear response file
    resp_file = get_response_file(agent_id)
    if os.path.exists(resp_file):
        os.remove(resp_file)
    
    # Send message to agent's window
    handle = AGENTS[agent_id]["handle"]
    if send_message_to_window(handle, message):
        resp = wait_response(agent_id, msg_id, timeout=120)
        if resp:
            print(f"    ✅ {agent_id} completed directive {dir_id}")
            # Store directive ID in agent info
            AGENTS[agent_id]["last_directive"] = dir_id
            return resp
        else:
            print(f"    ❌ {agent_id} timeout")
            return None
    
    print(f"    ❌ Failed to send message")
    return None

def send_browser_directive(agent_id, task_description, max_iterations=10):
    """
    Send browser automation task to agent with AI-driven execution loop.
    
    Agent sees browser state, decides actions, we execute, repeat until done.
    """
    global BROWSER
    
    if not BROWSER_AVAILABLE:
        print("❌ Browser not available")
        return None
    
    if agent_id not in AGENTS:
        print(f"ERROR: {agent_id} not initialized")
        return None
    
    # Start browser if not started
    if BROWSER is None:
        BROWSER = BrowserController()
        BROWSER.start(headless=False)
        print("🌐 Browser started")
    
    # Create initial tab
    if not BROWSER.state.pages:
        BROWSER.new_tab()
    
    print(f"\n🌐 Browser task for {agent_id}: {task_description}")
    
    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"\n  === Iteration {iteration}/{max_iterations} ===")
        
        # Get current browser state for AI
        browser_context = BROWSER.get_context_for_ai()
        
        # Build message with browser state + task
        msg_id = generate_msg_id()
        dir_id = f"DIRBROWSER{iteration}"
        
        message = f"""[{dir_id}] Browser Automation Task:

**Task**: {task_description}

**Current Browser State**:
```json
{json.dumps(browser_context, indent=2)[:2000]}
```

**Instructions**:
1. Analyze the current browser state above
2. Decide next action(s) to accomplish the task
3. Write actions as JSON array to @{agent_id}_response.txt

**Action Format**:
```json
[
  {{"type": "navigate", "url": "https://example.com"}},
  {{"type": "click", "selector": "button.search"}},
  {{"type": "done"}}
]
```

Available types: navigate, click, type, scroll, wait, screenshot, done

Write response to @c:/Users/wk23aau/Documents/xauto/xwarm2/.agent/{agent_id}/responses.txt
Start with [{dir_id}][{msg_id}], end with [{msg_id}]
"""
        
        # Send to agent
        handle = AGENTS[agent_id]["handle"]
        resp_file = get_response_file(agent_id)
        if os.path.exists(resp_file):
            os.remove(resp_file)
        
        print(f"  Asking {agent_id}...")
        if not send_message_to_window(handle, message):
            print("  ❌ Failed to send message")
            break
        
        # Wait for agent's decision
        resp = wait_response(agent_id, msg_id, timeout=60)
        if not resp:
            print("  ❌ No response")
            break
        
        print(f"  ✅ {agent_id} responded")
        
        # Parse actions from response
        try:
            # Extract JSON from response (handle markdown code blocks)
            actions_json = resp
            
            # Try to find JSON in markdown code block first
            if '```json' in resp:
                start = resp.find('```json') + len('```json')
                end = resp.find('```', start)
                if end != -1:
                    actions_json = resp[start:end].strip()
            # Fallback: find raw JSON array
            elif '[{' in resp:
                start = resp.find('[{')
                end = resp.rfind('}]') + 2
                if start != -1 and end > 1:
                    actions_json = resp[start:end]
            
            actions = json.loads(actions_json)
            
            print(f"  Found {len(actions)} action(s)")
            
            # Execute actions
            done = False
            for action in actions:
                print(f"    → {action.get('type', 'unknown')}")
                
                if action.get('type') == 'done':
                    done = True
                    print("    ✅ Task complete!")
                    break
                
                result = BROWSER.execute_action(action)
                if result['status'] == 'error':
                    print(f"    ❌ {result['message']}")
                else:
                    print(f"    ✅ {result['message']}")
            
            if done:
                break
                
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error: {e}")
            print(f"  Response: {resp[:200]}...")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            break
    
    print(f"\n✅ Browser task completed in {iteration} iteration(s)")
    return browser_context


def main():
    print("xwarm2 v30 - Auto duplicate workspace")
    print("=" * 40)
    
    # Get existing Antigravity windows
    handles = find_windows(title_re=".*Antigravity.*", visible_only=True)
    print(f"Found {len(handles)} Antigravity windows")
    
    if len(handles) < 1:
        print("\nPlease open at least 1 Antigravity window.")
        return
    
    # Duplicate workspace if only 1 window
    if len(handles) < 2:
        print("\nDuplicating workspace to create 2nd window...")
        duplicate_workspace(handles[0])
        
        # Re-scan
        handles = find_windows(title_re=".*Antigravity.*", visible_only=True)
        print(f"Now have {len(handles)} windows")
        
        if len(handles) < 2:
            print("ERROR: Duplicate failed. Try manually: Ctrl+Shift+P -> 'duplicate workspace'")
            return
    
    print("\nStarting in 3s...")
    time.sleep(3)
    
    # Spawn agents
    spawn_agent("AGENT001", handles[0])
    time.sleep(1)
    spawn_agent("AGENT002", handles[1])
    
    print("\n" + "=" * 40)
    print("AGENTS READY:")
    for a, info in AGENTS.items():
        print(f"  {a}: {info['status']} (Window Handle {info['handle']})")
    
    # === Browser Automation Demo ===
    if BROWSER_AVAILABLE:
        print("\n" + "=" * 40)
        print("DEMO: Browser Automation with AGENT001")
        print("=" * 40)
        
        result = send_browser_directive(
            "AGENT001",
            "Go to example.com and take a screenshot"
        )
        
        if result:
            print("\n✅ Browser automation complete!")
            print(f"Final URL: {result.get('current_page', {}).get('url', 'N/A')}")
    else:
        print("\n⚠️  Browser automation not available (Playwright not installed)")


if __name__ == "__main__":
    main()
