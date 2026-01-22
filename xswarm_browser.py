"""
xswarm Browser Agent Integration

Connects xswarm agents to browser_controller for web automation.
"""

from browser_controller import BrowserController
import json
import os

# Global browser instance shared across agents
BROWSER = None

def start_browser():
    """Start shared browser instance"""
    global BROWSER
    if BROWSER is None:
        BROWSER = BrowserController()
        BROWSER.start(headless=False)
        print("🌐 Browser started for xswarm agents")
    return BROWSER

def stop_browser():
    """Stop shared browser"""
    global BROWSER
    if BROWSER:
        BROWSER.stop()
        BROWSER = None

def execute_browser_directive(agent_id, directive_id, actions):
    """
    Execute browser actions from agent directive.
    
    Args:
        agent_id: Agent executing (e.g., "AGENT001")
        directive_id: Directive ID (e.g., "DIR_BROWSER_001")
        actions: List of action dicts to execute
        
    Returns:
        dict: Results with state, screenshots, extracted data
    """
    browser = start_browser()
    
    results = {
        "agent_id": agent_id,
        "directive_id": directive_id,
        "actions_executed": [],
        "final_state": None,
        "errors": []
    }
    
    # Execute each action
    for i, action in enumerate(actions):
        print(f"  Action {i+1}/{len(actions)}: {action['type']}")
        
        result = browser.execute_action(action)
        
        action_result = {
            "index": i + 1,
            "action": action,
            "result": result,
            "state_after": browser.state.to_dict()
        }
        
        results["actions_executed"].append(action_result)
        
        if result["status"] == "error":
            results["errors"].append({
                "action_index": i + 1,
                "error": result["message"]
            })
            print(f"    ❌ Error: {result['message']}")
        else:
            print(f"    ✅ {result['message']}")
    
    # Final state
    results["final_state"] = browser.get_context_for_ai()
    
    return results

def format_browser_response(directive_id, msg_id, results):
    """Format browser automation results for agent response file"""
    
    # Build action list
    actions_text = ""
    for i, action_result in enumerate(results["actions_executed"]):
        action = action_result["action"]
        result = action_result["result"]
        status = "✅" if result["status"] == "success" else "❌"
        
        actions_text += f"\n{i+1}. {action['type'].upper()}"
        if "url" in action:
            actions_text += f" to {action['url']}"
        if "selector" in action:
            actions_text += f"\n   Selector: {action['selector']}"
        if "x" in action and "y" in action:
            actions_text += f"\n   Coordinates: ({action['x']}, {action['y']})"
        actions_text += f"\n   Status: {status} {result['message']}\n"
    
    # Build errors section
    errors_text = "None"
    if results["errors"]:
        errors_text = "\n".join([
            f"- Action {e['action_index']}: {e['error']}" 
            for e in results["errors"]
        ])
    
    # Browser state
    state = results["final_state"]["browser_state"]
    state_text = f"""Active Page: {state['active_page']}
Total Tabs: {state['total_pages']}
Tabs:"""
    for page in state["pages"]:
        state_text += f"\n  - {page['id']}: {page['url']}"
    
    response = f"""[{directive_id}][{msg_id}]

## Task Goal
Browser automation via xswarm

## Actions Executed
{actions_text}

## Browser Final State
{state_text}

## Errors
{errors_text}

## Summary
Executed {len(results['actions_executed'])} actions. {len(results['errors'])} errors.

[{msg_id}]
"""
    
    return response


# Test/Example
if __name__ == "__main__":
    # Example: Agent receives browser directive
    actions = [
        {"type": "navigate", "url": "https://example.com"},
        {"type": "wait", "wait_ms": 2000},
        {"type": "screenshot", "path": "example.png"}
    ]
    
    results = execute_browser_directive("AGENT001", "DIR_BROWSER_001", actions)
    
    response = format_browser_response("DIR_BROWSER_001", "MSG123456", results)
    print("\n" + "="*50)
    print("AGENT RESPONSE:")
    print("="*50)
    print(response)
    
    stop_browser()
