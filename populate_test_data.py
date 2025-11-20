"""
Populate Cognitive Layer with Test Knowledge Graph
Run this to fill the graph with artificial house environment data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cognitive_layer.ego_core import EgoGraph
from planning_layer.test_knowledge_graph import TestKnowledgeGraphGenerator

def populate_cognitive_layer():
    """Populate cognitive layer with expansive test knowledge graph"""
    print("=" * 60)
    print("Populating Cognitive Layer with Test Knowledge Graph")
    print("=" * 60)
    
    # Initialize ego graph
    ego_graph = EgoGraph()
    
    print(f"\nInitial state:")
    print(f"  Nodes: {ego_graph.graph.number_of_nodes()}")
    print(f"  Edges: {ego_graph.graph.number_of_edges()}")
    
    # Generate house environment
    generator = TestKnowledgeGraphGenerator(ego_graph)
    stats = generator.generate_house_environment()
    
    print(f"\nFinal state:")
    print(f"  Nodes: {ego_graph.graph.number_of_nodes()}")
    print(f"  Edges: {ego_graph.graph.number_of_edges()}")
    
    # Add some user-specific memories
    print("\nAdding user-specific memories...")
    
    users = ["Ian", "Student", "Judge", "Dr. Smith"]
    for user in users:
        user_memory = {
            "id": f"user_{user.lower()}_001",
            "content": f"{user} is a frequent visitor. They often interact with the robot in the {['living room', 'kitchen', 'office'][hash(user) % 3]}.",
            "importance": 0.7,
            "user_context": user,
            "node_type": "memory"
        }
        from cognitive_layer.ego_core import MemoryNode
        memory = MemoryNode(**user_memory)
        ego_graph.add_memory_node(memory)
    
    print(f"  Added memories for {len(users)} users")
    
    # Add some interaction memories
    interactions = [
        {
            "content": "Ian asked the robot to pick up the red cup from the kitchen counter. The robot successfully completed this task.",
            "importance": 0.8,
            "user_context": "Ian",
            "node_type": "achievement"
        },
        {
            "content": "Student gave friendly high-five in the living room. Positive interaction, robot responded warmly.",
            "importance": 0.7,
            "user_context": "Student",
            "node_type": "joy"
        },
        {
            "content": "Judge observed the robot's cognitive capabilities during demonstration. Robot showed memory recall.",
            "importance": 0.9,
            "user_context": "Judge",
            "node_type": "memory"
        },
        {
            "content": "Dr. Smith tested the robot's planning abilities. Robot generated detailed action plan for moving objects.",
            "importance": 0.85,
            "user_context": "Dr. Smith",
            "node_type": "achievement"
        },
    ]
    
    for interaction in interactions:
        from cognitive_layer.ego_core import MemoryNode
        memory = MemoryNode(**interaction)
        ego_graph.add_memory_node(memory)
    
    print(f"  Added {len(interactions)} interaction memories")
    
    # Final stats
    final_nodes = ego_graph.graph.number_of_nodes()
    final_edges = ego_graph.graph.number_of_edges()
    
    print("\n" + "=" * 60)
    print("✓ Cognitive Layer Populated!")
    print("=" * 60)
    print(f"Total Nodes: {final_nodes}")
    print(f"Total Edges: {final_edges}")
    print(f"Rooms: {stats['rooms']}")
    print(f"Objects: {stats['objects']}")
    print(f"Users: {len(users)}")
    print(f"Interactions: {len(interactions)}")
    print("\nThe cognitive layer is now ready for planning demonstrations!")
    
    return ego_graph

if __name__ == "__main__":
    populate_cognitive_layer()

