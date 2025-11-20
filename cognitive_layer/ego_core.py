"""
EDEN Cognitive Layer: The "Ego Engine"
Implements the Self-Modulating Knowledge Graph with Personality-Based Perception Filtering
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import chromadb
from chromadb.config import Settings
import json
import uuid
from datetime import datetime
from cognitive_layer import config
from cognitive_layer.llm_analyzer import CognitiveAnalyzer, LLMAnalysisResult

# Lazy import for SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using simple embeddings fallback.")


@dataclass
class PersonalityVector:
    """Big 5 Personality Traits"""
    Openness: float = 0.5
    Conscientiousness: float = 0.5
    Extroversion: float = 0.5
    Agreeableness: float = 0.5  # Kindness
    Neuroticism: float = 0.5    # Anxiety/Caution
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def update_trait(self, trait: str, value: float):
        """Update a specific trait, clamping to [0, 1]"""
        if hasattr(self, trait):
            setattr(self, trait, max(0.0, min(1.0, value)))


@dataclass
class MemoryNode:
    """Represents a memory/experience node in the graph"""
    id: str
    content: str
    importance: float  # 0.0 to 1.0 (0.9+ = Trauma/Joy)
    user_context: Optional[str] = None  # If None, it's global
    timestamp: str = None
    node_type: str = "memory"  # memory, trauma, joy, threat
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EventFrame:
    """Comprehensive event frame from vision system or other sources"""
    frame_id: str
    timestamp: str
    description: str  # VLM-generated frame description
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    detected_objects: Optional[List[str]] = None
    detected_actions: Optional[List[str]] = None
    emotional_tone: Optional[str] = None
    scene_context: Optional[str] = None
    metadata: Optional[Dict] = None
    source: str = "camera_frame"  # camera_frame, interaction, system
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.detected_objects is None:
            self.detected_objects = []
        if self.detected_actions is None:
            self.detected_actions = []
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EventFrame':
        """Create EventFrame from dictionary"""
        return cls(
            frame_id=data.get('frame_id', str(uuid.uuid4())),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            description=data.get('description', ''),
            user_id=data.get('user_id'),
            user_name=data.get('user_name'),
            detected_objects=data.get('detected_objects', []),
            detected_actions=data.get('detected_actions', []),
            emotional_tone=data.get('emotional_tone'),
            scene_context=data.get('scene_context'),
            metadata=data.get('metadata', {}),
            source=data.get('source', 'camera_frame')
        )
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MemoryEngine:
    """Manages User Context (Mem0 Style) and Global Context (Hive Mind)"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Use new ChromaDB API
        try:
            # Try new API first
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        except:
            try:
                # Fallback to old API if new one fails
                self.chroma_client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_directory
                ))
            except Exception as e:
                print(f"Warning: Could not initialize ChromaDB: {e}. Using in-memory fallback.")
                self.chroma_client = chromadb.Client()
        
        # Create collections
        try:
            self.user_memory_collection = self.chroma_client.get_collection("user_memories")
        except:
            self.user_memory_collection = self.chroma_client.create_collection("user_memories")
        
        try:
            self.global_memory_collection = self.chroma_client.get_collection("global_memories")
        except:
            self.global_memory_collection = self.chroma_client.create_collection("global_memories")
        
        # Initialize embedding model (lazy-loaded)
        self._embedder = None
        self._embedder_available = SENTENCE_TRANSFORMERS_AVAILABLE
    
    @property
    def embedder(self):
        """Lazy-load the embedding model"""
        if self._embedder is None:
            if self._embedder_available:
                try:
                    self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception as e:
                    print(f"Warning: Could not load SentenceTransformer: {e}")
                    self._embedder_available = False
                    self._embedder = self._create_fallback_embedder()
            else:
                self._embedder = self._create_fallback_embedder()
        return self._embedder
    
    def _create_fallback_embedder(self):
        """Create a simple fallback embedder using hash-based features"""
        class FallbackEmbedder:
            def encode(self, text):
                # Simple hash-based embedding for demo purposes
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_hex = hash_obj.hexdigest()
                # Convert hex to 384-dim vector (matching all-MiniLM-L6-v2)
                embedding = []
                for i in range(0, len(hash_hex), 2):
                    val = int(hash_hex[i:i+2], 16) / 255.0
                    embedding.append(val)
                # Pad to 384 dimensions
                while len(embedding) < 384:
                    embedding.extend(embedding[:384-len(embedding)])
                return np.array(embedding[:384])
        return FallbackEmbedder()
    
    def store_memory(self, memory: MemoryNode, embedding: List[float]):
        """Store a memory in the appropriate collection"""
        collection = self.global_memory_collection if memory.user_context is None else self.user_memory_collection
        
        collection.add(
            ids=[memory.id],
            embeddings=[embedding],
            documents=[memory.content],
            metadatas=[{
                "importance": memory.importance,
                "user_context": memory.user_context or "global",
                "timestamp": memory.timestamp,
                "node_type": memory.node_type
            }]
        )
    
    def retrieve_relevant_memories(self, query: str, user_context: Optional[str] = None, top_k: int = 5) -> List[MemoryNode]:
        """Retrieve relevant memories using semantic search"""
        query_embedding = self.embedder.encode(query).tolist()
        
        memories = []
        
        # Search user-specific memories if user_context provided
        if user_context:
            try:
                results = self.user_memory_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"user_context": user_context}
                )
                for i, doc_id in enumerate(results['ids'][0]):
                    memories.append(MemoryNode(
                        id=doc_id,
                        content=results['documents'][0][i],
                        importance=results['metadatas'][0][i]['importance'],
                        user_context=user_context,
                        timestamp=results['metadatas'][0][i]['timestamp'],
                        node_type=results['metadatas'][0][i].get('node_type', 'memory')
                    ))
            except:
                pass
        
        # Always search global memories
        try:
            results = self.global_memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            for i, doc_id in enumerate(results['ids'][0]):
                memories.append(MemoryNode(
                    id=doc_id,
                    content=results['documents'][0][i],
                    importance=results['metadatas'][0][i]['importance'],
                    user_context=None,
                    timestamp=results['metadatas'][0][i]['timestamp'],
                    node_type=results['metadatas'][0][i].get('node_type', 'memory')
                ))
        except:
            pass
        
        return memories


class EgoGraph:
    """The Self-Modulating Knowledge Graph"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.personality = PersonalityVector()
        self.memory_engine = MemoryEngine()
        self.cognitive_analyzer = CognitiveAnalyzer()
        self._initialize_self_node()
    
    def _initialize_self_node(self):
        """Create the central SELF node"""
        self.graph.add_node("SELF", 
                           node_type="self",
                           personality=self.personality.to_dict(),
                           size=50)
    
    def update_personality(self, trait: str, value: float) -> Dict:
        """Update personality trait and trigger graph ripple"""
        self.personality.update_trait(trait, value)
        
        # Update SELF node
        self.graph.nodes["SELF"]["personality"] = self.personality.to_dict()
        
        # Re-weight edges based on personality (Hebbian shift)
        self._reweight_edges()
        
        return {
            "personality": self.personality.to_dict(),
            "graph_state": self.get_graph_state()
        }
    
    def _reweight_edges(self):
        """Re-weight graph edges based on current personality"""
        # Edges connected to SELF are weighted by personality relevance
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            
            if source == "SELF" or target == "SELF":
                # Adjust weight based on personality traits
                base_weight = data.get('weight', 1.0)
                
                # Example: High neuroticism increases weight of threat nodes
                if self.graph.nodes[target].get('node_type') == 'threat':
                    data['weight'] = base_weight * (1.0 + self.personality.Neuroticism)
                elif self.graph.nodes[target].get('node_type') == 'joy':
                    data['weight'] = base_weight * (1.0 + self.personality.Agreeableness)
                else:
                    data['weight'] = base_weight
    
    def add_memory_node(self, memory: MemoryNode) -> str:
        """Add a memory node to the graph"""
        embedding = self.memory_engine.embedder.encode(memory.content).tolist()
        self.memory_engine.store_memory(memory, embedding)
        
        # Add node to graph
        node_size = 10 + (memory.importance * 20)  # Size based on importance
        self.graph.add_node(memory.id,
                           node_type=memory.node_type,
                           content=memory.content,
                           importance=memory.importance,
                           user_context=memory.user_context,
                           timestamp=memory.timestamp,
                           size=node_size)
        
        # Link to SELF if high importance (Hive Mind rule)
        if memory.importance > 0.9:
            self.graph.add_edge("SELF", memory.id, 
                               weight=memory.importance,
                               edge_type="global_memory")
        
        # Link to user subgraph if user_context exists
        if memory.user_context:
            user_node_id = f"USER_{memory.user_context}"
            if not self.graph.has_node(user_node_id):
                self.graph.add_node(user_node_id,
                                   node_type="user",
                                   user_id=memory.user_context,
                                   size=15)
                self.graph.add_edge("SELF", user_node_id, weight=0.5, edge_type="user_link")
            
            self.graph.add_edge(user_node_id, memory.id,
                               weight=memory.importance,
                               edge_type="user_memory")
        
        return memory.id
    
    def filter_perception(self, input_intent: str, user_context: Optional[str] = None) -> Dict:
        """
        Filter perception through personality lens
        Returns filtered interpretation and decision
        """
        original_intent = input_intent.lower()
        filtered_intent = original_intent
        decision = "accept"
        confidence = 1.0
        
        # Retrieve relevant memories
        relevant_memories = self.memory_engine.retrieve_relevant_memories(input_intent, user_context)
        
        # Apply personality filters
        if "sudden" in original_intent or "movement" in original_intent or "threat" in original_intent:
            if self.personality.Neuroticism > 0.8:
                filtered_intent = "THREAT_DETECTED"
                decision = "reject"
                confidence = self.personality.Neuroticism
            elif self.personality.Neuroticism < 0.2:
                filtered_intent = "EXCITEMENT"
                decision = "accept"
                confidence = 1.0 - self.personality.Neuroticism
        
        if "friendly" in original_intent or "kind" in original_intent or "help" in original_intent:
            if self.personality.Agreeableness > 0.7:
                filtered_intent = "POSITIVE_INTERACTION"
                decision = "accept"
                confidence = self.personality.Agreeableness
            elif self.personality.Agreeableness < 0.3:
                filtered_intent = "SKEPTICAL_INTERACTION"
                decision = "cautious"
                confidence = 0.5
        
        # Check for trauma nodes affecting perception
        trauma_nodes = [n for n in self.graph.nodes(data=True) 
                       if n[1].get('node_type') == 'trauma' or n[1].get('node_type') == 'threat']
        if trauma_nodes and self.personality.Neuroticism > 0.6:
            decision = "reject"
            filtered_intent = f"FILTERED_BY_TRAUMA: {filtered_intent}"
            confidence = self.personality.Neuroticism
        
        return {
            "original_intent": input_intent,
            "filtered_intent": filtered_intent,
            "decision": decision,
            "confidence": confidence,
            "relevant_memories": [m.to_dict() for m in relevant_memories[:3]],
            "personality_state": self.personality.to_dict()
        }
    
    def process_interaction(self, user: str, action: str) -> Dict:
        """Process an interaction: filter perception and generate response"""
        # Filter perception
        perception = self.filter_perception(action, user_context=user)
        
        # Create memory node for this interaction
        importance = 0.5  # Default importance
        if perception["decision"] == "reject":
            importance = 0.7  # Rejections are more memorable
        
        memory = MemoryNode(
            id=str(uuid.uuid4()),
            content=f"User {user} performed action: {action}. Filtered as: {perception['filtered_intent']}",
            importance=importance,
            user_context=user,
            node_type="memory"
        )
        
        memory_id = self.add_memory_node(memory)
        
        # Generate response based on decision
        if perception["decision"] == "accept":
            response = f"I understand. {action} noted."
        elif perception["decision"] == "reject":
            response = f"I'm not comfortable with that right now."
        else:
            response = f"I'm cautious about {action}."
        
        return {
            "thought_trace": perception,
            "response": response,
            "memory_id": memory_id,
            "graph_state": self.get_graph_state()
        }
    
    def inject_trauma(self, description: str) -> Dict:
        """Inject a trauma node (for demo)"""
        trauma = MemoryNode(
            id=str(uuid.uuid4()),
            content=description,
            importance=0.95,  # High importance trauma
            user_context=None,  # Global trauma
            node_type="threat"
        )
        
        trauma_id = self.add_memory_node(trauma)
        
        # Auto-adjust personality
        self.personality.Neuroticism = 0.9
        self.personality.Agreeableness = 0.1
        self.graph.nodes["SELF"]["personality"] = self.personality.to_dict()
        self._reweight_edges()
        
        return {
            "trauma_id": trauma_id,
            "personality": self.personality.to_dict(),
            "graph_state": self.get_graph_state()
        }
    
    def inject_kindness(self, description: str) -> Dict:
        """Inject a positive memory (for demo)"""
        joy = MemoryNode(
            id=str(uuid.uuid4()),
            content=description,
            importance=0.9,
            user_context=None,
            node_type="joy"
        )
        
        joy_id = self.add_memory_node(joy)
        
        # Auto-adjust personality
        self.personality.Agreeableness = min(1.0, self.personality.Agreeableness + 0.2)
        self.personality.Neuroticism = max(0.0, self.personality.Neuroticism - 0.1)
        self.graph.nodes["SELF"]["personality"] = self.personality.to_dict()
        self._reweight_edges()
        
        return {
            "joy_id": joy_id,
            "personality": self.personality.to_dict(),
            "graph_state": self.get_graph_state()
        }
    
    def get_graph_state(self) -> Dict:
        """Export graph state for frontend visualization"""
        nodes = []
        links = []
        
        for node_id, data in self.graph.nodes(data=True):
            node_info = {
                "id": node_id,
                "type": data.get("node_type", "unknown"),
                "size": data.get("size", 10),
                "personality": data.get("personality") if node_id == "SELF" else None,
                "content": data.get("content", "")[:50] if data.get("content") else "",
                "importance": data.get("importance", 0.5)
            }
            nodes.append(node_info)
        
        for source, target, data in self.graph.edges(data=True):
            link_info = {
                "source": source,
                "target": target,
                "weight": data.get("weight", 1.0),
                "type": data.get("edge_type", "default")
            }
            links.append(link_info)
        
        return {
            "nodes": nodes,
            "links": links,
            "personality": self.personality.to_dict()
        }
    
    def _heuristic_importance_score(self, event: EventFrame) -> float:
        """Heuristic layer: Quick keyword-based importance scoring"""
        description = event.description.lower()
        importance = 0.5
        
        # High importance keywords
        high_importance_keywords = [
            'finished', 'completed', 'achievement', 'important', 'significant',
            'milestone', 'breakthrough', 'accomplished', 'success', 'final',
            'done', 'created', 'built', 'finished building'
        ]
        high_count = sum(1 for kw in high_importance_keywords if kw in description)
        if high_count > 0:
            importance = min(0.9, 0.5 + high_count * 0.1)
        
        # Low importance keywords
        low_importance_keywords = [
            'cool', 'nice', 'casual', 'routine', 'normal', 'typical', 'just',
            'maybe', 'might', 'probably', 'sort of', 'kind of'
        ]
        low_count = sum(1 for kw in low_importance_keywords if kw in description)
        if low_count > 0:
            importance = max(0.2, importance - low_count * 0.1)
        
        # Action-based scoring
        if event.detected_actions:
            completion_actions = ['completed', 'finished', 'achieved', 'accomplished']
            if any(action.lower() in completion_actions for action in event.detected_actions):
                importance = max(importance, 0.7)
        
        return importance
    
    def _semantic_importance_score(self, event: EventFrame) -> float:
        """Semantic layer: Compare to existing important memories"""
        try:
            # Get top important memories
            important_memories = []
            for node_id, data in self.graph.nodes(data=True):
                if data.get('importance', 0) > 0.7:
                    important_memories.append({
                        'content': data.get('content', ''),
                        'importance': data.get('importance', 0.5)
                    })
            
            if not important_memories:
                return 0.5
            
            # Calculate similarity to important memories
            event_embedding = self.memory_engine.embedder.encode(event.description)
            similarities = []
            
            for mem in important_memories[:5]:  # Top 5 important memories
                mem_embedding = self.memory_engine.embedder.encode(mem['content'])
                # Cosine similarity
                similarity = np.dot(event_embedding, mem_embedding) / (
                    np.linalg.norm(event_embedding) * np.linalg.norm(mem_embedding)
                )
                similarities.append(similarity * mem['importance'])
            
            if similarities:
                max_similarity = max(similarities)
                # Boost importance if similar to important memories
                return min(0.95, 0.5 + max_similarity * 0.5)
        except Exception as e:
            print(f"Semantic analysis error: {e}")
        
        return 0.5
    
    def _apply_personality_modulation(self, base_importance: float, event: EventFrame, node_type: str) -> float:
        """Apply personality-based modulation to importance score"""
        personality = self.personality.to_dict()
        modulator = 1.0
        
        # Openness: Boost novel events
        if node_type not in ['routine', 'casual']:
            openness_boost = config.PERSONALITY_MODULATION['Openness']['novel_events']
            modulator += openness_boost * (personality['Openness'] - 0.5)
        
        # Conscientiousness: Boost achievements
        if node_type == 'achievement':
            consc_boost = config.PERSONALITY_MODULATION['Conscientiousness']['achievement_events']
            modulator += consc_boost * (personality['Conscientiousness'] - 0.5)
        
        # Extroversion: Boost social events
        if event.user_name or event.user_id:
            extro_boost = config.PERSONALITY_MODULATION['Extroversion']['social_events']
            modulator += extro_boost * (personality['Extroversion'] - 0.5)
        
        # Agreeableness: Boost positive social, reduce negative
        if node_type in ['joy', 'achievement']:
            agree_boost = config.PERSONALITY_MODULATION['Agreeableness']['positive_social']
            modulator += agree_boost * (personality['Agreeableness'] - 0.5)
        elif node_type in ['threat', 'trauma']:
            agree_reduce = config.PERSONALITY_MODULATION['Agreeableness']['negative_social']
            modulator += agree_reduce * (personality['Agreeableness'] - 0.5)
        
        # Neuroticism: Amplify threats and negative events
        if node_type in ['threat', 'trauma']:
            neuro_boost = config.PERSONALITY_MODULATION['Neuroticism']['threat_events']
            modulator += neuro_boost * personality['Neuroticism']
        elif node_type in ['joy', 'achievement']:
            neuro_reduce = config.PERSONALITY_MODULATION['Neuroticism']['positive_events']
            modulator += neuro_reduce * personality['Neuroticism']
        
        final_importance = base_importance * modulator
        return max(0.0, min(1.0, final_importance))
    
    def process_event_frame(self, event_data: Dict) -> Dict:
        """
        Process a single event frame through the cognitive pipeline
        
        Args:
            event_data: Dictionary containing event frame data
        
        Returns:
            Dict with processing results including importance, reasoning, and graph update
        """
        try:
            # Parse event
            event = EventFrame.from_dict(event_data)
            
            # Step 1: Retrieve relevant memories
            query_text = f"{event.description} {event.scene_context or ''}"
            relevant_memories = self.memory_engine.retrieve_relevant_memories(
                query_text,
                user_context=event.user_id or event.user_name,
                top_k=5
            )
            relevant_memories_dict = [m.to_dict() for m in relevant_memories]
            
            # Step 2: Run hybrid importance analysis
            # Heuristic layer
            heuristic_score = self._heuristic_importance_score(event)
            
            # Semantic layer
            semantic_score = self._semantic_importance_score(event)
            
            # LLM layer
            llm_result = self.cognitive_analyzer.analyze_event_importance(
                event.to_dict(),
                self.personality.to_dict(),
                relevant_memories_dict
            )
            
            # Combine scores (weighted average)
            base_importance = (
                heuristic_score * 0.2 +
                semantic_score * 0.3 +
                llm_result.importance * 0.5
            )
            
            # Step 3: Apply personality modulation
            final_importance = self._apply_personality_modulation(
                base_importance,
                event,
                llm_result.node_type
            )
            
            # Step 4: Determine threshold
            context = {
                'memory_count': self.graph.number_of_nodes(),
                'personality': self.personality.to_dict()
            }
            threshold = self.cognitive_analyzer.determine_threshold(llm_result.node_type, context)
            
            # Step 5: Decide whether to add to graph
            reasoning_trace = {
                "heuristic_score": heuristic_score,
                "semantic_score": semantic_score,
                "llm_score": llm_result.importance,
                "llm_reasoning": llm_result.reasoning,
                "base_importance": base_importance,
                "personality_modulation": final_importance / base_importance if base_importance > 0 else 1.0,
                "final_importance": final_importance,
                "threshold": threshold,
                "node_type": llm_result.node_type,
                "relevant_memories_count": len(relevant_memories)
            }
            
            memory_id = None
            added_to_graph = False
            
            if final_importance >= threshold:
                # Add to graph as MemoryNode
                memory = MemoryNode(
                    id=str(uuid.uuid4()),
                    content=f"{event.description} | User: {event.user_name or event.user_id or 'Unknown'} | Actions: {', '.join(event.detected_actions) if event.detected_actions else 'None'}",
                    importance=final_importance,
                    user_context=event.user_id or event.user_name,
                    timestamp=event.timestamp,
                    node_type=llm_result.node_type
                )
                memory_id = self.add_memory_node(memory)
                added_to_graph = True
                reasoning_trace["action"] = "added_to_graph"
            else:
                # Store as episodic memory (low-priority, may decay)
                reasoning_trace["action"] = "stored_as_episodic"
                reasoning_trace["episodic_reason"] = f"Importance {final_importance:.3f} below threshold {threshold:.3f}"
            
            return {
                "status": "processed",
                "event_id": event.frame_id,
                "importance": final_importance,
                "threshold": threshold,
                "added_to_graph": added_to_graph,
                "memory_id": memory_id,
                "reasoning_trace": reasoning_trace,
                "llm_analysis": {
                    "reasoning": llm_result.reasoning,
                    "node_type": llm_result.node_type,
                    "confidence": llm_result.confidence,
                    "emotional_impact": llm_result.emotional_impact,
                    "key_insights": llm_result.key_insights
                },
                "graph_state": self.get_graph_state()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "event_id": event_data.get('frame_id', 'unknown')
            }
    
    def process_event_batch(self, events_data: List[Dict]) -> Dict:
        """
        Process a batch of events
        
        Args:
            events_data: List of event dictionaries
        
        Returns:
            Dict with batch processing summary
        """
        results = []
        added_count = 0
        episodic_count = 0
        error_count = 0
        
        # Process events in order (maintain temporal ordering)
        for event_data in events_data:
            result = self.process_event_frame(event_data)
            results.append(result)
            
            if result.get("status") == "processed":
                if result.get("added_to_graph"):
                    added_count += 1
                else:
                    episodic_count += 1
            else:
                error_count += 1
        
        return {
            "status": "batch_processed",
            "total_events": len(events_data),
            "added_to_graph": added_count,
            "episodic_memories": episodic_count,
            "errors": error_count,
            "results": results,
            "graph_state": self.get_graph_state()
        }

