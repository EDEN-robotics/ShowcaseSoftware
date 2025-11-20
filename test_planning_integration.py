#!/usr/bin/env python3
"""
Test Planning Integration
Tests the cognitive layer → planning layer integration
"""

import requests
import json

def test_planning_integration():
    """Test planning request through cognitive layer"""
    
    print("=" * 60)
    print("Testing EDEN Planning Integration")
    print("=" * 60)
    print()
    
    # Check services
    print("1. Checking services...")
    try:
        cog_status = requests.get("http://localhost:8000/api/graph/state", timeout=5)
        if cog_status.status_code == 200:
            cog_data = cog_status.json()
            print(f"   ✓ Cognitive Layer: {len(cog_data.get('nodes', []))} nodes")
        else:
            print(f"   ✗ Cognitive Layer: HTTP {cog_status.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Cognitive Layer: {e}")
        return
    
    try:
        plan_status = requests.get("http://localhost:8001/api/plan/status", timeout=5)
        if plan_status.status_code == 200:
            print(f"   ✓ Planning Layer: Running")
        else:
            print(f"   ✗ Planning Layer: HTTP {plan_status.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Planning Layer: {e}")
        return
    
    print()
    print("2. Testing planning request...")
    
    # Test goals
    test_cases = [
        {
            "goal": "Pick up the red cup from the kitchen counter",
            "user_context": "Ian",
            "description": "Simple object manipulation"
        },
        {
            "goal": "Move the blue book from the office desk to the living room bookshelf",
            "user_context": "Student",
            "description": "Multi-step navigation and manipulation"
        },
        {
            "goal": "Find and bring the toolbox from the garage to the kitchen",
            "user_context": None,
            "description": "Search and transport task"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['description']}")
        print(f"   Goal: {test_case['goal']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/plan/request",
                json={
                    "goal": test_case["goal"],
                    "user_context": test_case["user_context"]
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Success!")
                print(f"   Status: {result.get('status')}")
                print(f"   Memories used: {result.get('memories_used', 0)}")
                
                plan = result.get('plan', {})
                if plan:
                    print(f"   Plan actions: {len(plan.get('actions', []))}")
                    print(f"   Confidence: {plan.get('confidence', 0):.2f}")
                    if plan.get('reasoning'):
                        reasoning = plan.get('reasoning', '')[:100]
                        print(f"   Reasoning: {reasoning}...")
            else:
                print(f"   ✗ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  - Open http://localhost:8000 to see the graph visualization")
    print("  - Check that new plan memories were added to the graph")
    print("  - Try adjusting personality sliders and requesting plans again")

if __name__ == "__main__":
    test_planning_integration()

