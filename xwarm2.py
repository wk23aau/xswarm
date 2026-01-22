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

pyautogui.FAILSAFE = False

WORKSPACE_DIR = r"c:\Users\wk23aau\Documents\xauto\xwarm2"
AGENTS = {}

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
    print("FINAL RESULT:")
    for a, info in AGENTS.items():
        print(f"  {a}: {info['status']} (Window Handle {info['handle']})")

if __name__ == "__main__":
    main()
