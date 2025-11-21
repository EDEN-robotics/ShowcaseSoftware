"""
NVIDIA Cosmos Reason1-7B Planner using vLLM (Text-Only Mode)
"""

import os
import re
import time
import torch
from typing import Dict, List, Optional, Tuple
from .config import *


class CosmosLite:
    """Lightweight Cosmos planner using vLLM with quantization"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or COSMOS_MODEL_PATH
        self.llm = None
        self.model_loaded = False
        self.gpu_available = False
        self.quantization = QUANTIZATION_METHOD
        
        # Check GPU availability
        self._check_gpu()
        
        # Load model if GPU available
        if self.gpu_available:
            self._load_model()
        else:
            print("[CosmosLite] GPU not available. Will use Ollama fallback.")
    
    def _check_gpu(self):
        """Check if GPU is available and meets requirements"""
        try:
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                
                print(f"[CosmosLite] GPU detected: {gpu_name}")
                print(f"[CosmosLite] GPU Memory: {gpu_memory:.1f} GB")
                
                if gpu_memory < MIN_GPU_MEMORY_GB:
                    print(f"[CosmosLite] Warning: GPU memory ({gpu_memory:.1f}GB) is below recommended ({MIN_GPU_MEMORY_GB}GB)")
                    print(f"[CosmosLite] Model may not fit. Consider using Ollama fallback.")
                    self.gpu_available = False
                else:
                    self.gpu_available = True
            else:
                print("[CosmosLite] No GPU detected. CUDA not available.")
                print("[CosmosLite] Troubleshooting:")
                print("  1. Check NVIDIA drivers: nvidia-smi")
                print("  2. Verify CUDA installation: nvcc --version")
                print("  3. Install PyTorch with CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu121")
                self.gpu_available = False
        except Exception as e:
            print(f"[CosmosLite] GPU check error: {e}")
            self.gpu_available = False
    
    def _load_model(self):
        """Load Cosmos model using vLLM"""
        if not os.path.exists(self.model_path):
            print(f"[CosmosLite] Model not found at {self.model_path}")
            print(f"[CosmosLite] Please download the model first:")
            print(f"  huggingface-cli download {COSMOS_MODEL_HF_ID} --local-dir {self.model_path}")
            self.model_loaded = False
            return
        
        try:
            print(f"[CosmosLite] Loading model from {self.model_path}...")
            print(f"[CosmosLite] Quantization: {self.quantization}")
            
            # Import vLLM
            try:
                from vllm import LLM, SamplingParams
            except ImportError:
                print("[CosmosLite] Error: vllm not installed. Run: pip install vllm==0.9.2")
                self.model_loaded = False
                return
            
            # Prepare vLLM arguments
            vllm_kwargs = {
                "model": self.model_path,
                "trust_remote_code": TRUST_REMOTE_CODE,
                "gpu_memory_utilization": GPU_MEMORY_UTILIZATION,
                "enforce_eager": ENFORCE_EAGER,
                "max_model_len": MAX_CONTEXT_LENGTH,
            }
            
            # Add quantization
            if self.quantization == "fp8":
                vllm_kwargs["quantization"] = "fp8"
            elif self.quantization == "awq":
                vllm_kwargs["quantization"] = "awq"
            # fp16 is default if quantization not specified
            
            # Load model
            self.llm = LLM(**vllm_kwargs)
            self.model_loaded = True
            
            print("[CosmosLite] ✓ Model loaded successfully")
            
        except Exception as e:
            print(f"[CosmosLite] Error loading model: {e}")
            print(f"[CosmosLite] Falling back to Ollama")
            self.model_loaded = False
    
    def _construct_prompt(self, goal: str, scene_description: str) -> str:
        """Construct ChatML format prompt for Cosmos"""
        # Truncate scene description if too long
        if len(scene_description) > MAX_SCENE_DESCRIPTION_LENGTH:
            scene_description = scene_description[:MAX_SCENE_DESCRIPTION_LENGTH] + "..."
        
        prompt = f"""<|im_start|>system
You are a robot planner. Use physics reasoning to plan actions.
<|im_end|>
<|im_start|>user
SCENE: {scene_description}
GOAL: {goal}
TASK: Think about the physics constraints, then output a JSON list of ROS2 actions.
Answer format: <think>...</think> <answer>...</answer>
<|im_end|>
<|im_start|>assistant
<think>
"""
        return prompt
    
    def _extract_reasoning_and_actions(self, response_text: str) -> Tuple[str, List[str]]:
        """
        Extract reasoning from <think> tags and actions from <answer> tags.
        Cosmos uses <think> for reasoning and <answer> for actions.
        """
        reasoning = ""
        actions = []
        
        # Try to extract reasoning from <think> tags
        reasoning_match = re.search(r'<think>(.*?)</think>', response_text, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            # Fallback: try <think> tags (some models use this)
            think_match = re.search(r'<think>(.*?)</think>', response_text, re.DOTALL)
            if think_match:
                reasoning = think_match.group(1).strip()
        
        # Try to extract actions from <answer> tags
        answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
        if answer_match:
            answer_text = answer_match.group(1).strip()
            # Try to parse as JSON list
            try:
                import json
                actions = json.loads(answer_text)
                if not isinstance(actions, list):
                    actions = [answer_text]
            except:
                # If not JSON, split by lines or commas
                if '\n' in answer_text:
                    actions = [line.strip() for line in answer_text.split('\n') if line.strip()]
                else:
                    actions = [a.strip() for a in answer_text.split(',') if a.strip()]
        else:
            # Fallback: look for reasoning patterns or extract from response
            if not reasoning:
                # Try to find reasoning-like text
                lines = response_text.split('\n')
                reasoning_lines = []
                action_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Heuristic: reasoning lines are longer, action lines are shorter commands
                    if len(line) > 50 or any(word in line.lower() for word in ['because', 'since', 'considering', 'reason']):
                        reasoning_lines.append(line)
                    else:
                        action_lines.append(line)
                
                reasoning = ' '.join(reasoning_lines) if reasoning_lines else "Physics reasoning applied."
                actions = action_lines if action_lines else [response_text.strip()]
        
        # Clean up actions
        actions = [a.strip() for a in actions if a.strip()]
        
        return reasoning, actions
    
    def plan(self, goal: str, scene_description: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate action plan using Cosmos.
        
        Args:
            goal: The goal to achieve (e.g., "Pick up the red cup")
            scene_description: Description of current scene from VLM
            context: Optional context dictionary from cognitive layer
        
        Returns:
            Dictionary with actions, reasoning, confidence, etc.
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. GPU unavailable or model not found.")
        
        start_time = time.time()
        
        try:
            # Construct prompt
            prompt = self._construct_prompt(goal, scene_description)
            
            # Prepare sampling parameters
            from vllm import SamplingParams
            sampling_params = SamplingParams(
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                top_k=TOP_K,
                stop=["<|im_end|>", "</answer>", "</think>"]
            )
            
            # Generate
            outputs = self.llm.generate([prompt], sampling_params)
            response_text = outputs[0].outputs[0].text
            
            # Extract reasoning and actions
            reasoning, actions = self._extract_reasoning_and_actions(response_text)
            
            inference_time = time.time() - start_time
            
            # Calculate confidence (based on response quality)
            confidence = self._calculate_confidence(response_text, reasoning, actions)
            
            # Check if inference was slow
            if inference_time > SLOW_INFERENCE_THRESHOLD:
                print(f"[CosmosLite] Warning: Slow inference ({inference_time:.2f}s). Consider using Ollama fallback.")
            
            return {
                "actions": actions,
                "confidence": confidence,
                "model_used": "cosmos",
                "inference_time": inference_time,
                "raw_response": response_text[:200] if len(response_text) > 200 else response_text
            }
            
        except Exception as e:
            print(f"[CosmosLite] Planning error: {e}")
            raise
    
    def _calculate_confidence(self, response_text: str, reasoning: str, actions: List[str]) -> float:
        """Calculate confidence score based on response quality"""
        confidence = 0.5  # Base confidence
        
        # Boost if reasoning is present
        if reasoning and len(reasoning) > 20:
            confidence += 0.2
        
        # Boost if actions are present
        if actions and len(actions) > 0:
            confidence += 0.2
        
        # Boost if response contains physics-related terms
        physics_terms = ['velocity', 'force', 'distance', 'grasp', 'move', 'rotate', 'position']
        if any(term in response_text.lower() for term in physics_terms):
            confidence += 0.1
        
        return min(0.95, confidence)
    
    def is_available(self) -> bool:
        """Check if Cosmos planner is available"""
        return self.model_loaded and self.gpu_available

