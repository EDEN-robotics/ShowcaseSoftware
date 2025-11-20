"""
Test Knowledge Graph Generator
Creates artificial expansive knowledge graph simulating a house environment
"""

import uuid
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cognitive_layer.ego_core import EgoGraph, MemoryNode


class TestKnowledgeGraphGenerator:
    """Generates test knowledge graph with house environment"""
    
    def __init__(self, ego_graph: EgoGraph):
        self.ego_graph = ego_graph
    
    def generate_house_environment(self):
        """Generate comprehensive house environment knowledge graph"""
        print("[TestKG] Generating house environment knowledge graph...")
        
        # Rooms
        rooms = [
            {"name": "Living Room", "objects": ["sofa", "coffee table", "TV", "bookshelf", "lamp", "rug"]},
            {"name": "Kitchen", "objects": ["refrigerator", "stove", "sink", "microwave", "dishwasher", "counter", "cabinets"]},
            {"name": "Bedroom", "objects": ["bed", "dresser", "wardrobe", "nightstand", "mirror", "window"]},
            {"name": "Bathroom", "objects": ["toilet", "sink", "shower", "mirror", "towel rack", "medicine cabinet"]},
            {"name": "Office", "objects": ["desk", "chair", "computer", "monitor", "bookshelf", "filing cabinet"]},
            {"name": "Garage", "objects": ["car", "toolbox", "workbench", "shelves", "bicycle"]},
        ]
        
        # Generate room memories
        for room in rooms:
            room_memory = MemoryNode(
                id=f"room_{uuid.uuid4().hex[:8]}",
                content=f"Room: {room['name']}. Contains: {', '.join(room['objects'])}. This is a {room['name'].lower()} with typical furniture and fixtures.",
                importance=0.6,
                user_context=None,
                node_type="memory"
            )
            self.ego_graph.add_memory_node(room_memory)
            
            # Generate object memories for each room
            for obj in room['objects']:
                obj_memory = MemoryNode(
                    id=f"obj_{uuid.uuid4().hex[:8]}",
                    content=f"Object: {obj} is located in {room['name']}. It is a standard household item.",
                    importance=0.4,
                    user_context=None,
                    node_type="memory"
                )
                self.ego_graph.add_memory_node(obj_memory)
        
        print(f"[TestKG] Generated {len(rooms)} rooms with objects")
        
        # Generate spatial relationships
        spatial_memories = [
            "The kitchen is adjacent to the living room. There is a doorway connecting them.",
            "The bedroom is upstairs, accessible via stairs from the living room.",
            "The bathroom is next to the bedroom on the second floor.",
            "The office is on the first floor, near the front entrance.",
            "The garage is attached to the house, accessible from the kitchen side door.",
            "The living room has windows facing the front yard.",
            "The kitchen has a window overlooking the backyard.",
        ]
        
        for spatial in spatial_memories:
            spatial_memory = MemoryNode(
                id=f"spatial_{uuid.uuid4().hex[:8]}",
                content=spatial,
                importance=0.5,
                user_context=None,
                node_type="memory"
            )
            self.ego_graph.add_memory_node(spatial_memory)
        
        print(f"[TestKG] Generated {len(spatial_memories)} spatial relationship memories")
        
        # Generate interaction memories
        interactions = [
            {
                "content": "User Ian frequently works in the office. He spends evenings there.",
                "importance": 0.7,
                "user_context": "Ian"
            },
            {
                "content": "The red cup is usually on the kitchen counter near the sink.",
                "importance": 0.6,
                "user_context": None
            },
            {
                "content": "The robot has successfully navigated from living room to kitchen before.",
                "importance": 0.8,
                "user_context": None
            },
            {
                "content": "The coffee table in the living room is fragile. Handle with care.",
                "importance": 0.9,
                "user_context": None,
                "node_type": "threat"
            },
            {
                "content": "Student gave friendly high-five in the living room. Positive interaction.",
                "importance": 0.7,
                "user_context": "Student",
                "node_type": "joy"
            },
        ]
        
        for interaction in interactions:
            interaction_memory = MemoryNode(
                id=f"interaction_{uuid.uuid4().hex[:8]}",
                content=interaction["content"],
                importance=interaction["importance"],
                user_context=interaction.get("user_context"),
                node_type=interaction.get("node_type", "memory")
            )
            self.ego_graph.add_memory_node(interaction_memory)
        
        print(f"[TestKG] Generated {len(interactions)} interaction memories")
        
        # Generate navigation paths
        navigation_paths = [
            "Path from living room to kitchen: Move forward 3 meters, turn right 90 degrees, move forward 2 meters.",
            "Path from kitchen to garage: Exit through side door, turn left, move forward 1 meter.",
            "Path from living room to office: Move forward 2 meters, turn left, move forward 4 meters.",
            "Path from living room to bedroom: Go to stairs, ascend stairs, turn right, move forward 3 meters.",
        ]
        
        for path in navigation_paths:
            path_memory = MemoryNode(
                id=f"path_{uuid.uuid4().hex[:8]}",
                content=path,
                importance=0.7,
                user_context=None,
                node_type="memory"
            )
            self.ego_graph.add_memory_node(path_memory)
        
        print(f"[TestKG] Generated {len(navigation_paths)} navigation path memories")
        
        # Generate object properties
        object_properties = [
            "The red cup is lightweight, made of plastic. It can be grasped with standard gripper.",
            "The coffee table is 50cm tall, made of glass. It is fragile and requires careful handling.",
            "The sofa is large and soft. It cannot be moved by the robot.",
            "The refrigerator door opens outward. It requires 60cm clearance to open fully.",
            "The desk chair has wheels. It can be moved but is heavy (15kg).",
        ]
        
        for prop in object_properties:
            prop_memory = MemoryNode(
                id=f"prop_{uuid.uuid4().hex[:8]}",
                content=prop,
                importance=0.6,
                user_context=None,
                node_type="memory"
            )
            self.ego_graph.add_memory_node(prop_memory)
        
        print(f"[TestKG] Generated {len(object_properties)} object property memories")
        
        total_nodes = self.ego_graph.graph.number_of_nodes()
        total_edges = self.ego_graph.graph.number_of_edges()
        
        print(f"[TestKG] ✓ Knowledge graph generated:")
        print(f"  Total nodes: {total_nodes}")
        print(f"  Total edges: {total_edges}")
        print(f"  Rooms: {len(rooms)}")
        print(f"  Total objects: {sum(len(r['objects']) for r in rooms)}")
        print(f"  Spatial relationships: {len(spatial_memories)}")
        print(f"  Interactions: {len(interactions)}")
        print(f"  Navigation paths: {len(navigation_paths)}")
        print(f"  Object properties: {len(object_properties)}")
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "rooms": len(rooms),
            "objects": sum(len(r['objects']) for r in rooms),
            "spatial_relationships": len(spatial_memories),
            "interactions": len(interactions),
            "navigation_paths": len(navigation_paths),
            "object_properties": len(object_properties)
        }


def main():
    """Generate test knowledge graph"""
    print("=" * 60)
    print("EDEN Test Knowledge Graph Generator")
    print("=" * 60)
    
    # Initialize ego graph
    ego_graph = EgoGraph()
    
    # Generate house environment
    generator = TestKnowledgeGraphGenerator(ego_graph)
    stats = generator.generate_house_environment()
    
    print("\n" + "=" * 60)
    print("Test knowledge graph ready for planning tests!")
    print("=" * 60)
    
    return ego_graph, stats


if __name__ == "__main__":
    main()

