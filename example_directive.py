"""
Example: Send directive to agents

This shows how to use send_directive() to dispatch tasks to initialized agents.
"""

from xwarm2 import send_directive, AGENTS

# Ensure agents are initialized first (run xwarm2.py)
if not AGENTS:
    print("ERROR: No agents initialized. Run 'python xwarm2.py' first.")
    exit(1)

# Send directive to AGENT001
print("Sending 'analyze_snapshot' directive to AGENT001...")
result = send_directive("AGENT001", "analyze_snapshot")

if result:
    print("\n=== AGENT001 RESPONSE ===")
    print(result)
else:
    print("\nERROR: Directive failed")
