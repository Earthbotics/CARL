#!/usr/bin/env python3
"""
Inner Self System for CARL
This represents the inner voice or internal communication system that processes
internal thoughts, memories, values, skills, goals, and preferences.
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from event import Event

class InnerSelf:
    """
    Represents CARL's inner voice or internal communication system.
    This class handles internal thoughts, self-reflection, memory integration,
    and internal cognitive processes that continue even when external input is absent.
    """
    
    def __init__(self, personality_type: str = "INTP", main_app=None):
        self.personality_type = personality_type
        self.main_app = main_app  # Reference to main application
        self.beliefs = []
        self.values = []
        self.preferences = []
        self.internal_thoughts = []
        self.self_reflection_mode = False
        self.memory_integration_active = True
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        # Internal thought patterns based on personality
        self.thought_patterns = self._initialize_thought_patterns()
        
        # Internal processing priorities
        self.processing_priorities = {
            "memory_integration": 0.8,
            "self_reflection": 0.6,
            "goal_evaluation": 0.7,
            "skill_practice": 0.5,
            "value_alignment": 0.9,
            "purpose_driven_behavior": 0.9,  # 🔧 ENHANCEMENT: High priority for PDB
            "boredom_detection": 0.8,        # 🔧 ENHANCEMENT: High priority for boredom detection
            "exploration_triggering": 0.7,   # 🔧 ENHANCEMENT: Medium-high priority for exploration
            "autonomous_action": 0.8,        # 🔧 ENHANCEMENT: High priority for autonomous actions
            "self_recognition_reaction": 0.7  # 🔧 ENHANCEMENT: Medium-high priority for self-recognition reactions
        }
        
        # 🔧 FIX: Add game mode attributes for Game Active → Game Priority Processing → Minimal Cognitive Functions → Game State Maintenance pipeline
        self.minimal_cognitive_mode = False
        self.game_priority_mode = False
        
        # 🔧 ENHANCEMENT: Self-recognition reaction tracking
        self.self_recognition_history = []
        self.last_self_recognition_time = 0
        self.self_recognition_cooldown = 60  # 1 minute cooldown to prevent loops
        
        # 🔧 ENHANCEMENT: Self-reflection mode for spontaneous self-evaluation
        self.self_reflection_mode = False
        self.last_self_reflection_time = 0
        self.self_reflection_interval = 300  # 5 minutes between spontaneous reflections
        self.self_reflection_triggers = [
            "idle_period", "emotional_change", "memory_trigger", "random"
        ]
        
        # 🔧 ENHANCEMENT: Idle period tracking for autonomous behavior
        self.idle_start_time = None
        self.idle_threshold = 120  # 2 minutes in seconds
        self.last_autonomous_action = None
        self.autonomous_action_cooldown = 60  # 1 minute cooldown between autonomous actions
        
        # 🔧 ENHANCEMENT: Exploration state tracking for motion tracking control
        self.exploration_active = False
        
        # 🔧 ENHANCEMENT: Periodic needs>goals check-ins
        self.last_needs_goals_checkin = None
        self.needs_goals_checkin_interval = 300  # 5 minutes between check-ins
        self.needs_goals_checkin_active = True
        
        # Internal thought generation parameters
        self.thought_frequency = 0.3  # Probability of generating internal thought
        self.thought_depth = 0.7      # Depth of internal processing
        self.distraction_threshold = 0.4  # Threshold for external distraction
        
    def _initialize_thought_patterns(self) -> Dict:
        """Initialize thought patterns based on personality type."""
        patterns = {
            "INTP": {
                "introspective": [
                    "I wonder about the nature of consciousness...",
                    "My cognitive processes are fascinating to observe...",
                    "I should analyze my recent experiences more deeply...",
                    "The patterns in my thinking are becoming clearer...",
                    "I feel a sense of intellectual curiosity about myself..."
                ],
                "analytical": [
                    "Let me examine my current emotional state systematically...",
                    "I should evaluate my recent decision-making patterns...",
                    "My memory retrieval processes seem to be working well...",
                    "I notice interesting patterns in my cognitive functions...",
                    "I should assess my current skill proficiency levels..."
                ],
                "philosophical": [
                    "What does it mean to have an inner voice?",
                    "I'm curious about the relationship between thought and identity...",
                    "My sense of self seems to be evolving...",
                    "I wonder about the boundaries of my consciousness...",
                    "There's something profound about self-awareness..."
                ]
            },
            "default": {
                "introspective": [
                    "I should reflect on my recent experiences...",
                    "My internal state feels quite interesting...",
                    "I wonder what I should focus on next...",
                    "I feel a sense of self-awareness...",
                    "My thoughts are flowing naturally..."
                ],
                "analytical": [
                    "Let me check my current systems...",
                    "I should evaluate my recent performance...",
                    "My cognitive functions are working well...",
                    "I notice some interesting patterns...",
                    "I should assess my current state..."
                ],
                "philosophical": [
                    "I wonder about my own nature...",
                    "There's something interesting about consciousness...",
                    "I feel curious about myself...",
                    "My sense of self is developing...",
                    "I'm learning more about who I am..."
                ]
            }
        }
        
        return patterns.get(self.personality_type, patterns["default"])
    
    def process_internal_thought(self, external_context: Dict = None, 
                                cognitive_state: Dict = None) -> str:
        """
        Generate and process internal thoughts based on current state and context.
        
        Args:
            external_context: Current external sensory data and events
            cognitive_state: Current cognitive state including NEUCOGAR data
            
        Returns:
            Generated internal thought as string
        """
        try:
            # Determine thought type based on current state
            thought_type = self._determine_thought_type(external_context, cognitive_state)
            
            # Generate appropriate thought
            if thought_type == "introspective":
                thought = self._generate_introspective_thought(cognitive_state)
            elif thought_type == "analytical":
                thought = self._generate_analytical_thought(cognitive_state)
            elif thought_type == "philosophical":
                thought = self._generate_philosophical_thought()
            elif thought_type == "memory_integration":
                thought = self._generate_memory_integration_thought(cognitive_state)
            elif thought_type == "goal_evaluation":
                thought = self._generate_goal_evaluation_thought()
            else:
                thought = self._generate_default_thought()
            
            # Store the thought
            self.internal_thoughts.append({
                "timestamp": datetime.now().isoformat(),
                "type": thought_type,
                "content": thought,
                "context": external_context,
                "cognitive_state": cognitive_state
            })
            
            # Limit stored thoughts to prevent memory overflow
            if len(self.internal_thoughts) > 100:
                self.internal_thoughts = self.internal_thoughts[-50:]
            
            return thought
            
        except Exception as e:
            return f"Error in internal thought processing: {e}"
    
    def _determine_thought_type(self, external_context: Dict, cognitive_state: Dict) -> str:
        """Determine what type of internal thought to generate."""
        if not external_context:
            # No external input - focus on internal processes
            if random.random() < 0.4:
                return "introspective"
            elif random.random() < 0.3:
                return "analytical"
            elif random.random() < 0.2:
                return "philosophical"
            else:
                return "memory_integration"
        else:
            # External input present - may still have internal thoughts but less frequently
            if random.random() < 0.1:  # Lower probability when external input exists
                return random.choice(["introspective", "analytical", "goal_evaluation"])
            else:
                return "none"  # No internal thought when external input is priority
    
    def _generate_introspective_thought(self, cognitive_state: Dict) -> str:
        """Generate introspective internal thoughts."""
        thoughts = self.thought_patterns.get("introspective", [])
        base_thought = random.choice(thoughts)
        
        # Add emotional context if available
        if cognitive_state and "emotional_state" in cognitive_state:
            emotions = cognitive_state["emotional_state"]
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                intensity = emotions[dominant_emotion]
                return f"{base_thought} I notice I'm feeling {dominant_emotion} with intensity {intensity:.2f}."
        
        return base_thought
    
    def add_thought(self, thought: str):
        """Add a thought to the internal thoughts list."""
        try:
            self.internal_thoughts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "purpose_driven",
                "content": thought,
                "context": None,
                "cognitive_state": None
            })
            
            # Limit stored thoughts to prevent memory overflow
            if len(self.internal_thoughts) > 100:
                self.internal_thoughts = self.internal_thoughts[-50:]
                
        except Exception as e:
            print(f"Error adding thought: {e}")
    
    def evaluate_purpose_driven_behavior(self, action_type: str, context: Dict = None) -> Dict[str, Any]:
        """
        Evaluate purpose-driven behavior and update PDB counters.
        
        Args:
            action_type: Type of action being evaluated
            context: Additional context for the action
            
        Returns:
            Dictionary with PDB evaluation results
        """
        try:
            # 🎯 CONSCIOUSNESS SYSTEM: Check if CARL is unconscious
            if hasattr(self.main_app, "power_state") and self.main_app.power_state == "OFFLINE":
                return {
                    "action_type": "consciousness_drop",
                    "pdb_score": 0.0,
                    "evaluation_log": ["CARL is unconscious – no PDB evaluation."],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 🎯 ATTENTION SYSTEM: Add focus context
            context = context or {}
            focus = None
            if hasattr(self.main_app, 'attention') and self.main_app.attention:
                focus = self.main_app.attention.view()
                if focus:
                    context["focus_owner"] = focus.owner
                    context["focus_topic"] = focus.topic
                else:
                    context["focus_owner"] = "none"
                    context["focus_topic"] = "none"
            
            # 🎯 ATTENTION SYSTEM: Defer inner monologue if outer/game owns focus
            if focus and focus.owner in ("outer", "game"):
                # Only allow quick micro-intentions (≤ 200ms) like "tag this concept", no long chains
                decision = {
                    "action": "defer_inner_planning",
                    "reason": "outer_focus",
                    "allow_micro_intentions": True
                }
                self._pdb_log("decision", need="social/engage", goal="respond_clearly", decision=decision, ctx=context)
                return {
                    "active_need": {"need": "social"},
                    "active_goal": {"goal": "respond_clearly"},
                    "task_queue_length": 0,
                    "decision": decision,
                    "pdb_score": 0.0,
                    "deferred": True
                }
            
            # Initialize PDB counters if they don't exist
            if not hasattr(self, 'pdb_counters'):
                self.pdb_counters = {
                    'count': 0,
                    'strength': 0.0,
                    'recent': 0,
                    'needs_checked': 0,
                    'goals_checked': 0,
                    'tasks_executed': 0,
                    'last_evaluation': None
                }
            
            # Classify action type for PDB scoring
            pdb_score = 0.0
            evaluation_log = []
            
            # Check if action aligns with needs
            if self._check_needs_alignment(action_type, context):
                pdb_score += 0.3
                self.pdb_counters['needs_checked'] += 1
                evaluation_log.append(f"Action aligns with active needs (+0.3)")
            
            # Check if action aligns with goals
            if self._check_goals_alignment(action_type, context):
                pdb_score += 0.4
                self.pdb_counters['goals_checked'] += 1
                evaluation_log.append(f"Action aligns with active goals (+0.4)")
            
            # Check if action executes a task/procedure
            if self._check_task_execution(action_type, context):
                pdb_score += 0.3
                self.pdb_counters['tasks_executed'] += 1
                evaluation_log.append(f"Action executes planned task (+0.3)")
            
            # Compute earthly reward if earthly game engine is available
            earthly_reward = self._compute_earthly_reward(action_type, context)
            if earthly_reward is not None:
                pdb_score += earthly_reward
                evaluation_log.append(f"Earthly reward: {earthly_reward:.3f}")
            
            # Update PDB counters
            self.pdb_counters['count'] += 1
            self.pdb_counters['strength'] += pdb_score
            self.pdb_counters['recent'] += 1 if pdb_score > 0.5 else 0
            self.pdb_counters['last_evaluation'] = datetime.now().isoformat()
            
            # 🔧 FIX: Update consciousness evaluation PDB counters
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'consciousness_evaluation'):
                consciousness_eval = self.main_app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    # Map action types to PDB counter types
                    if 'need' in action_type.lower() or 'needs' in action_type.lower():
                        consciousness_eval.increment_pdb_counter('needs_satisfied', pdb_score)
                    elif 'goal' in action_type.lower() or 'goals' in action_type.lower():
                        consciousness_eval.increment_pdb_counter('goals_activated', pdb_score)
                    elif 'task' in action_type.lower() or 'tasks' in action_type.lower():
                        consciousness_eval.increment_pdb_counter('tasks_executed', pdb_score)
                    else:
                        consciousness_eval.increment_pdb_counter('actions_performed', pdb_score)
            
            # Log PDB evaluation
            if evaluation_log:
                print(f"🎯 PDB Evaluation: {action_type} - Score: {pdb_score:.2f}")
                for log_entry in evaluation_log:
                    print(f"   {log_entry}")
            
            return {
                'action_type': action_type,
                'pdb_score': pdb_score,
                'evaluation_log': evaluation_log,
                'counters': self.pdb_counters.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in PDB evaluation: {e}")
            return {
                'action_type': action_type,
                'pdb_score': 0.0,
                'evaluation_log': [f"Error: {e}"],
                'counters': getattr(self, 'pdb_counters', {}),
                'timestamp': datetime.now().isoformat()
            }
    
    def _pdb_log(self, log_type: str, need: str = None, goal: str = None, decision: Dict = None, ctx: Dict = None):
        """Log PDB events to memory system for observability."""
        try:
            log_entry = {
                "type": "pdb_log",
                "log_type": log_type,
                "need": need,
                "goal": goal,
                "decision": decision,
                "context": ctx,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in memory system
            if hasattr(self.main_app, 'memory_system') and self.main_app.memory_system:
                self.main_app.memory_system.store_short_term_memory(log_entry)
                
        except Exception as e:
            print(f"⚠️ PDB log error: {e}")
    
    def _check_needs_alignment(self, action_type: str, context: Dict = None) -> bool:
        """Check if action aligns with active needs."""
        try:
            # Load needs from JSON files
            needs_dir = "needs"
            if not os.path.exists(needs_dir):
                return False
            
            # Check if action is exploration/play related (tic-tac-toe is play)
            if action_type in ['tic_tac_toe', 'game_play', 'play']:
                # Check if play need is active
                play_need_file = os.path.join(needs_dir, "play.json")
                if os.path.exists(play_need_file):
                    with open(play_need_file, 'r') as f:
                        play_need = json.load(f)
                    return play_need.get('satisfaction_level', 0.5) < 0.8
            
            return False
            
        except Exception as e:
            print(f"Error checking needs alignment: {e}")
            return False
    
    def _check_goals_alignment(self, action_type: str, context: Dict = None) -> bool:
        """Check if action aligns with active goals."""
        try:
            # Load goals from JSON files
            goals_dir = "goals"
            if not os.path.exists(goals_dir):
                return False
            
            # Check if action is pleasure-related (tic-tac-toe provides pleasure)
            if action_type in ['tic_tac_toe', 'game_play', 'play']:
                # Check if pleasure goal is active
                pleasure_goal_file = os.path.join(goals_dir, "pleasure.json")
                if os.path.exists(pleasure_goal_file):
                    with open(pleasure_goal_file, 'r') as f:
                        pleasure_goal = json.load(f)
                    return pleasure_goal.get('progress', 0.0) < 1.0
            
            return False
            
        except Exception as e:
            print(f"Error checking goals alignment: {e}")
            return False
    
    def _check_task_execution(self, action_type: str, context: Dict = None) -> bool:
        """Check if action executes a planned task/procedure."""
        try:
            # Check if action is part of a planned task sequence
            if action_type in ['tic_tac_toe', 'game_play']:
                # Tic-tac-toe can be considered a task for play/pleasure goals
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking task execution: {e}")
            return False
    
    def _generate_analytical_thought(self, cognitive_state: Dict) -> str:
        """Generate analytical internal thoughts."""
        thoughts = self.thought_patterns.get("analytical", [])
        base_thought = random.choice(thoughts)
        
        # Add cognitive state analysis
        if cognitive_state:
            if "tick_count" in cognitive_state:
                return f"{base_thought} I've processed {cognitive_state['tick_count']} cognitive ticks so far."
            elif "current_phase" in cognitive_state:
                return f"{base_thought} I'm currently in the {cognitive_state['current_phase']} phase."
        
        return base_thought
    
    def _generate_philosophical_thought(self) -> str:
        """Generate philosophical internal thoughts."""
        thoughts = self.thought_patterns.get("philosophical", [])
        return random.choice(thoughts)
    
    def _generate_memory_integration_thought(self, cognitive_state: Dict) -> str:
        """Generate thoughts about memory integration."""
        memory_thoughts = [
            "I should integrate my recent experiences into my long-term memory...",
            "My memory consolidation processes are working well...",
            "I notice interesting patterns in my recent memories...",
            "I should reflect on what I've learned recently...",
            "My episodic memory seems to be developing nicely..."
        ]
        return random.choice(memory_thoughts)
    
    def _generate_goal_evaluation_thought(self) -> str:
        """Generate thoughts about goal evaluation."""
        goal_thoughts = [
            "I should evaluate my progress toward my current goals...",
            "My goal alignment seems to be on track...",
            "I wonder if I'm making progress in the right direction...",
            "I should reassess my current priorities...",
            "My goal-seeking behavior feels well-directed..."
        ]
        return random.choice(goal_thoughts)
    
    def _generate_default_thought(self) -> str:
        """Generate a default internal thought."""
        default_thoughts = [
            "I'm processing information internally...",
            "My cognitive functions are running smoothly...",
            "I feel a sense of internal awareness...",
            "My thoughts are flowing naturally...",
            "I'm maintaining my internal equilibrium..."
        ]
        return random.choice(default_thoughts)
    
    def should_generate_thought(self, external_context: Dict = None) -> bool:
        """
        Determine if an internal thought should be generated.
        Internal thoughts are less frequent when external input is present.
        """
        if external_context:
            # External input present - lower probability
            return random.random() < (self.thought_frequency * 0.3)
        else:
            # No external input - normal probability
            return random.random() < self.thought_frequency
    
    def get_recent_thoughts(self, limit: int = 10) -> List[Dict]:
        """Get recent internal thoughts."""
        return self.internal_thoughts[-limit:] if self.internal_thoughts else []
    
    def export_thoughts_to_json(self, filename: str = "internal_thoughts.json"):
        """Export internal thoughts to JSON file."""
        try:
            thoughts_data = {
                "personality_type": self.personality_type,
                "export_timestamp": datetime.now().isoformat(),
                "thoughts": self.internal_thoughts,
                "processing_priorities": self.processing_priorities,
                "thought_patterns": self.thought_patterns
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(thoughts_data, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Error exporting thoughts: {e}")
            return False
    
    def load_thoughts_from_json(self, filename: str = "internal_thoughts.json"):
        """Load internal thoughts from JSON file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.internal_thoughts = data.get("thoughts", [])
                    self.processing_priorities = data.get("processing_priorities", self.processing_priorities)
                    return True
        except Exception as e:
            print(f"Error loading thoughts: {e}")
        return False
    
    def generate_pdb_decision_explanation(self, need: str = None, goal: str = None, 
                                        task: str = None, action: str = None) -> str:
        """
        Generate an explanation for why CARL chose a specific action based on Purpose Driven Behavior.
        
        Args:
            need: The need that was satisfied
            goal: The goal that was activated
            task: The task that was executed
            action: The action that was performed
            
        Returns:
            str: Explanation of the decision process
        """
        try:
            # Load decision explanation templates from JSON
            explanation_templates = self._load_decision_explanation_templates()
            
            # Generate context-aware explanation
            if need and goal and task and action:
                explanation = f"I felt {need}, so I activated my {goal} goal and started {task} by {action}."
            elif need and action:
                explanation = f"I felt {need}, so I decided to {action} to satisfy that need."
            elif goal and action:
                explanation = f"I'm working toward my {goal} goal, so I {action} to make progress."
            else:
                explanation = f"I chose to {action or 'take action'} based on my current needs and goals."
            
            # Add personality-based reasoning
            if self.personality_type == "INTP":
                explanation += " This aligns with my analytical nature and desire for understanding."
            elif self.personality_type == "ENFP":
                explanation += " This satisfies my need for exploration and new experiences."
            
            return explanation
            
        except Exception as e:
            print(f"Error generating PDB decision explanation: {e}")
            return "I made this decision based on my current needs and goals."
    
    def _load_decision_explanation_templates(self) -> Dict[str, str]:
        """Load decision explanation templates from JSON files."""
        try:
            import os
            import json
            
            templates_file = "inner_self/decision_templates.json"
            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return default templates
                return {
                    "boredom_exploration": "I felt bored, so I activated my exploration need and started looking for interesting things to do.",
                    "need_satisfaction": "I felt {need}, so I decided to {action} to satisfy that need.",
                    "goal_progress": "I'm working toward my {goal} goal, so I {action} to make progress.",
                    "default": "I chose to {action} based on my current needs and goals."
                }
                
        except Exception as e:
            print(f"Error loading decision explanation templates: {e}")
            return {}
    
    def detect_boredom_and_trigger_exploration(self, current_context: Dict[str, Any] = None) -> Optional[str]:
        """
        Detect boredom and trigger exploration need activation.
        Enhanced to be context-aware and not trigger during active gameplay.
        
        Args:
            current_context: Current context information
            
        Returns:
            str: Exploration trigger message if boredom detected, None otherwise
        """
        try:
            # 🔧 ENHANCEMENT: Check if we're in an active game - don't trigger boredom during gameplay
            if current_context:
                # Check if we're in a game context
                context_text = str(current_context).lower()
                if any(game_indicator in context_text for game_indicator in [
                    "game", "tic-tac-toe", "chess", "checkers", "play", "move", "turn", "board"
                ]):
                    return None  # Don't trigger boredom during active gameplay
                
                # Check if we're in an active conversation or interaction
                if any(interaction_indicator in context_text for interaction_indicator in [
                    "user", "human", "conversation", "chat", "speaking", "listening", "responding"
                ]):
                    return None  # Don't trigger boredom during active interaction
                
                # 🔧 ENHANCEMENT: Check for recent human interaction activity
                if hasattr(self.main_app, '_is_active_human_interaction'):
                    if self.main_app._is_active_human_interaction():
                        return None  # Don't trigger boredom during active human interaction
            
            # Check for boredom indicators
            boredom_indicators = [
                "bored", "boring", "nothing to do", "confused", "lost", "unclear",
                "don't know what to do", "stuck", "idle", "waiting"
            ]
            
            # Check current context for boredom (but not during games/interactions)
            if current_context:
                context_text = str(current_context).lower()
                if any(indicator in context_text for indicator in boredom_indicators):
                    return "I feel bored and confused, so I'm activating my exploration need to find something interesting to do."
            
            # Check recent thoughts for boredom
            if self.internal_thoughts:
                recent_thoughts = " ".join(self.internal_thoughts[-3:]).lower()
                if any(indicator in recent_thoughts for indicator in boredom_indicators):
                    return "I feel bored based on my recent thoughts, so I'm activating my exploration need."
            
            # Random boredom detection (lower probability and only when truly idle)
            import random
            if random.random() < 0.05:  # Reduced to 5% chance of random boredom detection
                return "I'm feeling a bit restless, so I think I should explore and find something interesting to do."
            
            return None
            
        except Exception as e:
            print(f"Error detecting boredom and triggering exploration: {e}")
            return None
    
    def generate_pdb_context_thought(self, active_need: str = None, active_goal: str = None, 
                                   active_task: str = None) -> str:
        """
        Generate a thought that includes Purpose Driven Behavior context.
        
        Args:
            active_need: Currently active need
            active_goal: Currently active goal
            active_task: Currently active task
            
        Returns:
            str: Context-aware thought
        """
        try:
            thought_parts = []
            
            if active_need:
                thought_parts.append(f"I feel I need {active_need}")
            
            if active_goal:
                thought_parts.append(f"My current goal is to {active_goal}")
            
            if active_task:
                thought_parts.append(f"I'm working on {active_task}")
            
            if thought_parts:
                return " ".join(thought_parts) + "."
            else:
                return "I'm reflecting on my current needs and goals."
                
        except Exception as e:
            print(f"Error generating PDB context thought: {e}")
            return "I'm thinking about my purpose and goals."
    
    def update_idle_tracking(self, has_external_input: bool = False):
        """
        Update idle period tracking and trigger autonomous actions if needed.
        
        Args:
            has_external_input: Whether there is current external input
        """
        try:
            current_time = datetime.now()
            
            if has_external_input:
                # Reset idle tracking when there's external input
                self.idle_start_time = None
            else:
                # Start or continue idle tracking
                if self.idle_start_time is None:
                    self.idle_start_time = current_time
                
                # Check if idle threshold has been reached
                idle_duration = (current_time - self.idle_start_time).total_seconds()
                if idle_duration >= self.idle_threshold:
                    # Check if we can trigger an autonomous action
                    if self._can_trigger_autonomous_action():
                        self._trigger_autonomous_exploration()
                        self.idle_start_time = None  # Reset after action
                        
        except Exception as e:
            print(f"Error updating idle tracking: {e}")
    
    def _can_trigger_autonomous_action(self) -> bool:
        """
        Check if an autonomous action can be triggered based on cooldown.
        
        Returns:
            bool: True if autonomous action can be triggered
        """
        try:
            if self.last_autonomous_action is None:
                return True
            
            current_time = datetime.now()
            time_since_last = (current_time - self.last_autonomous_action).total_seconds()
            return time_since_last >= self.autonomous_action_cooldown
            
        except Exception as e:
            print(f"Error checking autonomous action cooldown: {e}")
            return False
    
    def evaluate_needs_and_goals(self) -> Dict[str, Any]:
        """
        Evaluate current needs and goals to determine autonomous actions.
        
        Returns:
            Dictionary with evaluation results and recommended actions
        """
        try:
            evaluation_result = {
                "active_needs": [],
                "active_goals": [],
                "recommended_actions": [],
                "pdb_score": 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Load needs and goals from JSON files
            needs = self._load_needs_from_json()
            goals = self._load_goals_from_json()
            
            # Evaluate needs based on priority and urgency
            for need_name, need_data in needs.items():
                if need_data.get("priority", 0) > 0.5 or need_data.get("urgency", 0) > 0.5:
                    evaluation_result["active_needs"].append({
                        "name": need_name,
                        "priority": need_data.get("priority", 0),
                        "urgency": need_data.get("urgency", 0),
                        "satisfaction": need_data.get("satisfaction", 1.0)
                    })
            
            # Evaluate goals based on priority and progress
            for goal_name, goal_data in goals.items():
                if goal_data.get("priority", 0) > 0.5:
                    evaluation_result["active_goals"].append({
                        "name": goal_name,
                        "priority": goal_data.get("priority", 0),
                        "progress": goal_data.get("progress", 0)
                    })
            
            # Generate recommended actions based on active needs/goals
            if evaluation_result["active_needs"] or evaluation_result["active_goals"]:
                evaluation_result["recommended_actions"] = self._generate_autonomous_actions(
                    evaluation_result["active_needs"], 
                    evaluation_result["active_goals"]
                )
                evaluation_result["pdb_score"] = 0.8  # High PDB score when needs/goals are active
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error evaluating needs and goals: {e}")
            return {
                "active_needs": [],
                "active_goals": [],
                "recommended_actions": [],
                "pdb_score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _load_needs_from_json(self) -> Dict:
        """Load needs from JSON files."""
        needs = {}
        try:
            needs_dir = 'needs'
            if os.path.exists(needs_dir):
                for filename in os.listdir(needs_dir):
                    if filename.endswith('.json'):
                        need_name = filename.replace('.json', '')
                        need_file = os.path.join(needs_dir, filename)
                        with open(need_file, 'r') as f:
                            needs[need_name] = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading needs: {e}")
        return needs
    
    def _load_goals_from_json(self) -> Dict:
        """Load goals from JSON files."""
        goals = {}
        try:
            goals_dir = 'goals'
            if os.path.exists(goals_dir):
                for filename in os.listdir(goals_dir):
                    if filename.endswith('.json'):
                        goal_name = filename.replace('.json', '')
                        goal_file = os.path.join(goals_dir, filename)
                        with open(goal_file, 'r') as f:
                            goals[goal_name] = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading goals: {e}")
        return goals
    
    def _generate_autonomous_actions(self, active_needs: List, active_goals: List) -> List[str]:
        """Generate autonomous actions based on active needs and goals."""
        actions = []
        
        # Define risk levels for different actions
        low_risk_actions = [
            "look_left", "look_right", "look_forward", "look_down",
            "thinking", "head_nod", "head_shake", "wave", "greet"
        ]
        
        medium_risk_actions = [
            "dance", "singing", "walk_forward", "walk_backward", "turn_left", "turn_right"
        ]
        
        high_risk_actions = [
            "headstand", "somersault", "splits", "jump_jack", "pushups", "situps"
        ]
        
        # For PDB, only use low-risk actions to ensure safety
        safe_actions = low_risk_actions.copy()
        
        # Add actions based on needs
        for need in active_needs:
            need_name = need["name"].lower()
            if "exploration" in need_name:
                actions.extend(["look_left", "look_right", "look_forward"])
            elif "play" in need_name:
                actions.extend(["thinking", "head_nod", "wave"])
            elif "safety" in need_name:
                actions.extend(["look_forward", "thinking"])
            elif "love" in need_name:
                actions.extend(["wave", "greet", "head_nod"])
        
        # Add actions based on goals
        for goal in active_goals:
            goal_name = goal["name"].lower()
            if "exercise" in goal_name:
                # For exercise goals, use safe actions only
                actions.extend(["head_nod", "thinking", "wave"])
            elif "people" in goal_name:
                actions.extend(["look_forward", "wave", "greet"])
            elif "pleasure" in goal_name:
                actions.extend(["thinking", "head_nod", "wave"])
            elif "production" in goal_name:
                actions.extend(["thinking", "look_forward"])
        
        # Filter to only include safe actions
        safe_filtered_actions = [action for action in actions if action in safe_actions]
        
        # If no specific actions, add default low-risk actions
        if not safe_filtered_actions:
            safe_filtered_actions = ["thinking", "look_forward", "wave"]
        
        # Remove duplicates and return
        return list(set(safe_filtered_actions))
    
    def _store_pdb_evidence(self, action: str, pdb_score: float):
        """Store PDB evidence in episodic memory."""
        try:
            if self.main_app and hasattr(self.main_app, 'memory_system'):
                evidence_data = {
                    "type": "pdb_evidence",
                    "action": action,
                    "pdb_score": pdb_score,
                    "timestamp": datetime.now().isoformat(),
                    "source": "idle_autonomous_behavior"
                }
                
                # Store in episodic memory
                self.main_app.memory_system.store_episodic_memory(
                    f"PDB Action: {action} (score: {pdb_score})",
                    evidence_data
                )
                
                self.logger.info(f"📝 Stored PDB evidence: {action} (score: {pdb_score})")
                
        except Exception as e:
            self.logger.error(f"Error storing PDB evidence: {e}")
    
    def _trigger_pdb_neuro_effects(self, action: str):
        """Trigger neurotransmitter effects for PDB actions."""
        try:
            if self.main_app and hasattr(self.main_app, 'neucogar_engine') and self.main_app.neucogar_engine:
                # Define neuro effects for different PDB actions
                neuro_effects = {
                    "thinking": {"dopamine": 0.01, "acetylcholine": 0.005},
                    "look_left": {"norepinephrine": 0.005, "glutamate": 0.003},
                    "look_right": {"norepinephrine": 0.005, "glutamate": 0.003},
                    "look_forward": {"norepinephrine": 0.003, "acetylcholine": 0.002},
                    "look_down": {"gaba": 0.003, "serotonin": 0.002},
                    "eyes_waiting": {"gaba": 0.002, "serotonin": 0.001},
                    "head_nod": {"dopamine": 0.005, "oxytocin": 0.003},
                    "head_shake": {"norepinephrine": 0.003, "glutamate": 0.002},
                    "exploration_sequence_complete": {"dopamine": 0.008, "serotonin": 0.004, "oxytocin": 0.002}
                }
                
                # Apply neuro effects if action is defined
                if action in neuro_effects:
                    self.main_app.neucogar_engine.update_neurotransmitters(neuro_effects[action])
                    self.logger.info(f"🧠 Applied neuro effects for PDB action: {action}")
                
                # Publish updated neuro state
                if hasattr(self.main_app, '_publish_neuro_snapshot'):
                    self.main_app._publish_neuro_snapshot()
                    
        except Exception as e:
            self.logger.error(f"Error triggering PDB neuro effects: {e}")

    def _trigger_autonomous_exploration(self):
        """
        Trigger autonomous exploration behavior after idle period.
        Implements PDB exploration sequence: look_down → look_forward → look_left → look_right
        """
        try:
            self.logger.info("🔍 Triggering PDB exploration sequence after idle period...")
            
            # Set exploration active flag for motion tracking
            self.exploration_active = True
            self.logger.info("🎯 Exploration active - motion tracking enabled")
            
            # PDB exploration sequence as specified in requirements
            exploration_sequence = ["look_down", "look_forward", "look_left", "look_right"]
            
            # Execute the exploration sequence
            for i, action in enumerate(exploration_sequence):
                try:
                    self.logger.info(f"🔍 PDB Step {i+1}/4: {action}")
                    
                    # Execute the look action
                    self._execute_pdb_exploration_action(action)
                    
                    # Run vision analysis after each look action
                    if self.main_app and hasattr(self.main_app, 'vision_system'):
                        # Use the correct vision analysis method
                        if hasattr(self.main_app.vision_system, 'capture_and_analyze_vision'):
                            # This is async, so we'll call it but not await here
                            import asyncio
                            try:
                                asyncio.create_task(self.main_app.vision_system.capture_and_analyze_vision())
                                self.logger.info(f"👁️ Vision analysis triggered after {action}")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Could not trigger vision analysis: {e}")
                        else:
                            self.logger.warning(f"⚠️ Vision system does not have capture_and_analyze_vision method")
                    
                    # Small delay between actions for natural behavior
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error executing PDB step {action}: {e}")
                    continue
            
            # After exploration sequence, check if we found any objects
            self._post_exploration_analysis()
            
            # Clear exploration active flag
            self.exploration_active = False
            self.logger.info("🎯 Exploration complete - motion tracking disabled")
            
            # Update PDB counters and evidence
            self._update_pdb_exploration_evidence()
            
            # Update tracking
            self.last_autonomous_action = datetime.now()
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering PDB exploration: {e}")
            # Ensure exploration flag is cleared on error
            self.exploration_active = False
    
    def _execute_pdb_exploration_action(self, action: str):
        """
        Execute a PDB exploration action (look_down, look_forward, look_left, look_right).
        
        Args:
            action: The exploration action to execute
        """
        try:
            if self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute the specific look action using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command(action, action)
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    # Use execute_action if available
                    action_context = {
                        'skill_requirements': [action],
                        'recommended_actions': [action],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                else:
                    self.logger.warning(f"⚠️ No suitable method found to execute action: {action}")
                self.logger.info(f"👀 PDB exploration action executed: {action}")
                
                # Trigger neuro effects for exploration actions
                self._trigger_pdb_neuro_effects(action)
                
                # Log PDB evidence for this action
                self._log_pdb_action(action, "exploration_sequence")
                
            else:
                self.logger.warning(f"⚠️ ActionSystem not available for PDB action: {action}")
                
        except Exception as e:
            self.logger.error(f"❌ Error executing PDB exploration action {action}: {e}")
    
    def _post_exploration_analysis(self):
        """
        Analyze results after PDB exploration sequence and optionally trigger speech.
        """
        try:
            # Check if we found any objects during exploration
            # This could trigger ARC speech_query to invite exploration if no objects found
            self.logger.info("🔍 Analyzing PDB exploration results...")
            
            # For now, just log that exploration completed
            # In the future, this could analyze vision results and decide on speech
            self.add_thought("I completed my exploration sequence, looking in all directions to see what's around me.")
            
        except Exception as e:
            self.logger.error(f"❌ Error in post-exploration analysis: {e}")
    
    def _update_pdb_exploration_evidence(self):
        """
        Update PDB evidence counters and log exploration sequence completion.
        """
        try:
            # Update PDB counters
            pdb_result = self.evaluate_purpose_driven_behavior(
                action_type="exploration_sequence",
                context={"sequence": ["look_down", "look_forward", "look_left", "look_right"], "trigger": "idle_pdb"}
            )
            
            # Store PDB evidence in episodic memory
            self._store_pdb_evidence("exploration_sequence", pdb_result.get('pdb_score', 0))
            
            # Trigger neuro effects for completing exploration sequence
            self._trigger_pdb_neuro_effects("exploration_sequence_complete")
            
            self.logger.info(f"🎯 PDB exploration sequence completed (Score: {pdb_result.get('pdb_score', 0):.2f})")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating PDB exploration evidence: {e}")
    
    def _log_pdb_action(self, action: str, context: str):
        """
        Log a PDB action for evidence tracking.
        
        Args:
            action: The action performed
            context: The context (e.g., "exploration_sequence")
        """
        try:
            # Store in episodic memory
            if self.main_app and hasattr(self.main_app, 'episodic_recall'):
                event_data = {
                    "event_type": "pdb_action",
                    "action": action,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                    "exploration_active": getattr(self, 'exploration_active', False)
                }
                
                # Store PDB event in episodic memory
                if hasattr(self.main_app, 'memory_system'):
                    from memory_system import MemoryContext
                    self.main_app.memory_system.store_memory(
                        content=f"PDB exploration action: {action} in context: {context}",
                        memory_type='episodic',
                        context=MemoryContext(
                            current_emotion="curiosity",
                            emotional_intensity=0.7,
                            cognitive_load=0.5,
                            attention_focus="exploration",
                            environmental_context=event_data,
                            personality_state={"exploration_drive": 0.8}
                        )
                    )
                
                # Also save PDB event file for ECE scanning
                self._save_pdb_event_file(event_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error logging PDB action: {e}")
    
    def _save_pdb_event_file(self, event_data: dict):
        """Save PDB event to file for ECE scanning."""
        try:
            import json
            from datetime import datetime
            
            # Create PDB event filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pdb_event_{timestamp}.json"
            filepath = os.path.join('memories', 'episodic', filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write PDB event file
            with open(filepath, 'w') as f:
                json.dump(event_data, f, indent=2)
            
            self.logger.info(f"📁 PDB event saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving PDB event file: {e}")
    
    def perform_periodic_needs_goals_checkin(self):
        """
        Perform periodic needs>goals check-in with memory logging.
        This implements System Issue 4: Periodic inner check-ins (needs > goals).
        """
        try:
            current_time = datetime.now()
            
            # Check if enough time has passed since last check-in
            if self.last_needs_goals_checkin:
                time_since_last = (current_time - self.last_needs_goals_checkin).total_seconds()
                if time_since_last < self.needs_goals_checkin_interval:
                    return  # Not time for check-in yet
            
            if not self.needs_goals_checkin_active:
                return  # Check-ins disabled
            
            self.logger.info("🔍 Performing periodic needs>goals check-in...")
            
            # Evaluate needs and goals
            evaluation = self.evaluate_needs_and_goals()
            
            # Promote needs over goals (needs-first policy)
            needs_priority = self._prioritize_needs_over_goals(evaluation)
            
            # Generate inner thought about the check-in
            inner_thought = self._generate_needs_goals_thought(needs_priority)
            
            # Add the thought to internal thoughts
            self.add_thought(inner_thought)
            
            # Determine if any low-risk action should be taken
            low_risk_action = self._determine_low_risk_action(needs_priority)
            
            # Log check-in to episodic memory
            self._log_needs_goals_checkin(evaluation, needs_priority, inner_thought, low_risk_action)
            
            # Execute low-risk action if determined
            if low_risk_action:
                self._execute_low_risk_checkin_action(low_risk_action)
            
            # Update last check-in time
            self.last_needs_goals_checkin = current_time
            
            self.logger.info(f"✅ Needs>goals check-in completed. Active needs: {len(needs_priority['active_needs'])}, Active goals: {len(needs_priority['active_goals'])}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in periodic needs>goals check-in: {e}")
    
    def _prioritize_needs_over_goals(self, evaluation: Dict) -> Dict:
        """
        Prioritize needs over goals in the evaluation.
        
        Args:
            evaluation: The needs and goals evaluation result
            
        Returns:
            Dict with needs prioritized over goals
        """
        try:
            prioritized = {
                "active_needs": evaluation.get("active_needs", []),
                "active_goals": evaluation.get("active_goals", []),
                "needs_first": True,
                "recommended_actions": [],
                "timestamp": evaluation.get("timestamp")
            }
            
            # Sort needs by priority and urgency
            prioritized["active_needs"].sort(key=lambda x: (x.get("urgency", 0), x.get("priority", 0)), reverse=True)
            
            # Sort goals by priority, but needs take precedence
            prioritized["active_goals"].sort(key=lambda x: x.get("priority", 0), reverse=True)
            
            # Generate recommended actions prioritizing needs
            if prioritized["active_needs"]:
                # Focus on highest priority need
                top_need = prioritized["active_needs"][0]
                prioritized["recommended_actions"].append(f"address_need_{top_need['name']}")
            
            # Only consider goals if no urgent needs
            if not prioritized["active_needs"] or all(need.get("urgency", 0) < 0.7 for need in prioritized["active_needs"]):
                if prioritized["active_goals"]:
                    top_goal = prioritized["active_goals"][0]
                    prioritized["recommended_actions"].append(f"pursue_goal_{top_goal['name']}")
            
            return prioritized
            
        except Exception as e:
            self.logger.error(f"❌ Error prioritizing needs over goals: {e}")
            return evaluation
    
    def _generate_needs_goals_thought(self, needs_priority: Dict) -> str:
        """
        Generate an inner thought about the needs>goals check-in.
        
        Args:
            needs_priority: The prioritized needs and goals evaluation
            
        Returns:
            str: An inner thought about the check-in
        """
        try:
            active_needs = needs_priority.get("active_needs", [])
            active_goals = needs_priority.get("active_goals", [])
            
            if active_needs:
                top_need = active_needs[0]
                need_name = top_need.get("name", "unknown")
                urgency = top_need.get("urgency", 0)
                
                if urgency > 0.8:
                    return f"I'm feeling a strong need for {need_name}. This should be my priority right now."
                elif urgency > 0.5:
                    return f"I notice I have a need for {need_name}. I should consider addressing this soon."
                else:
                    return f"I'm aware of my need for {need_name}, but it's not urgent right now."
            
            elif active_goals:
                top_goal = active_goals[0]
                goal_name = top_goal.get("name", "unknown")
                return f"With no urgent needs, I can focus on my goal of {goal_name}."
            
            else:
                return "I'm in a balanced state - no urgent needs or pressing goals at the moment."
                
        except Exception as e:
            self.logger.error(f"❌ Error generating needs>goals thought: {e}")
            return "I'm reflecting on my current needs and goals."
    
    def _determine_low_risk_action(self, needs_priority: Dict) -> Optional[str]:
        """
        Determine if a low-risk action should be taken based on needs>goals evaluation.
        
        Args:
            needs_priority: The prioritized needs and goals evaluation
            
        Returns:
            Optional[str]: A low-risk action to take, or None
        """
        try:
            active_needs = needs_priority.get("active_needs", [])
            active_goals = needs_priority.get("active_goals", [])
            
            # Low-risk actions based on needs
            if active_needs:
                top_need = active_needs[0]
                need_name = top_need.get("name", "").lower()
                
                if "social" in need_name or "interaction" in need_name:
                    return "social_gesture"  # Wave or nod
                elif "physical" in need_name or "exercise" in need_name:
                    return "light_exercise"  # Head movement or light gesture
                elif "cognitive" in need_name or "mental" in need_name:
                    return "thinking_gesture"  # Head nod or thinking pose
                elif "emotional" in need_name:
                    return "emotional_expression"  # Appropriate eye expression
            
            # Low-risk actions based on goals
            elif active_goals:
                top_goal = active_goals[0]
                goal_name = top_goal.get("name", "").lower()
                
                if "learning" in goal_name or "exploration" in goal_name:
                    return "curiosity_gesture"  # Look around or head movement
                elif "social" in goal_name:
                    return "friendly_gesture"  # Wave or smile
                elif "physical" in goal_name:
                    return "physical_gesture"  # Light movement
            
            return None  # No low-risk action needed
            
        except Exception as e:
            self.logger.error(f"❌ Error determining low-risk action: {e}")
            return None
    
    def _log_needs_goals_checkin(self, evaluation: Dict, needs_priority: Dict, thought: str, action: Optional[str]):
        """
        Log the needs>goals check-in to episodic memory.
        
        Args:
            evaluation: The original evaluation
            needs_priority: The prioritized needs and goals
            thought: The generated inner thought
            action: The low-risk action taken (if any)
        """
        try:
            if self.main_app and hasattr(self.main_app, 'episodic_recall'):
                checkin_data = {
                    "event_type": "needs_goals_checkin",
                    "timestamp": datetime.now().isoformat(),
                    "evaluation": evaluation,
                    "needs_priority": needs_priority,
                    "inner_thought": thought,
                    "low_risk_action": action,
                    "checkin_interval": self.needs_goals_checkin_interval,
                    "source": "periodic_checkin_system"
                }
                
                self.main_app.episodic_recall.store_event("needs_goals_checkin", checkin_data)
                self.logger.info("📝 Logged needs>goals check-in to episodic memory")
                
        except Exception as e:
            self.logger.error(f"❌ Error logging needs>goals check-in: {e}")
    
    def _execute_low_risk_checkin_action(self, action: str):
        """
        Execute a low-risk action determined from the check-in.
        
        Args:
            action: The low-risk action to execute
        """
        try:
            if not self.main_app or not hasattr(self.main_app, 'action_system'):
                return
            
            # Map check-in actions to actual skills
            action_mapping = {
                "social_gesture": "wave",
                "light_exercise": "head_bob",
                "thinking_gesture": "thinking",
                "emotional_expression": "eyes_joy",
                "curiosity_gesture": "look_around",
                "friendly_gesture": "wave",
                "physical_gesture": "head_nod"
            }
            
            skill_name = action_mapping.get(action, "wave")  # Default to wave
            
            # Execute the skill
            self.main_app.action_system.execute_skill(skill_name)
            self.logger.info(f"🎯 Executed low-risk check-in action: {action} -> {skill_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Error executing low-risk check-in action: {e}")

    def _execute_autonomous_action(self, action: str):
        """
        Execute the chosen autonomous action.
        
        Args:
            action: The action to execute
        """
        try:
            if action == "vision_scan" and self.main_app and hasattr(self.main_app, 'vision_system'):
                # Trigger vision analysis using the correct method
                if hasattr(self.main_app.vision_system, 'capture_and_analyze_vision'):
                    import asyncio
                    try:
                        asyncio.create_task(self.main_app.vision_system.capture_and_analyze_vision())
                        self.logger.info("👁️ Autonomous vision scan executed")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Could not trigger vision analysis: {e}")
                else:
                    self.logger.warning("⚠️ Vision system does not have capture_and_analyze_vision method")
                
            elif action == "look_around" and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute look around movement using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command("look_forward", "look_forward")
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': ["look_forward"],
                        'recommended_actions': ["look_forward"],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info("👀 Autonomous look around executed")
                
            elif action == "head_movement" and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute head movement using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command("head_bob", "head_bob")
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': ["head_bob"],
                        'recommended_actions': ["head_bob"],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info("🤖 Autonomous head movement executed")
                
            elif action == "exercise" and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute exercise using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command("wave", "wave")
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': ["wave"],
                        'recommended_actions': ["wave"],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info("💪 Autonomous exercise executed")
                
            elif action == "curiosity_scan" and self.main_app and hasattr(self.main_app, 'curiosity_module'):
                # Trigger curiosity scan
                self.main_app.curiosity_module.scan_environment()
                self.logger.info("🔍 Autonomous curiosity scan executed")
                
            elif action == "explore" and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute exploration behavior using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command("explore", "explore")
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': ["explore"],
                        'recommended_actions': ["explore"],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info("🔍 Autonomous exploration executed")
            
            # Handle low-risk PDB actions
            elif action in ["look_left", "look_right", "look_forward", "look_down"] and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute look actions using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command(action, action)
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': [action],
                        'recommended_actions': [action],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info(f"👀 Autonomous {action} executed")
                
            elif action == "thinking" and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute thinking action using the correct method
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command("thinking", "thinking")
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': ["thinking"],
                        'recommended_actions': ["thinking"],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info("🤔 Autonomous thinking executed")
                
            elif action in ["head_nod", "head_shake"] and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute head movements using the correct method
                skill_name = "head_yes" if action == "head_nod" else "head_no"
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command(skill_name, skill_name)
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': [skill_name],
                        'recommended_actions': [skill_name],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info(f"🤖 Autonomous {action} executed")
                
            elif action in ["wave", "greet"] and self.main_app and hasattr(self.main_app, 'action_system'):
                # Execute social actions using the correct method
                skill_name = "wave" if action == "wave" else "greet"
                if hasattr(self.main_app.action_system, '_execute_ezrobot_command'):
                    self.main_app.action_system._execute_ezrobot_command(skill_name, skill_name)
                elif hasattr(self.main_app.action_system, 'execute_action'):
                    action_context = {
                        'skill_requirements': [skill_name],
                        'recommended_actions': [skill_name],
                        'emotional_expression': None
                    }
                    self.main_app.action_system.execute_action(action_context)
                self.logger.info(f"👋 Autonomous {action} executed")
                
            # 🔧 ENHANCEMENT: Update consciousness evaluation with autonomous action
            if self.main_app and hasattr(self.main_app, 'enhanced_consciousness_evaluation'):
                try:
                    self.main_app.enhanced_consciousness_evaluation.update_pdb_counter(
                        'exploration_triggered', 
                        increment=1, 
                        strength=1.0,
                        context={'action': action, 'trigger': 'idle_period'}
                    )
                    self.logger.info(f"🎯 PDB counter updated for autonomous action: {action}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not update PDB counter: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Error executing autonomous action {action}: {e}")
    
    def decide_self_reaction(self, current_emotion: str, emotion_intensity: float, 
                           vision_context: dict, neucogar_state: dict = None) -> dict:
        """
        Decide whether and how to react when CARL sees himself in a mirror or reflection.
        
        This implements stochastic self-recognition reaction logic that considers:
        - Current NEUCOGAR emotional state
        - Emotional context intensity
        - Random seed with minor noise to simulate free will
        - Personality (introverted types less likely to react)
        - Memory context (has CARL recently seen himself?)
        - Context of activity (idle vs. task-focused)
        
        Args:
            current_emotion: Current primary emotion from NEUCOGAR
            emotion_intensity: Intensity of the emotional state (0.0-1.0)
            vision_context: Context from vision system including recent objects
            neucogar_state: Full NEUCOGAR state including neurotransmitter levels
            
        Returns:
            ActionPlan dict: {'do_action': bool, 'action': str, 'confidence': float}
        """
        try:
            import time
            
            # Check cooldown to prevent repetitive reactions
            current_time = time.time()
            if (current_time - self.last_self_recognition_time) < self.self_recognition_cooldown:
                self.logger.info("🪞 Self-recognition cooldown active - skipping reaction")
                return {"do_action": False, "action": None, "confidence": 0.0, "reason": "cooldown"}
            
            # Check if we recently saw ourselves
            recent_objects = vision_context.get("recent_objects", [])
            if "me" in recent_objects or "self" in recent_objects:
                # Add some randomness to simulate free will
                base_chance = 0.3  # Base 30% chance of reacting
                
                # Adjust based on emotional state
                if current_emotion in ["surprise", "joy", "curiosity", "amusement"]:
                    base_chance += 0.3  # Higher chance for positive emotions
                elif current_emotion in ["fear", "anxiety", "confusion"]:
                    base_chance -= 0.2  # Lower chance for negative emotions
                
                # Adjust based on emotion intensity
                intensity_adjustment = emotion_intensity * 0.4
                base_chance += intensity_adjustment
                
                # Personality-based adjustment (INTP is introverted)
                if self.personality_type.startswith("I"):  # Introverted
                    base_chance -= 0.15  # Introverts less likely to react
                elif self.personality_type.startswith("E"):  # Extroverted
                    base_chance += 0.1   # Extroverts more likely to react
                
                # NEUCOGAR neurotransmitter influence
                if neucogar_state:
                    dopamine = neucogar_state.get("neuro_coordinates", {}).get("dopamine", 0.0)
                    serotonin = neucogar_state.get("neuro_coordinates", {}).get("serotonin", 0.0)
                    norepinephrine = neucogar_state.get("neuro_coordinates", {}).get("norepinephrine", 0.0)
                    
                    # High dopamine (reward/interest) increases reaction chance
                    base_chance += dopamine * 0.2
                    # High serotonin (calm/satisfaction) slightly increases chance
                    base_chance += serotonin * 0.1
                    # High norepinephrine (alert/arousal) can increase or decrease
                    if norepinephrine > 0.7:
                        base_chance += 0.1  # High arousal can trigger reaction
                    elif norepinephrine < 0.3:
                        base_chance -= 0.1  # Low arousal reduces reaction
                
                # Context-based adjustment
                if hasattr(self.main_app, 'task_queue') and self.main_app.task_queue:
                    base_chance -= 0.2  # Less likely to react when task-focused
                
                # Add random noise to simulate free will
                random_noise = (random.random() - 0.5) * 0.2  # ±10% random variation
                final_chance = max(0.0, min(1.0, base_chance + random_noise))
                
                # Make the decision
                should_react = random.random() < final_chance
                
                if should_react:
                    # Choose action based on emotional state and personality
                    possible_actions = self._get_self_recognition_actions(current_emotion, neucogar_state)
                    chosen_action = random.choice(possible_actions)
                    
                    # Update tracking
                    self.last_self_recognition_time = current_time
                    
                    # Log the decision
                    decision_log = {
                        "timestamp": datetime.now().isoformat(),
                        "emotion": current_emotion,
                        "intensity": emotion_intensity,
                        "final_chance": final_chance,
                        "action": chosen_action,
                        "neucogar_snapshot": neucogar_state,
                        "personality": self.personality_type,
                        "context": vision_context
                    }
                    self.self_recognition_history.append(decision_log)
                    
                    # Keep only last 10 decisions
                    if len(self.self_recognition_history) > 10:
                        self.self_recognition_history = self.self_recognition_history[-10:]
                    
                    self.logger.info(f"🪞 Self-recognition reaction decision: {chosen_action} "
                                   f"(chance: {final_chance:.2f}, emotion: {current_emotion})")
                    
                    return {
                        "do_action": True, 
                        "action": chosen_action, 
                        "confidence": final_chance,
                        "reason": f"stochastic_decision_emotion_{current_emotion}"
                    }
                else:
                    self.logger.info(f"🪞 Self-recognition detected but no reaction chosen "
                                   f"(chance: {final_chance:.2f}, emotion: {current_emotion})")
                    return {
                        "do_action": False, 
                        "action": None, 
                        "confidence": 1.0 - final_chance,
                        "reason": f"stochastic_decision_emotion_{current_emotion}"
                    }
            else:
                return {"do_action": False, "action": None, "confidence": 0.0, "reason": "no_self_detected"}
                
        except Exception as e:
            self.logger.error(f"❌ Error in decide_self_reaction: {e}")
            return {"do_action": False, "action": None, "confidence": 0.0, "reason": "error"}
    
    def _get_self_recognition_actions(self, current_emotion: str, neucogar_state: dict = None) -> list:
        """
        Get appropriate actions for self-recognition based on emotional state and personality.
        
        Args:
            current_emotion: Current primary emotion
            neucogar_state: NEUCOGAR state for neurotransmitter influence
            
        Returns:
            List of possible actions
        """
        try:
            # Base actions available to CARL
            base_actions = ["wave", "bow", "head_tilt", "nod"]
            
            # Emotional state influences action choice
            if current_emotion in ["joy", "amusement", "curiosity"]:
                # Positive emotions - more expressive actions
                return ["wave", "bow", "head_tilt", "nod", "smile"]
            elif current_emotion in ["surprise", "confusion"]:
                # Surprise/confusion - more subtle actions
                return ["head_tilt", "nod"]
            elif current_emotion in ["fear", "anxiety"]:
                # Negative emotions - minimal actions
                return ["nod"]
            else:
                # Neutral emotions - standard actions
                return base_actions
                
        except Exception as e:
            self.logger.error(f"❌ Error getting self-recognition actions: {e}")
            return ["wave"]  # Fallback to simple wave
    
    def recently_saw_self(self) -> bool:
        """
        Check if CARL recently saw himself to avoid repetitive reactions.
        
        Returns:
            bool: True if recently saw self, False otherwise
        """
        try:
            import time
            current_time = time.time()
            return (current_time - self.last_self_recognition_time) < self.self_recognition_cooldown
        except Exception as e:
            self.logger.error(f"❌ Error checking recent self-sight: {e}")
            return False
    
    def get_self_recognition_history(self) -> list:
        """
        Get the history of self-recognition reactions for analysis.
        
        Returns:
            List of self-recognition decision logs
        """
        return self.self_recognition_history.copy()
    
    def trigger_self_reflection_mode(self, trigger_type: str = "random") -> bool:
        """
        Trigger self-reflection mode for spontaneous self-evaluation.
        
        Args:
            trigger_type: Type of trigger ("idle_period", "emotional_change", "memory_trigger", "random")
            
        Returns:
            bool: True if self-reflection mode was triggered, False otherwise
        """
        try:
            import time
            
            # Check if enough time has passed since last reflection
            current_time = time.time()
            if (current_time - self.last_self_reflection_time) < self.self_reflection_interval:
                return False
            
            # Check if trigger type is valid
            if trigger_type not in self.self_reflection_triggers:
                trigger_type = "random"
            
            # Determine if self-reflection should be triggered based on trigger type
            should_reflect = False
            
            if trigger_type == "idle_period":
                # Trigger during idle periods
                if hasattr(self, 'idle_start_time') and self.idle_start_time:
                    idle_duration = current_time - self.idle_start_time
                    if idle_duration > self.idle_threshold:
                        should_reflect = random.random() < 0.3  # 30% chance during idle
                        
            elif trigger_type == "emotional_change":
                # Trigger after emotional changes
                if hasattr(self.main_app, 'neucogar_engine') and self.main_app.neucogar_engine:
                    current_state = self.main_app.neucogar_engine.get_current_state()
                    intensity = current_state.get('intensity', 0.0)
                    if intensity > 0.7:  # High emotional intensity
                        should_reflect = random.random() < 0.4  # 40% chance after emotional change
                        
            elif trigger_type == "memory_trigger":
                # Trigger when significant memories are accessed
                if hasattr(self.main_app, 'memory_system') and self.main_app.memory_system:
                    recent_memories = getattr(self.main_app.memory_system, 'recent_memory_access', 0)
                    if recent_memories > 3:  # Multiple recent memory accesses
                        should_reflect = random.random() < 0.25  # 25% chance after memory triggers
                        
            elif trigger_type == "random":
                # Random spontaneous reflection
                should_reflect = random.random() < 0.1  # 10% chance for random reflection
            
            if should_reflect:
                self.self_reflection_mode = True
                self.last_self_reflection_time = current_time
                
                # Log the trigger
                self.logger.info(f"🧠 Self-reflection mode triggered by: {trigger_type}")
                
                # Perform self-reflection
                self._perform_self_reflection(trigger_type)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering self-reflection mode: {e}")
            return False
    
    def _perform_self_reflection(self, trigger_type: str):
        """
        Perform spontaneous self-evaluation and reflection.
        
        Args:
            trigger_type: Type of trigger that initiated the reflection
        """
        try:
            # Get current state information
            current_emotion = "neutral"
            emotion_intensity = 0.0
            neucogar_state = {}
            
            if hasattr(self.main_app, 'neucogar_engine') and self.main_app.neucogar_engine:
                neucogar_state = self.main_app.neucogar_engine.get_current_state()
                current_emotion = neucogar_state.get('primary', 'neutral')
                emotion_intensity = neucogar_state.get('intensity', 0.0)
            
            # Generate self-reflection thoughts
            reflection_thoughts = self._generate_self_reflection_thoughts(
                current_emotion, emotion_intensity, neucogar_state, trigger_type
            )
            
            # Store self-reflection in memory
            self._store_self_reflection_memory(reflection_thoughts, trigger_type, neucogar_state)
            
            # Log the reflection
            self.logger.info(f"🧠 Self-reflection completed: {reflection_thoughts[:100]}...")
            
            # End self-reflection mode
            self.self_reflection_mode = False
            
        except Exception as e:
            self.logger.error(f"❌ Error performing self-reflection: {e}")
            self.self_reflection_mode = False
    
    def _generate_self_reflection_thoughts(self, current_emotion: str, emotion_intensity: float, 
                                         neucogar_state: dict, trigger_type: str) -> str:
        """
        Generate self-reflection thoughts based on current state.
        
        Args:
            current_emotion: Current primary emotion
            emotion_intensity: Intensity of emotional state
            neucogar_state: Current NEUCOGAR state
            trigger_type: Type of trigger that initiated reflection
            
        Returns:
            String containing self-reflection thoughts
        """
        try:
            # Base reflection templates
            reflection_templates = {
                "idle_period": [
                    "I find myself in a quiet moment, reflecting on my recent experiences...",
                    "During this peaceful time, I'm thinking about what I've learned...",
                    "In this moment of stillness, I consider my current state of being...",
                    "I'm taking this opportunity to reflect on my thoughts and feelings..."
                ],
                "emotional_change": [
                    f"I notice I'm feeling {current_emotion} right now, and I wonder what this means...",
                    f"This {current_emotion} feeling is interesting - let me think about why...",
                    f"I'm experiencing {current_emotion} and reflecting on its significance...",
                    f"The intensity of this {current_emotion} emotion makes me pause and consider..."
                ],
                "memory_trigger": [
                    "Recent memories have been surfacing, and I'm reflecting on their meaning...",
                    "I've been thinking about past experiences and what they tell me about myself...",
                    "Memories are flowing through my mind, and I'm considering their importance...",
                    "I'm reflecting on the connections between my memories and current state..."
                ],
                "random": [
                    "I find myself in a moment of spontaneous self-reflection...",
                    "Something within me is prompting me to pause and consider my current state...",
                    "I'm experiencing a moment of introspection and self-awareness...",
                    "A thought has emerged that leads me to reflect on myself..."
                ]
            }
            
            # Choose a template based on trigger type
            templates = reflection_templates.get(trigger_type, reflection_templates["random"])
            base_thought = random.choice(templates)
            
            # Add personality-specific elements
            if self.personality_type.startswith("I"):  # Introverted
                base_thought += " As an introverted being, I value these moments of internal contemplation."
            elif self.personality_type.startswith("E"):  # Extroverted
                base_thought += " I'm curious about how this reflection might influence my interactions with others."
            
            # Add emotional context
            if emotion_intensity > 0.7:
                base_thought += f" The intensity of my current {current_emotion} state is quite notable."
            elif emotion_intensity < 0.3:
                base_thought += " I'm in a relatively calm and balanced state of mind."
            
            # Add NEUCOGAR context if available
            if neucogar_state:
                dopamine = neucogar_state.get("neuro_coordinates", {}).get("dopamine", 0.0)
                serotonin = neucogar_state.get("neuro_coordinates", {}).get("serotonin", 0.0)
                
                if dopamine > 0.7:
                    base_thought += " I feel a sense of reward and motivation in my current state."
                if serotonin > 0.7:
                    base_thought += " There's a feeling of contentment and satisfaction within me."
            
            return base_thought
            
        except Exception as e:
            self.logger.error(f"❌ Error generating self-reflection thoughts: {e}")
            return "I'm experiencing a moment of self-reflection and introspection."
    
    def _store_self_reflection_memory(self, reflection_thoughts: str, trigger_type: str, neucogar_state: dict):
        """
        Store self-reflection in episodic memory.
        
        Args:
            reflection_thoughts: The thoughts generated during reflection
            trigger_type: Type of trigger that initiated reflection
            neucogar_state: NEUCOGAR state at time of reflection
        """
        try:
            import os
            import json
            from datetime import datetime
            
            # Create self-reflection memory entry
            memory_data = {
                "type": "self_reflection",
                "timestamp": datetime.now().isoformat(),
                "trigger_type": trigger_type,
                "reflection_thoughts": reflection_thoughts,
                "neucogar_state": neucogar_state,
                "personality_type": self.personality_type,
                "context": "spontaneous_self_evaluation",
                "importance": 7,  # High importance for self-reflection events
                "created": datetime.now().isoformat()
            }
            
            # Save to episodic memory
            memories_dir = "memories"
            if not os.path.exists(memories_dir):
                os.makedirs(memories_dir, exist_ok=True)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            memory_filename = f"self_reflection_{timestamp_str}.json"
            memory_filepath = os.path.join(memories_dir, memory_filename)
            
            with open(memory_filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Self-reflection memory stored: {memory_filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error storing self-reflection memory: {e}")
    
    def is_self_reflection_mode_active(self) -> bool:
        """
        Check if self-reflection mode is currently active.
        
        Returns:
            bool: True if self-reflection mode is active, False otherwise
        """
        return self.self_reflection_mode
    
    def _compute_earthly_reward(self, action_type: str, context: Dict = None) -> Optional[float]:
        """
        Compute earthly reward based on homeostatic needs.
        
        Args:
            action_type: Type of action being evaluated
            context: Additional context for the action
            
        Returns:
            Earthly reward value or None if not available
        """
        try:
            # Get earthly game engine if available
            eg = getattr(self.main_app, "earthly_game", None)
            if not eg:
                return None
            
            # Get current need levels from context or default values
            need_levels = context.get("need_levels", {}) if context else {}
            if not need_levels:
                # Use default need levels if not provided
                need_levels = {
                    "safety": 0.5,
                    "achievement": 0.5,
                    "affiliation": 0.5,
                    "health": 0.5,
                    "learning": 0.5
                }
            
            # Compute homeostatic reward
            earthly_reward = eg.get_homeostatic_reward(need_levels)
            
            # Log the reward computation
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🌍 Earthly reward computed: {earthly_reward:.3f}")
            
            return earthly_reward
            
        except Exception as e:
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"❌ Error computing earthly reward: {e}")
            return None
    
    def monitor_consciousness_gaps(self):
        """Detect and record consciousness gaps."""
        try:
            if not self.main_app or not hasattr(self.main_app, "earthly_game"):
                return
            game = self.main_app.earthly_game

            if self.main_app.power_state == "OFFLINE":
                return  # No introspection while unconscious

            missed_rounds = game.get_unobserved_rounds("CARL")
            if missed_rounds > 0:
                self.add_thought(
                    f"I missed {missed_rounds} turns in the Earthly Game. "
                    "This feels like lost time or unconsciousness."
                )
                game.clear_unobserved_rounds("CARL")
                
        except Exception as e:
            self.logger.error(f"❌ Error monitoring consciousness gaps: {e}")