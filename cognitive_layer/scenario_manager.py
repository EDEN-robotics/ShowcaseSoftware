"""
EDEN Scenario Manager: Handles the "Trauma Arc" demo logic
"""

from cognitive_layer.ego_core import EgoGraph
from typing import Dict, List
import asyncio


class ScenarioManager:
    """Manages demo scenarios and state transitions"""
    
    def __init__(self, ego_graph: EgoGraph):
        self.ego_graph = ego_graph
        self.current_state = "neutral"
        self.state_history: List[Dict] = []
    
    def get_state(self) -> Dict:
        """Get current scenario state"""
        return {
            "state": self.current_state,
            "personality": self.ego_graph.personality.to_dict(),
            "graph_nodes": self.ego_graph.graph.number_of_nodes(),
            "graph_edges": self.ego_graph.graph.number_of_edges()
        }
    
    def execute_trauma_arc(self) -> Dict:
        """
        Execute the full trauma arc scenario:
        State 1: Neutral -> State 2: Incident -> State 3: Aftermath -> State 4: Healing
        """
        results = []
        
        # State 1: Neutral
        self.current_state = "neutral"
        results.append({
            "step": 1,
            "state": "neutral",
            "description": "Initial neutral state",
            "personality": self.ego_graph.personality.to_dict()
        })
        
        # State 2: The Incident
        self.current_state = "incident"
        trauma_result = self.ego_graph.inject_trauma("John throws can at robot - sudden aggressive movement detected")
        results.append({
            "step": 2,
            "state": "incident",
            "description": "Trauma injected: John throws can",
            "personality": trauma_result["personality"],
            "trauma_id": trauma_result["trauma_id"]
        })
        
        # State 3: The Aftermath - Test interaction rejection
        self.current_state = "aftermath"
        test_interaction = self.ego_graph.filter_perception("Friendly wave from student")
        results.append({
            "step": 3,
            "state": "aftermath",
            "description": "Friendly interaction filtered through trauma",
            "perception": test_interaction,
            "personality": self.ego_graph.personality.to_dict()
        })
        
        # State 4: The Healing - Manual adjustment
        self.current_state = "healing"
        healing_result = self.ego_graph.update_personality("Agreeableness", 0.8)
        healing_result2 = self.ego_graph.update_personality("Neuroticism", 0.3)
        
        # Test interaction again
        test_interaction_2 = self.ego_graph.filter_perception("Friendly wave from student")
        results.append({
            "step": 4,
            "state": "healing",
            "description": "Personality adjusted - robot accepts interaction",
            "perception": test_interaction_2,
            "personality": self.ego_graph.personality.to_dict()
        })
        
        self.state_history.extend(results)
        return {
            "scenario": "trauma_arc",
            "steps": results,
            "final_state": self.get_state()
        }
    
    def reset_to_neutral(self) -> Dict:
        """Reset personality to neutral state"""
        self.ego_graph.personality = self.ego_graph.personality.__class__(
            Openness=0.5,
            Conscientiousness=0.5,
            Extroversion=0.5,
            Agreeableness=0.5,
            Neuroticism=0.5
        )
        self.ego_graph.graph.nodes["SELF"]["personality"] = self.ego_graph.personality.to_dict()
        self.ego_graph._reweight_edges()
        self.current_state = "neutral"
        
        return {
            "status": "reset",
            "state": self.get_state()
        }
    
    def simulate_interaction_sequence(self, interactions: List[Dict]) -> List[Dict]:
        """Simulate a sequence of interactions"""
        results = []
        for interaction in interactions:
            result = self.ego_graph.process_interaction(
                interaction["user"],
                interaction["action"]
            )
            results.append({
                "interaction": interaction,
                "result": result
            })
        return results


# Demo script function
async def run_demo():
    """Run the trauma arc demo"""
    from cognitive_layer.ego_core import EgoGraph
    
    print("=" * 60)
    print("EDEN TRAUMA ARC DEMO")
    print("=" * 60)
    
    ego_graph = EgoGraph()
    scenario = ScenarioManager(ego_graph)
    
    # Execute trauma arc
    arc_result = scenario.execute_trauma_arc()
    
    print("\nTRAUMA ARC EXECUTION:")
    print("-" * 60)
    for step in arc_result["steps"]:
        print(f"\nStep {step['step']}: {step['state'].upper()}")
        print(f"  Description: {step['description']}")
        print(f"  Personality: {step['personality']}")
        if 'perception' in step:
            print(f"  Perception Decision: {step['perception']['decision']}")
            print(f"  Filtered Intent: {step['perception']['filtered_intent']}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    
    return arc_result


if __name__ == "__main__":
    asyncio.run(run_demo())

