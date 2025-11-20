"""
Test script for event processing system
"""

import json
from cognitive_layer.ego_core import EgoGraph

def test_event_processing():
    """Test the event processing pipeline"""
    print("=" * 60)
    print("Testing EDEN Event Processing System")
    print("=" * 60)
    
    # Initialize graph
    ego_graph = EgoGraph()
    
    # Test event 1: Important event (finished robot)
    print("\n1. Testing IMPORTANT event:")
    print("-" * 60)
    event1 = {
        "frame_id": "test_001",
        "description": "Ian just finished building the robot. This is a significant achievement.",
        "user_name": "Ian",
        "detected_actions": ["completed", "finished"],
        "source": "camera_frame"
    }
    
    result1 = ego_graph.process_event_frame(event1)
    print(f"Importance: {result1.get('importance', 0):.3f}")
    print(f"Threshold: {result1.get('threshold', 0):.3f}")
    print(f"Added to graph: {result1.get('added_to_graph', False)}")
    print(f"Reasoning: {result1.get('reasoning_trace', {}).get('llm_reasoning', 'N/A')[:100]}")
    
    # Test event 2: Low importance event
    print("\n2. Testing LOW IMPORTANCE event:")
    print("-" * 60)
    event2 = {
        "frame_id": "test_002",
        "description": "Ian making this robot is cool and all but might not be important to the graph",
        "user_name": "Ian",
        "detected_actions": ["observing"],
        "source": "camera_frame"
    }
    
    result2 = ego_graph.process_event_frame(event2)
    print(f"Importance: {result2.get('importance', 0):.3f}")
    print(f"Threshold: {result2.get('threshold', 0):.3f}")
    print(f"Added to graph: {result2.get('added_to_graph', False)}")
    print(f"Action: {result2.get('reasoning_trace', {}).get('action', 'N/A')}")
    
    # Test event 3: Batch processing
    print("\n3. Testing BATCH PROCESSING:")
    print("-" * 60)
    events_batch = [
        {
            "frame_id": "batch_001",
            "description": "Student gives friendly high-five",
            "user_name": "Student",
            "detected_actions": ["wave", "high-five"],
            "source": "camera_frame"
        },
        {
            "frame_id": "batch_002",
            "description": "Routine check of robot status",
            "detected_actions": ["check"],
            "source": "system"
        },
        {
            "frame_id": "batch_003",
            "description": "Major milestone achieved: robot can now walk",
            "user_name": "Ian",
            "detected_actions": ["achievement"],
            "source": "camera_frame"
        }
    ]
    
    batch_result = ego_graph.process_event_batch(events_batch)
    print(f"Total events: {batch_result.get('total_events', 0)}")
    print(f"Added to graph: {batch_result.get('added_to_graph', 0)}")
    print(f"Episodic memories: {batch_result.get('episodic_memories', 0)}")
    print(f"Errors: {batch_result.get('errors', 0)}")
    
    # Final graph state
    print("\n4. Final Graph State:")
    print("-" * 60)
    graph_state = ego_graph.get_graph_state()
    print(f"Total nodes: {len(graph_state.get('nodes', []))}")
    print(f"Total edges: {len(graph_state.get('links', []))}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_event_processing()

