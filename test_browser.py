"""
Test xswarm browser integration

This demonstrates how xswarm can dispatch browser automation tasks to xauto.
"""

from browser_integration import run_xauto_task
import json

# Example 1: Simple browse task
print("=" * 50)
print("Example 1: Browse testdevjobs")
print("=" * 50)

result = run_xauto_task("Go to testdevjobs.com and search for QA Analyst jobs")
print(json.dumps(result, indent=2))

# Example 2: Extract data
print("\n" + "=" * 50)
print("Example 2: Extract job listings")
print("=" * 50)

result = run_xauto_task(
    "Go to testdevjobs.com, search for 'Senior Developer', and extract the first 5 job titles"
)
print(json.dumps(result, indent=2))
