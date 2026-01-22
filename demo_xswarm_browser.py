"""
DEMO: xswarm + Browser Automation

Shows complete integration:
1. Start xswarm agents
2. Send browser directive to agent
3. Agent executes browser actions
4. Results written to response file
"""

from xswarm_browser import execute_browser_directive, format_browser_response, start_browser, stop_browser
import os

def demo():
    print("="*60)
    print("xswarm Browser Automation Demo")
    print("="*60)
    
    # Start browser
    print("\n1️⃣ Starting browser...")
    browser = start_browser()
    
    # Define browser task (what AI agent would generate)
    print("\n2️⃣ Agent decides actions...")
    actions = [
        {
            "type": "navigate",
            "url": "https://testdevjobs.com"
        },
        {
            "type": "wait",
            "wait_ms": 3000
        },
        {
            "type": "screenshot",
            "path": "screenshots/testdevjobs_home.png"
        },
        {
            "type": "click",
            "selector": "input[type='search']",  # Example selector
        },
        {
            "type": "type",
            "text": "QA Analyst",
            "selector": "input[type='search']"
        },
        {
            "type": "wait",
            "wait_ms": 1000
        },
        {
            "type": "screenshot",
            "path": "screenshots/search_filled.png"
        }
    ]
    
    # Execute via agent
    print("\n3️⃣ Executing browser actions...")
    results = execute_browser_directive(
        agent_id="AGENT001",
        directive_id="DIR_BROWSER_001",
        actions=actions
    )
    
    # Format response
    print("\n4️⃣ Formatting agent response...")
    response = format_browser_response(
        "DIR_BROWSER_001",
        "MSGTEST001",
        results
    )
    
    # Write to agent response file
    response_file = r"c:\Users\wk23aau\Documents\xauto\xwarm2\.agent\AGENT001\browser_demo_response.txt"
    os.makedirs(os.path.dirname(response_file), exist_ok=True)
    
    with open(response_file, 'w') as f:
        f.write(response)
    
    print(f"\n5️⃣ Response written to: {response_file}")
    
    # Display response
    print("\n" + "="*60)
    print("AGENT001 RESPONSE:")
    print("="*60)
    print(response)
    
    # Keep browser open for inspection
    print("\n" + "="*60)
    print("✅ Demo complete! Browser still open for inspection.")
    print("Press Enter to close browser and exit...")
    input()
    
    stop_browser()
    print("✅ Browser closed")

if __name__ == "__main__":
    demo()
