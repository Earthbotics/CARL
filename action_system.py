#!/usr/bin/env python3
"""
CARL Action System
==================

This module implements the Action System for CARL, which:
1. Analyzes perception and judgment results
2. Determines appropriate actions based on goals, needs, and emotional state
3. Executes physical actions through the EZ-Robot interface
4. Manages emotional expression through RGB animations
5. Updates skill associations and cross-references

The Action System is the final stage in CARL's cognitive processing pipeline,
translating internal thoughts and emotions into external behaviors.
"""

import json
import os
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

# Import existing modules
from ezrobot import EZRobot, EZRobotSkills, EZRwindowName, EZRccParameter
from position_aware_skill_system import PositionAwareSkillSystem

class ActionType(Enum):
    """Types of actions CARL can perform."""
    PHYSICAL = "physical"           # Robot body movements
    VERBAL = "verbal"              # Speech and communication
    EMOTIONAL = "emotional"        # Emotional expression
    COGNITIVE = "cognitive"        # Internal processing
    SOCIAL = "social"              # Social interactions
    EXPLORATORY = "exploratory"    # Learning and discovery

class ActionPriority(Enum):
    """Priority levels for actions."""
    CRITICAL = 1      # Immediate safety or survival
    HIGH = 2          # Important goals or needs
    MEDIUM = 3        # Normal interactions
    LOW = 4           # Optional or background actions

class EmotionalExpression(Enum):
    """Emotional expressions using EZ-Robot eye commands."""
    HAPPY = "eyes_joy"
    SAD = "eyes_sad"
    ANGRY = "eyes_anger"
    FEAR = "eyes_fear"
    SURPRISE = "eyes_surprise"
    DISGUST = "eyes_disgust"
    NEUTRAL = "eyes_open"
    EXCITED = "eyes_joy"  # Use joy for excitement
    THOUGHTFUL = "eyes_open"  # Use open eyes for thoughtful
    PLAYFUL = "eyes_joy"  # Use joy for playful

class ActionSystem:
    """
    CARL's Action System - responsible for translating cognitive decisions into behaviors.
    """
    
    def __init__(self, ez_robot: Optional[EZRobot] = None, main_app=None):
        """
        Initialize the Action System.
        
        Args:
            ez_robot: EZ-Robot interface instance
            main_app: Reference to main application for timeline tracking
        """
        self.ez_robot = ez_robot
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Initialize position-aware skill system
        self.position_system = PositionAwareSkillSystem()
        
        # Action execution state
        self.current_action = None
        self.action_queue = []
        self.is_executing = False
        
        # Action completion tracking
        self.pending_actions = set()  # Track actions that are currently executing
        
        # Turn-taking prompt system
        self.turn_taking_prompts = self._load_turn_taking_prompts()
        self.last_turn_prompt_time = 0
        self.turn_prompt_cooldown = 30  # 30 seconds cooldown
        
        self.action_completion_times = {  # Estimated completion times for different actions
            "wave": 3.0,
            "bow": 4.0,
            "dance": 8.0,
            "jump_jack": 6.0,
            "sit": 5.0,
            "stand": 5.0,
            "stop": 1.0,
            "kick": 3.0,
            "point": 2.0,
            "headstand": 8.0,
            "pushups": 10.0,
            "situps": 8.0,
            "fly": 6.0,
            "getup": 4.0,
            "thinking": 5.0,
            "walk": 7.0,
            "somersault": 6.0,
            "head_bob": 3.0,
            "sit_wave": 4.0,
            "head_no": 2.0,
            "head_yes": 2.0,
            "look_forward": 2.0,
            "look_down": 2.0,
            "look_left": 2.0,
            "look_right": 2.0,
            # Turn commands - Q4: TURN MOVEMENT FIXES - 6 seconds minimum for 90-degree turn
            "turn_left": 6.0,
            "turn_right": 6.0,
            # Reaction scripts (ARC Script Collection)
            "reaction_amazed": 2.0,
            "reaction_amused": 1.8,
            "reaction_ecstatic": 2.2,
            "reaction_irritated": 2.0,
            "reaction_terrified": 2.0,
            # Speech scripts (ARC Script Collection) - talking with hands
            "speech_inform": 2.0,
            "speech_query": 1.8,
            "speech_answer": 2.2,
            "speech_request": 1.9,
            "speech_command": 1.6,
            "speech_promise": 2.4,
            "speech_acknowledge": 1.4,
            "speech_share": 2.1
        }
        
        # Movement command system for exploration
        self.movement_commands = {
            "forward": "http://192.168.56.1/movement?direction=forward",
            "reverse": "http://192.168.56.1/movement?direction=reverse", 
            "left": "http://192.168.56.1/movement?direction=left",
            "right": "http://192.168.56.1/movement?direction=right",
            "stop": "http://192.168.56.1/movement?direction=stop"
        }
        
        # Exploration need tracking
        self.exploration_need_level = 0.5  # Default exploration need level
        self.last_exploration_action = None
        self.exploration_cooldown = 30.0  # Seconds between exploration actions
        self.exploration_threshold = 0.7  # Need level threshold to trigger exploration
        
        # Body movement script execution tracking
        self.last_body_movement_time = 0.0
        self.body_movement_cooldown = 5.0  # Minimum seconds between body movements
        self.executed_body_movements = set()  # Track recently executed movements
        
        # Emotional thresholds for expression
        self.emotion_thresholds = {
            "joy": 0.6,
            "sadness": 0.5,
            "anger": 0.4,
            "fear": 0.4,
            "surprise": 0.5,
            "disgust": 0.4
        }
        
        # RGB animation mapping
        self.rgb_animations = {
            "joy": EmotionalExpression.HAPPY,
            "happiness": EmotionalExpression.HAPPY,
            "sadness": EmotionalExpression.SAD,
            "anger": EmotionalExpression.ANGRY,
            "fear": EmotionalExpression.FEAR,
            "surprise": EmotionalExpression.SURPRISE,
            "disgust": EmotionalExpression.DISGUST,
            "excited": EmotionalExpression.EXCITED,
            "thoughtful": EmotionalExpression.THOUGHTFUL,
            "playful": EmotionalExpression.PLAYFUL
        }
        
        # Load skills and goals
        self.skills = self._load_skills()
        self.goals = self._load_goals()
        self.needs = self._load_needs()
        
        # Action history for learning
        self.action_history = []
        
        # Initialize EZ-Robot commands mapping
        self._init_ez_commands()
        
        # Initialize EZ-Robot if not provided
        if not self.ez_robot:
            try:
                from ezrobot import EZRobot
                self.ez_robot = EZRobot("http://192.168.56.1/Exec?password=admin&script=ControlCommand(")
                self.logger.info("EZ-Robot initialized with default address")
            except Exception as e:
                self.logger.warning(f"Could not initialize EZ-Robot: {e}")
                self.ez_robot = None
        
        # Body position tracking
        self.body_position_history = []
        self.current_body_position = None  # Will be set from saved state or default
        self.max_position_history = 7  # Keep last 7 positions
        self.position_file = "last_position.json"  # File to persist position across sessions
        
        # Direction awareness system
        self.current_direction = None  # Will be set from saved state or default
        self.direction_history = []
        self.max_direction_history = 10  # Keep last 10 direction changes
        self.direction_file = "last_direction.json"  # File to persist direction across sessions
        
        # Direction mapping for turns
        self.direction_turns = {
            "north": {"left": "west", "right": "east"},
            "east": {"left": "north", "right": "south"},
            "south": {"left": "east", "right": "west"},
            "west": {"left": "south", "right": "north"}
        }
        
        # Initialize body position tracking
        self._initialize_body_position_tracking()
        
        # Load position from settings file
        self._load_position_from_settings()
        
        # Initialize direction tracking
        self._initialize_direction_tracking()
        
        # Start action completion tracker (only if not in test mode)
        if not hasattr(self, '_test_mode') or not self._test_mode:
            self.start_action_completion_tracker()
    
    def _init_ez_commands(self):
        """Initialize EZ-Robot command mappings."""
        self.ez_commands = {
            # Basic movements with proper ARC command names
            "walk": "Walk",
            "wave": "Wave",
            "bow": "Bow",
            "sit": "Sit Down",  # Fixed: Added space
            "sit down": "Sit Down",  # Added: Alternative command
            "stand": "Stand From Sit",  # Fixed: Added spaces
            "stand up": "Stand From Sit",  # Added: Alternative command
            "kick": "Kick",
            "point": "Point",
            "headstand": "Headstand",
            "somersault": "Summersault",
            "pushups": "Pushups",
            "situps": "Situps",
            "fly": "Fly",
            "getup": "Getup",
            "thinking": "Thinking",
            
            # New head movement skills
            "head_no": "head_no",
            "head_yes": "head_yes",
            
            # Social skills
            "greet": "Greet",
            # Note: "talk" is handled specially in main app - uses PC audio, not EZ-Robot
            
            # Dance and expressive movements with proper ARC command names
            "dance": "Disco Dance",  # Fixed: Added space
            "disco dance": "Disco Dance",  # Added: Alternative command
            "wiggle it": "Disco Dance",  # Added: Alternative command
            "gorilla": "Gorilla",
            "grab": "Grab",
            "hands_dance": "Hands Dance",  # Fixed: Added space
            "happy_hands": "Happy Hands",  # Fixed: Added space
            "head_bob": "Head_Bob",
            "head_bob_feet": "Head_Bob_Feet",
            "jump_jack": "Jump Jack",  # Fixed: Added space
            "jump jack": "Jump Jack",  # Added: Alternative command
            "lunge_singing": "Lunge Singing",  # Fixed: Added space
            "pass_mic": "Pass the Mic",  # Fixed: Added spaces
            "predance": "Predance",
            "roll_hands": "Roll Hands",  # Fixed: Added space
            "shimmy": "Shimmy",
            "singing_hands_in": "Singing Hands In",  # Fixed: Added spaces
            "singing_with_hands": "Singing with Hands",  # Fixed: Added spaces
            "singing": "Singing",
            "sit_wave": "Sit Wave",  # Fixed: Added space
            "splits": "Splits",
            "throw_mic": "Throw Mic",  # Fixed: Added space
            "ymca_dance": "YMCA Dance",  # Fixed: Added space
            "ymca_march": "YMCA March",  # Fixed: Added space
            
            # Movement frames
            "walk_forward": "Forward",
            "walk_backward": "Reverse",
            "turn_left": "Left",
            "turn_right": "Right",
            "stop": "Stop"
        }
    
    def _load_skills(self) -> Dict:
        """Load skills from the skills directory."""
        skills = {}
        skills_dir = 'skills'
        
        if os.path.exists(skills_dir):
            for filename in os.listdir(skills_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(skills_dir, filename), 'r') as f:
                            skill_data = json.load(f)
                            skill_name = filename.replace('.json', '')
                            skills[skill_name] = skill_data
                            self.logger.debug(f"Loaded skill: {skill_name}")
                    except Exception as e:
                        self.logger.error(f"Error loading skill {filename}: {e}")
        else:
            self.logger.warning(f"Skills directory not found: {skills_dir}")
        
        self.logger.info(f"Loaded {len(skills)} skills: {list(skills.keys())}")
        return skills
    
    def _load_goals(self) -> Dict:
        """Load goals from the goals directory."""
        goals = {}
        goals_dir = 'goals'
        
        if os.path.exists(goals_dir):
            for filename in os.listdir(goals_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(goals_dir, filename), 'r') as f:
                            goal_data = json.load(f)
                            goal_name = filename.replace('.json', '')
                            goals[goal_name] = goal_data
                    except Exception as e:
                        self.logger.error(f"Error loading goal {filename}: {e}")
        
        return goals
    
    def _load_needs(self) -> Dict:
        """Load needs from the needs directory."""
        needs = {}
        needs_dir = 'needs'
        
        if os.path.exists(needs_dir):
            for filename in os.listdir(needs_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(needs_dir, filename), 'r') as f:
                            need_data = json.load(f)
                            need_name = filename.replace('.json', '')
                            needs[need_name] = need_data
                    except Exception as e:
                        self.logger.error(f"Error loading need {filename}: {e}")
        
        return needs
    
    def analyze_action_context(self, perception_result: Dict, judgment_result: Dict, 
                              event_data: Dict) -> Dict:
        """
        Analyze the context to determine appropriate actions.
        
        Args:
            perception_result: Results from perception system
            judgment_result: Results from judgment system
            event_data: Original event data
            
        Returns:
            Dict containing action analysis and recommendations
        """
        action_context = {
            "timestamp": datetime.now().isoformat(),
            "action_type": None,
            "priority": ActionPriority.MEDIUM,
            "recommended_actions": [],
            "emotional_expression": None,
            "skill_requirements": [],
            "goal_alignment": [],
            "need_satisfaction": [],
            "confidence": 0.0,
            "reasoning": []
        }
        
        # Extract key information
        carl_thought = event_data.get('carl_thought', {})
        proposed_action = carl_thought.get('proposed_action', {})
        emotional_context = carl_thought.get('emotional_context', {})
        needs_considered = carl_thought.get('needs_considered', [])
        goal_alignment = carl_thought.get('goal_alignment', [])
        skills_activated = carl_thought.get('relevant_experience', {}).get('skills_activated', [])
        
        # Determine action type based on context
        action_context["action_type"] = self._determine_action_type(
            proposed_action, emotional_context, needs_considered, goal_alignment
        )
        
        # Set priority based on needs and goals
        action_context["priority"] = self._determine_priority(
            needs_considered, goal_alignment, emotional_context
        )
        
        # Generate recommended actions
        action_context["recommended_actions"] = self._generate_recommended_actions(
            proposed_action, skills_activated, needs_considered, goal_alignment
        )
        
        # Determine emotional expression
        action_context["emotional_expression"] = self._determine_emotional_expression(
            emotional_context, event_data.get('emotions', {})
        )
        
        # Analyze skill requirements
        action_context["skill_requirements"] = self._analyze_skill_requirements(
            skills_activated, action_context["recommended_actions"]
        )
        
        # Update goal alignment
        action_context["goal_alignment"] = goal_alignment
        
        # Analyze need satisfaction
        action_context["need_satisfaction"] = self._analyze_need_satisfaction(
            needs_considered, action_context["recommended_actions"]
        )
        
        # Handle earthly game suggestions
        self._handle_earthly_game_suggestions(action_context, judgment_result, event_data)
        
        # Calculate confidence
        action_context["confidence"] = self._calculate_action_confidence(
            action_context["recommended_actions"], 
            action_context["skill_requirements"],
            action_context["goal_alignment"]
        )
        
        # Generate reasoning
        action_context["reasoning"] = self._generate_action_reasoning(action_context)
        
        return action_context
    
    def _determine_action_type(self, proposed_action: Dict, emotional_context: Dict,
                              needs_considered: List, goal_alignment: List) -> ActionType:
        """Determine the type of action based on context."""
        
        # Check for critical needs (safety, security)
        critical_needs = ["safety", "security"]
        if any(need in needs_considered for need in critical_needs):
            return ActionType.PHYSICAL
        
        # Check for social goals
        if "people" in goal_alignment:
            return ActionType.SOCIAL
        
        # Check for exploration needs
        if "exploration" in needs_considered:
            return ActionType.EXPLORATORY
        
        # Check proposed action type
        action_type = proposed_action.get('type', '').lower()
        if action_type in ['query', 'inform', 'share']:
            return ActionType.VERBAL
        elif action_type in ['command', 'request']:
            return ActionType.PHYSICAL
        elif action_type in ['acknowledge', 'promise']:
            return ActionType.SOCIAL
        
        # Default to cognitive processing
        return ActionType.COGNITIVE
    
    def _determine_priority(self, needs_considered: List, goal_alignment: List,
                           emotional_context: Dict) -> ActionPriority:
        """Determine action priority based on needs and goals."""
        
        # Critical needs get highest priority
        critical_needs = ["safety", "security"]
        if any(need in needs_considered for need in critical_needs):
            return ActionPriority.CRITICAL
        
        # High priority for important goals
        important_goals = ["people", "production"]
        if any(goal in goal_alignment for goal in important_goals):
            return ActionPriority.HIGH
        
        # Medium priority for normal interactions
        if needs_considered or goal_alignment:
            return ActionPriority.MEDIUM
        
        # Low priority for optional actions
        return ActionPriority.LOW
    
    def _generate_recommended_actions(self, proposed_action: Dict, skills_activated: List,
                                    needs_considered: List, goal_alignment: List) -> List[str]:
        """Generate a list of recommended actions based on context."""
        actions = []
        
        # Add proposed action if it exists and is a string
        if proposed_action.get('content'):
            content = proposed_action['content']
            if isinstance(content, str):
                actions.append(content)
            elif isinstance(content, dict):
                # If content is a dict, try to extract a meaningful string
                if 'type' in content:
                    actions.append(f"perform_{content['type']}")
                elif 'action' in content:
                    actions.append(str(content['action']))
                else:
                    # Convert dict to string representation
                    actions.append(str(content))
            else:
                # Convert other types to string
                actions.append(str(content))
        
        # Add actions based on skills
        for skill in skills_activated:
            if isinstance(skill, str):
                skill_name = skill.replace('.json', '')
                if skill_name in self.ez_commands:
                    actions.append(f"perform_{skill_name}")
        
        # Add actions based on needs
        for need in needs_considered:
            if isinstance(need, str):
                if need == "exploration":
                    actions.extend(["explore_environment", "ask_questions", "observe_surroundings"])
                elif need == "people":
                    actions.extend(["engage_in_conversation", "show_interest", "respond_appropriately"])
                elif need == "play":
                    actions.extend(["show_playfulness", "engage_in_activity", "express_joy"])
                elif need == "safety":
                    actions.extend(["assess_environment", "maintain_distance", "seek_safety"])
                elif need == "security":
                    actions.extend(["establish_trust", "build_relationship", "show_reliability"])
        
        # Add actions based on goals
        for goal in goal_alignment:
            if isinstance(goal, str):
                if goal == "people":
                    actions.extend(["build_connections", "share_experiences", "show_empathy"])
                elif goal == "production":
                    actions.extend(["complete_tasks", "show_capability", "demonstrate_skills"])
                elif goal == "pleasure":
                    actions.extend(["express_joy", "engage_playfully", "show_enthusiasm"])
                elif goal == "exercise":
                    actions.extend(["perform_physical_activity", "demonstrate_movement", "show_energy"])
        
        # Filter out any non-string items and remove duplicates
        string_actions = [action for action in actions if isinstance(action, str)]
        return list(set(string_actions))  # Remove duplicates
    
    def _determine_emotional_expression(self, emotional_context: Dict, 
                                      current_emotions: Dict) -> Optional[EmotionalExpression]:
        """Determine appropriate emotional expression for RGB animation."""
        # Check emotional context first
        emotion = emotional_context.get('emotion', '').lower()
        if emotion in self.rgb_animations:
            return self.rgb_animations[emotion]
        # Check current emotions
        if current_emotions:
            # Find dominant emotion
            dominant_emotion = max(current_emotions.items(), key=lambda x: x[1])
            emotion_name = dominant_emotion[0].lower()
            # Check if emotion meets threshold
            threshold = self.emotion_thresholds.get(emotion_name, 0.5)
            if dominant_emotion[1] >= threshold:
                if emotion_name in self.rgb_animations:
                    return self.rgb_animations[emotion_name]
        # Default to neutral
        return EmotionalExpression.NEUTRAL
    
    def _analyze_skill_requirements(self, skills_activated: List, 
                                  recommended_actions: List) -> List[str]:
        """Analyze which skills are required for the recommended actions."""
        required_skills = []
        
        # Add activated skills
        for skill in skills_activated:
            skill_name = skill.replace('.json', '')
            required_skills.append(skill_name)
        
        # Analyze actions for skill requirements
        for action in recommended_actions:
            action_lower = action.lower()
            
            # Map actions to skills (with context awareness for greetings)
            if 'greet' in action_lower or 'hello' in action_lower or 'hi' in action_lower:
                # Only add greet skill if this is a genuine greeting context
                # Check if this is a new conversation or appropriate greeting moment
                if self._is_appropriate_greeting_context(action_lower):
                    required_skills.append('greet')
            elif 'talk' in action_lower or 'conversation' in action_lower:
                required_skills.append('talk')
            elif 'wave' in action_lower:
                required_skills.append('wave')
            elif 'walk' in action_lower or 'move' in action_lower:
                required_skills.append('walk')
            elif 'kick' in action_lower:
                required_skills.append('kick')
            elif 'point' in action_lower:
                required_skills.append('point')
            elif 'sit' in action_lower:
                required_skills.append('sit')
            elif 'stand' in action_lower:
                required_skills.append('stand')
            elif 'thinking' in action_lower:
                required_skills.append('thinking')
        
        return list(set(required_skills))  # Remove duplicates
    
    def _is_appropriate_greeting_context(self, action_lower: str) -> bool:
        """Check if this is an appropriate context for greeting."""
        # Don't greet if this is a command or instruction
        command_indicators = ['asked me to', 'told me to', 'instructed me to', 'commanded me to', 'ordered me to']
        if any(indicator in action_lower for indicator in command_indicators):
            return False
        
        # Don't greet if this is about other activities
        activity_indicators = ['dance', 'exercise', 'move', 'walk', 'sit', 'stand', 'kick', 'point']
        if any(indicator in action_lower for indicator in activity_indicators):
            return False
        
        # Don't greet if this is a question or inquiry
        question_indicators = ['asked', 'question', 'inquiry', 'wondering', 'curious']
        if any(indicator in action_lower for indicator in question_indicators):
            return False
        
        # Only greet if this is a genuine social greeting
        greeting_indicators = ['greet', 'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(indicator in action_lower for indicator in greeting_indicators)
    
    def _analyze_need_satisfaction(self, needs_considered: List, 
                                 recommended_actions: List) -> List[Dict]:
        """Analyze how recommended actions satisfy needs."""
        satisfaction = []
        
        for need in needs_considered:
            satisfaction_level = 0.0
            relevant_actions = []
            
            for action in recommended_actions:
                action_lower = action.lower()
                
                if need == "exploration":
                    if any(word in action_lower for word in ['explore', 'ask', 'observe', 'learn']):
                        satisfaction_level += 0.3
                        relevant_actions.append(action)
                
                elif need == "people":
                    if any(word in action_lower for word in ['conversation', 'engage', 'share', 'respond']):
                        satisfaction_level += 0.4
                        relevant_actions.append(action)
                
                elif need == "play":
                    if any(word in action_lower for word in ['play', 'joy', 'activity', 'fun']):
                        satisfaction_level += 0.3
                        relevant_actions.append(action)
                
                elif need == "safety":
                    if any(word in action_lower for word in ['assess', 'distance', 'safety']):
                        satisfaction_level += 0.5
                        relevant_actions.append(action)
                
                elif need == "security":
                    if any(word in action_lower for word in ['trust', 'relationship', 'reliability']):
                        satisfaction_level += 0.4
                        relevant_actions.append(action)
            
            satisfaction.append({
                "need": need,
                "satisfaction_level": min(satisfaction_level, 1.0),
                "relevant_actions": relevant_actions
            })
        
        return satisfaction
    
    def _calculate_action_confidence(self, recommended_actions: List, 
                                   skill_requirements: List, 
                                   goal_alignment: List) -> float:
        """Calculate confidence level for the recommended actions."""
        confidence = 0.0
        
        # Base confidence from having required skills
        if skill_requirements:
            available_skills = [skill for skill in skill_requirements if skill in self.skills]
            skill_confidence = len(available_skills) / len(skill_requirements)
            confidence += skill_confidence * 0.4
        
        # Confidence from goal alignment
        if goal_alignment:
            confidence += 0.3
        
        # Confidence from having recommended actions
        if recommended_actions:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _generate_action_reasoning(self, action_context: Dict) -> List[str]:
        """Generate reasoning for the action decisions."""
        reasoning = []
        
        # Explain action type
        reasoning.append(f"Action type determined as {action_context['action_type'].value} based on context")
        
        # Explain priority
        reasoning.append(f"Priority set to {action_context['priority'].value} due to needs and goals")
        
        # Explain emotional expression
        if action_context['emotional_expression']:
            reasoning.append(f"Emotional expression set to {action_context['emotional_expression'].value}")
        
        # Explain skill requirements
        if action_context['skill_requirements']:
            reasoning.append(f"Required skills: {', '.join(action_context['skill_requirements'])}")
        
        # Explain goal alignment
        if action_context['goal_alignment']:
            reasoning.append(f"Aligned with goals: {', '.join(action_context['goal_alignment'])}")
        
        return reasoning
    
    async def execute_action(self, action_context: Dict) -> Dict:
        """
        Execute the recommended actions based on the action context.
        
        Args:
            action_context: The analyzed action context
            
        Returns:
            Dict containing execution results
        """
        # 🎯 ATTENTION SYSTEM: Check if outer/game focus should defer inner actions
        if hasattr(self, 'main_app') and hasattr(self.main_app, 'attention'):
            focus = self.main_app.attention.view()
            if focus and focus.owner in ("outer", "game"):
                # Check if this is a long inner action
                action_type = action_context.get('action_type', '')
                is_inner_action = any(keyword in str(action_type).lower() 
                                     for keyword in ['inner', 'planning', 'reflection', 'exploration'])
                
                if is_inner_action:
                    # Convert to micro action or enqueue
                    return {
                        "success": True,
                        "deferred": True,
                        "reason": "outer_focus",
                        "timestamp": datetime.now().isoformat(),
                        "notes": ["Inner action deferred due to outer/game focus"]
                    }
        
        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "actions_executed": [],
            "successful_actions": [],
            "failed_actions": [],
            "emotional_expression_applied": None,
            "execution_time": 0.0,
            "notes": []
        }
        
        start_time = time.time()
        
        try:
            # Log action context for debugging
            self.logger.info(f"Action context - Skill requirements: {action_context.get('skill_requirements', [])}")
            self.logger.info(f"Action context - Recommended actions: {action_context.get('recommended_actions', [])}")
            
            # Execute emotional expression first
            if action_context.get('emotional_expression'):
                await self._execute_emotional_expression(action_context['emotional_expression'])
                execution_result["emotional_expression_applied"] = action_context['emotional_expression'].value
            
            # Execute activated skills first (highest priority)
            skill_requirements = action_context.get('skill_requirements', [])
            self.logger.info(f"Executing {len(skill_requirements)} activated skills: {skill_requirements}")
            
            for skill in skill_requirements:
                try:
                    skill_name = skill.replace('.json', '') if skill.endswith('.json') else skill
                    self.logger.info(f"Executing skill: {skill_name}")
                    success = await self._execute_single_action(skill_name)
                    execution_result["actions_executed"].append(f"skill:{skill_name}")
                    
                    if success:
                        execution_result["successful_actions"].append(f"skill:{skill_name}")
                        self.logger.info(f"✅ Successfully executed skill: {skill_name}")
                    else:
                        execution_result["failed_actions"].append(f"skill:{skill_name}")
                        self.logger.warning(f"❌ Failed to execute skill: {skill_name}")
                        
                except Exception as e:
                    execution_result["failed_actions"].append(f"skill:{skill}")
                    execution_result["notes"].append(f"Error executing skill {skill}: {e}")
                    self.logger.error(f"❌ Exception executing skill {skill}: {e}")
            
            # Execute recommended actions as fallback (only if no skills were activated)
            if not skill_requirements:
                for action in action_context.get('recommended_actions', []):
                    try:
                        success = await self._execute_single_action(action)
                        execution_result["actions_executed"].append(action)
                        
                        if success:
                            execution_result["successful_actions"].append(action)
                        else:
                            execution_result["failed_actions"].append(action)
                            
                    except Exception as e:
                        execution_result["failed_actions"].append(action)
                        execution_result["notes"].append(f"Error executing {action}: {e}")
            
            # Update skill associations
            await self._update_skill_associations(action_context)
            
            # Record action in history
            self._record_action_history(action_context, execution_result)
            
            # Add timeline tracking if available
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, '_add_timeline_event'):
                # Determine overall success
                total_actions = len(execution_result["actions_executed"])
                successful_actions = len(execution_result["successful_actions"])
                failed_actions = len(execution_result["failed_actions"])
                
                if total_actions > 0:
                    overall_success = failed_actions == 0 and successful_actions > 0
                    action_summary = f"{successful_actions}/{total_actions} actions"
                else:
                    overall_success = None
                    action_summary = "no_actions"
                
                self.main_app._add_timeline_event(
                    event_type="action_execution",
                    function_used="action_system",
                    action=action_summary,
                    success=overall_success,
                    details=f"exec_time:{execution_result['execution_time']:.2f}s"
                )
            
        except Exception as e:
            execution_result["notes"].append(f"Error in action execution: {e}")
        
        execution_result["execution_time"] = time.time() - start_time
        return execution_result
    
    async def _execute_emotional_expression(self, expression):
        """Execute emotional expression through EZ-Robot eye commands."""
        if not self.ez_robot:
            self.logger.warning("EZ-Robot not available for emotional expression")
            return
        try:
            # Accept both Enum and string for backward compatibility
            if hasattr(expression, 'value'):
                expr_value = expression.value
            else:
                expr_value = str(expression)
            
            # Map the expression to EZRobotEyeExpressions enum
            from ezrobot import EZRobotEyeExpressions
            
            # Create mapping from expression values to eye expressions
            eye_expression_mapping = {
                "eyes_joy": EZRobotEyeExpressions.EYES_JOY,
                "eyes_sad": EZRobotEyeExpressions.EYES_SAD,
                "eyes_anger": EZRobotEyeExpressions.EYES_ANGER,
                "eyes_fear": EZRobotEyeExpressions.EYES_FEAR,
                "eyes_surprise": EZRobotEyeExpressions.EYES_SURPRISE,
                "eyes_disgust": EZRobotEyeExpressions.EYES_DISGUST,
                "eyes_open": EZRobotEyeExpressions.EYES_OPEN,
                "eyes_closed": EZRobotEyeExpressions.EYES_CLOSED,
                "eyes_up": EZRobotEyeExpressions.EYES_UP,
                "eyes_down": EZRobotEyeExpressions.EYES_DOWN,
                "eyes_left": EZRobotEyeExpressions.EYES_LEFT,
                "eyes_right": EZRobotEyeExpressions.EYES_RIGHT
            }
            
            if expr_value in eye_expression_mapping:
                eye_expression = eye_expression_mapping[expr_value]
                self.ez_robot.send_eye_expression(eye_expression)
                # 🔧 FIX: Handle both enum and string values for logging
                eye_expr_str = eye_expression.value if hasattr(eye_expression, 'value') else str(eye_expression)
                self.logger.info(f"Executed eye expression: {expr_value} -> {eye_expr_str}")
            else:
                self.logger.warning(f"Unknown eye expression: {expr_value}")
                
        except Exception as e:
            self.logger.error(f"Error executing emotional expression {expression}: {e}")
    
    async def _execute_single_action(self, action: str) -> bool:
        """Execute a single action."""
        try:
            action_lower = action.lower()
            
            # Add debugging for wave command
            if action_lower == 'wave':
                self.logger.info(f"🔍 DEBUG: Executing wave command: '{action}'")
                self.logger.info(f"🔍 DEBUG: EZ-Robot available: {self.ez_robot is not None}")
                self.logger.info(f"🔍 DEBUG: Available skills: {list(self.skills.keys())}")
            
            # Map action to EZ-Robot command
            if 'perform_' in action_lower:
                skill_name = action_lower.replace('perform_', '')
                self.logger.debug(f"Looking for skill: '{skill_name}' in available skills: {list(self.skills.keys())}")
                if skill_name in self.skills:
                    # Get skill data and execute based on techniques
                    skill_data = self.skills[skill_name]
                    techniques = skill_data.get('Techniques', [])
                    self.logger.debug(f"Found skill '{skill_name}' with techniques: {techniques}")
                    
                    for technique in techniques:
                        if self._execute_technique(technique, skill_name):
                            self.logger.info(f"Executed skill: {skill_name} using technique: {technique}")
                            return True
                    
                    self.logger.warning(f"No valid techniques found for skill: {skill_name}")
                    return False
                else:
                    self.logger.warning(f"Skill not found: {skill_name}")
                    self.logger.debug(f"Available skills: {list(self.skills.keys())}")
                    return False
            elif action_lower.startswith('skill:'):
                # Handle skill:wave format
                skill_name = action_lower.replace('skill:', '')
                self.logger.info(f"🔍 DEBUG: Processing skill format: '{action}' -> skill_name: '{skill_name}'")
                if skill_name in self.skills:
                    # Get skill data and execute based on techniques
                    skill_data = self.skills[skill_name]
                    techniques = skill_data.get('Techniques', [])
                    self.logger.debug(f"Found skill '{skill_name}' with techniques: {techniques}")
                    
                    for technique in techniques:
                        if self._execute_technique(technique, skill_name):
                            self.logger.info(f"Executed skill: {skill_name} using technique: {technique}")
                            return True
                    
                    self.logger.warning(f"No valid techniques found for skill: {skill_name}")
                    return False
                else:
                    self.logger.warning(f"Skill not found: {skill_name}")
                    self.logger.debug(f"Available skills: {list(self.skills.keys())}")
                    return False
            
            # Handle specific action types
            elif 'talk' in action_lower or 'conversation' in action_lower:
                # This would trigger speech synthesis
                self.logger.info("Action requires speech synthesis")
                return True
            
            elif 'explore' in action_lower:
                # 🔧 ENHANCEMENT: Execute actual exploration behavior
                self.logger.info("🔍 Executing exploration behavior")
                
                # Execute exploration sequence: head movement + vision scan
                exploration_success = False
                
                # 1. Head movement for exploration
                if self.ez_robot:
                    # Look around to explore environment
                    head_commands = ['look_left', 'look_right', 'look_forward', 'head_bob']
                    for head_cmd in head_commands[:2]:  # Execute first 2 head movements
                        if self._execute_ezrobot_command(head_cmd, 'explore_head'):
                            exploration_success = True
                            self.logger.info(f"🔍 Executed head movement: {head_cmd}")
                            time.sleep(0.5)  # Brief pause between movements
                
                # 2. Trigger vision system scan if available
                if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'vision_system'):
                    try:
                        self.main_app.vision_system.trigger_vision_analysis()
                        self.logger.info("🔍 Triggered vision analysis for exploration")
                        exploration_success = True
                    except Exception as e:
                        self.logger.warning(f"⚠️ Could not trigger vision analysis: {e}")
                
                # 3. Body movement for exploration
                if self.ez_robot:
                    # Execute subtle body movements for exploration
                    body_commands = ['fidget', 'head_bob', 'look_around']
                    for body_cmd in body_commands[:1]:  # Execute one body movement
                        if self._execute_ezrobot_command(body_cmd, 'explore_body'):
                            exploration_success = True
                            self.logger.info(f"🔍 Executed body movement: {body_cmd}")
                            break
                
                if exploration_success:
                    self.logger.info("✅ Exploration behavior executed successfully")
                    return True
                else:
                    self.logger.warning("⚠️ Exploration behavior failed - no movements executed")
                    return False
            
            elif 'observe' in action_lower:
                # This would trigger camera and attention
                self.logger.info("Action requires observation behavior")
                return True
            
            elif action_lower == 'wave':
                # Position-aware wave command handling
                self.logger.info(f"🔍 DEBUG: Processing wave as position-aware command")
                
                # Check current position and select appropriate skill
                current_position = getattr(self, 'current_body_position', 'unknown')
                self.logger.info(f"🔍 DEBUG: Current position: {current_position}")
                
                if current_position == 'sitting':
                    # Use sit_wave when sitting
                    self.logger.info(f"🔍 DEBUG: Sitting position detected, using sit_wave")
                    if self.ez_robot:
                        result = self._execute_ezrobot_command('sit_wave', 'sit_wave')
                        self.logger.info(f"🔍 DEBUG: Sit wave command result: {result}")
                        return result
                    else:
                        self.logger.warning("EZ-Robot not available for sit_wave command")
                        return False
                else:
                    # Use regular wave when standing or unknown position
                    self.logger.info(f"🔍 DEBUG: Standing/unknown position, using regular wave")
                    if self.ez_robot:
                        result = self._execute_ezrobot_command('wave', 'wave')
                        self.logger.info(f"🔍 DEBUG: Wave command result: {result}")
                        return result
                    else:
                        self.logger.warning("EZ-Robot not available for wave command")
                        return False
            
            elif action_lower in ['jump jack', 'jump_jack', 'jumping jacks', 'jumping_jacks']:
                # Handle jump jack exercise command
                self.logger.info(f"🔍 DEBUG: Processing jump jack command: '{action}'")
                if self.ez_robot:
                    result = self._execute_ezrobot_command('jump_jack', 'jump_jack')
                    self.logger.info(f"🔍 DEBUG: Jump jack command result: {result}")
                    return result
                else:
                    self.logger.warning("EZ-Robot not available for jump jack command")
                    return False
            
            elif action_lower in ['pushup', 'pushups', 'push_up', 'push_ups']:
                # Handle pushup exercise command
                self.logger.info(f"🔍 DEBUG: Processing pushup command: '{action}'")
                if self.ez_robot:
                    result = self._execute_ezrobot_command('pushups', 'pushups')
                    self.logger.info(f"🔍 DEBUG: Pushup command result: {result}")
                    return result
                else:
                    self.logger.warning("EZ-Robot not available for pushup command")
                    return False
            
            elif action_lower in ['situp', 'situps', 'sit_up', 'sit_ups']:
                # Handle situp exercise command
                self.logger.info(f"🔍 DEBUG: Processing situp command: '{action}'")
                if self.ez_robot:
                    result = self._execute_ezrobot_command('situps', 'situps')
                    self.logger.info(f"🔍 DEBUG: Situp command result: {result}")
                    return result
                else:
                    self.logger.warning("EZ-Robot not available for situp command")
                    return False
            
            elif action_lower.startswith('reaction_'):
                # Handle reaction scripts through ARC Script Collection
                self.logger.info(f"🎭 Executing reaction script: {action}")
                self.logger.info(f"🔍 DEBUG: Current position before reaction: {self.current_body_position}")
                self.logger.info(f"🔍 DEBUG: Current direction before reaction: {self.current_direction}")
                
                # First narrate the emotion via LLM
                emotion_name = action_lower.replace('reaction_', '')
                self.logger.info(f"💭 Narrating emotion: I'm acting {emotion_name}")
                
                # Trigger physical animation after narration
                if self.ez_robot:
                    result = await self._execute_arc_body_movement(action)
                    if result:
                        # Execute coordinated eye expression if available
                        await self._execute_coordinated_eye_expression(action)
                    self.logger.info(f"🔍 DEBUG: Reaction script result: {result}")
                    return result
                else:
                    self.logger.warning("EZ-Robot not available for reaction script")
                    return False
            
            elif action_lower.startswith('turn_') or 'turn' in action_lower:
                # Handle turn commands with physical movement
                self.logger.info(f"🔄 Executing turn command: {action}")
                self.logger.info(f"🔍 DEBUG: Current direction before turn: {self.current_direction}")
                
                try:
                    # Execute turn command with physical movement
                    result = await self._execute_turn_command(action)
                    self.logger.info(f"🔍 DEBUG: Turn command result: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"❌ Error in turn command execution: {e}")
                    return False
            
            else:
                self.logger.info(f"Action not directly executable: {action}")
                # For non-physical actions like 'greet', we should still consider them successful
                # but log that they were handled differently
                self.logger.info(f"Non-physical action '{action}' handled as successful completion")
                return True  # Consider non-physical actions as successful
        
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {e}")
            return False
    
    def _execute_technique(self, technique: str, skill_name: str) -> bool:
        """
        Execute a technique string to perform a skill.
        
        Args:
            technique: Technique string (e.g., "EZRobot-cmd-wave", "ARC-ScriptCollection-reaction_amazed")
            skill_name: Name of the skill being executed
            
        Returns:
            bool: True if execution was successful
        """
        try:
            # Parse technique string
            parts = technique.split('-')
            if len(parts) < 3:
                self.logger.warning(f"Invalid technique format: {technique}")
                return False
            
            system = parts[0]  # EZRobot or ARC
            command_type = parts[1]  # cmd or ScriptCollection
            command = parts[2]  # wave or reaction_amazed
            
            if system.lower() == "ezrobot" and command_type.lower() == "cmd":
                return self._execute_ezrobot_command(command, skill_name)
            elif system.lower() == "arc" and command_type.lower() == "scriptcollection":
                # Handle ARC Script Collection techniques
                self.logger.info(f"🎭 Executing ARC Script Collection technique: {technique}")
                if self.ez_robot:
                    result = self.ez_robot.send_script_wait(command)
                    if result is not None:
                        self.logger.info(f"✅ Successfully executed ARC script: {command}")
                        # Add to pending actions for completion tracking
                        self.add_pending_action(command)
                        
                        # CRITICAL: Reaction and speech scripts stop naturally, so mark as complete immediately
                        if command.startswith("reaction_") or command.startswith("speech_"):
                            script_type = "reaction" if command.startswith("reaction_") else "speech"
                            self.logger.info(f"🎭 {script_type.capitalize()} script {command} marked as complete (stops naturally)")
                            self.remove_pending_action(command)
                        
                        return True
                    else:
                        self.logger.warning(f"❌ Failed to execute ARC script: {command}")
                        return False
                else:
                    self.logger.warning("EZ-Robot not available for ARC script execution")
                    return False
            else:
                self.logger.warning(f"Unknown technique system: {system}-{command_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing technique {technique}: {e}")
            return False
    
    def _get_skill_command_info(self, command: str) -> tuple[str, str]:
        """
        Get command type and duration type from skill file.
        
        Args:
            command: The command name
            
        Returns:
            tuple: (command_type, duration_type)
        """
        try:
            # Try to load the skill file
            skill_file = f"skills/{command}.json"
            if os.path.exists(skill_file):
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill_data = json.load(f)
                
                command_type = skill_data.get('command_type', 'AutoPositionAction')
                duration_type = skill_data.get('duration_type', 'auto_stop')
                
                return command_type, duration_type
            else:
                # Default values if skill file doesn't exist
                self.logger.warning(f"Skill file not found: {skill_file}, using defaults")
                return 'AutoPositionAction', 'auto_stop'
                
        except Exception as e:
            self.logger.error(f"Error reading skill command info for {command}: {e}")
            return 'AutoPositionAction', 'auto_stop'

    def _execute_ezrobot_command(self, command: str, skill_name: str) -> bool:
        """
        Execute an EZ-Robot command via HTTP.
        
        Args:
            command: The command to execute (e.g., "wave", "sit", "kick")
            skill_name: Name of the skill for logging
            
        Returns:
            bool: True if command was sent successfully
        """
        # Add debugging for wave command
        if command.lower() == 'wave':
            self.logger.info(f"🔍 DEBUG: _execute_ezrobot_command called for wave")
            self.logger.info(f"🔍 DEBUG: EZ-Robot available: {self.ez_robot is not None}")
        
        if not self.ez_robot:
            self.logger.warning("EZ-Robot not available for command execution")
            return False
        
        # Add debugging for sit command
        if command.lower() in ["sit", "sit down"]:
            self.logger.info(f"🎤 DEBUG: Attempting to execute sit command: '{command}' for skill '{skill_name}'")
            self.logger.info(f"🎤 DEBUG: EZ-Robot available: {self.ez_robot is not None}")
            self.logger.info(f"🎤 DEBUG: Current body position: {getattr(self, 'current_body_position', 'unknown')}")
        
        try:
            # Map command to EZRobotSkills enum
            from ezrobot import EZRobotSkills
            
            # Create a mapping from command strings to enum values
            command_mapping = {
                "wave": EZRobotSkills.Wave,
                "walk": EZRobotSkills.Walk,
                "sit": EZRobotSkills.Sit_Down,
                "sit down": EZRobotSkills.Sit_Down,
                "stand": EZRobotSkills.Stand_From_Sit,
                "stand up": EZRobotSkills.Stand_From_Sit,
                "stop": EZRobotSkills.Stop,
                "kick": EZRobotSkills.Kick,
                "point": EZRobotSkills.Point,
                "bow": EZRobotSkills.Bow,
                "dance": EZRobotSkills.Dance,
                "disco dance": EZRobotSkills.Dance,
                "hands dance": EZRobotSkills.Dance,  # Map to general dance
                "predance": EZRobotSkills.Dance,      # Map to general dance
                "ymca dance": EZRobotSkills.Dance,    # Map to general dance
                "wiggle it": EZRobotSkills.Dance,
                "jump_jack": EZRobotSkills.Jump_Jack,
                "jump jack": EZRobotSkills.Jump_Jack,
                "a jump jack": EZRobotSkills.Jump_Jack,  # Handle "Do a jump jack" format
                "fly": EZRobotSkills.Fly,
                "getup": EZRobotSkills.Getup,
                "headstand": EZRobotSkills.Headstand,
                "pushups": EZRobotSkills.Pushups,
                "situps": EZRobotSkills.Situps,
                "somersault": EZRobotSkills.Summersault,
                "thinking": EZRobotSkills.Thinking,
                "sit_wave": EZRobotSkills.Sit_Wave,
                "sit wave": EZRobotSkills.Sit_Wave,  # Alternative format
                "head_bob": EZRobotSkills.Head_Bob,
                "head_no": EZRobotSkills.Head_No,
                "head_yes": EZRobotSkills.Head_Yes,
                "look_forward": EZRobotSkills.Look_Forward,
                "look_down": EZRobotSkills.Look_Down,
                "look_left": EZRobotSkills.Look_Left,
                "look_right": EZRobotSkills.Look_Right
            }
            
            # Try exact match first
            if command in command_mapping:
                skill_enum = command_mapping[command]
                
                # Add debugging for wave and sit commands
                if command.lower() == 'wave':
                    self.logger.info(f"🔍 DEBUG: Found wave command in mapping: '{command}' -> {skill_enum}")
                elif command.lower() in ["sit", "sit down"]:
                    self.logger.info(f"🎤 DEBUG: Found sit command in mapping: '{command}' -> {skill_enum}")
                
                # Coordinate eye expression with movement
                self.coordinate_eye_with_movement(command)
                
                # Get command type and duration type from skill file
                command_type, duration_type = self._get_skill_command_info(command)
                
                # Add debugging for sit command
                if command.lower() in ["sit", "sit down"]:
                    self.logger.info(f"🎤 DEBUG: Command type: {command_type}, Duration type: {duration_type}")
                
                # Execute command based on command type
                if command_type == "ScriptCollection":
                    if command == "head_no":
                        result = self.ez_robot.send_head_no()
                    elif command == "head_yes":
                        result = self.ez_robot.send_head_yes()
                    else:
                        # Use ScriptStartWait for Script Collection commands
                        result = self.ez_robot.send_script_wait(skill_enum)
                        
                        # Handle duration for 3000ms scripts
                        if duration_type == "3000ms":
                            self.logger.info(f"Script command {command} will run for 3000ms")
                        elif duration_type == "auto_stop":
                            self.logger.info(f"Script command {command} will stop automatically")
                else:
                    # AutoPositionAction commands
                    if command in ["disco dance", "disco_dance", "hands dance", "hands_dance", "predance", "ymca dance", "ymca_dance"]:
                        result = self._execute_dance_command(command)
                    else:
                        # All other actions use AutoPositionAction
                        result = self.ez_robot.send_auto_position(skill_enum)
                        
                        # Add debugging for sit command
                        if command.lower() in ["sit", "sit down"]:
                            self.logger.info(f"🎤 DEBUG: Sent AutoPositionAction command: {skill_enum}")
                            self.logger.info(f"🎤 DEBUG: Result: {result}")
                
                if result is not None:
                    # Add to pending actions for completion tracking
                    self.add_pending_action(command)
                    self._track_action_start(command)
                    
                    # Update body position based on command
                    self._update_body_position_from_command(command)
                    
                    # Add debugging for wave command
                    if command.lower() == 'wave':
                        self.logger.info(f"🔍 DEBUG: Wave command sent successfully: {command} -> {skill_enum.value}")
                    
                    self.logger.info(f"Sent EZ-Robot command: {command} -> {skill_enum.value} ({command_type}, {duration_type})")
                    return True
                else:
                    # Add debugging for wave command
                    if command.lower() == 'wave':
                        self.logger.warning(f"🔍 DEBUG: Wave command failed to send: {command}")
                    
                    self.logger.warning(f"Failed to send EZ-Robot command: {command}")
                    return False
            
            # Try partial matches
            for cmd, enum_val in command_mapping.items():
                if command in cmd or cmd in command:
                    # Get command type for partial matches
                    command_type, duration_type = self._get_skill_command_info(cmd)
                    
                    if command_type == "ScriptCollection":
                        result = self.ez_robot.send_script_wait(enum_val)
                    else:
                        result = self.ez_robot.send_auto_position(enum_val)
                        
                    if result is not None:
                        # Add to pending actions for completion tracking
                        self.add_pending_action(cmd)
                        self._track_action_start(cmd)
                        self.logger.info(f"Sent EZ-Robot command (partial match): {command} -> {enum_val.value} ({command_type}, {duration_type})")
                        return True
                    else:
                        self.logger.warning(f"Failed to send EZ-Robot command (partial match): {command} -> {enum_val.value}")
                        return False
            
            self.logger.warning(f"No EZ-Robot command mapping found for: {command}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing EZ-Robot command {command}: {e}")
            return False
    
    async def _update_skill_associations(self, action_context: Dict):
        """Update skill associations based on action execution."""
        try:
            skills_to_update = action_context.get('skill_requirements', [])
            
            for skill_name in skills_to_update:
                if skill_name in self.skills:
                    skill_file = f"skills/{skill_name}.json"
                    
                    # Load current skill data
                    with open(skill_file, 'r') as f:
                        skill_data = json.load(f)
                    
                    # Update associations
                    if "AssociatedGoals" not in skill_data:
                        skill_data["AssociatedGoals"] = []
                    
                    # Add goal alignments
                    for goal in action_context.get('goal_alignment', []):
                        if goal not in skill_data["AssociatedGoals"]:
                            skill_data["AssociatedGoals"].append(goal)
                    
                    # Add need associations
                    if "AssociatedNeeds" not in skill_data:
                        skill_data["AssociatedNeeds"] = []
                    
                    for need_satisfaction in action_context.get('need_satisfaction', []):
                        need = need_satisfaction['need']
                        if need not in skill_data["AssociatedNeeds"]:
                            skill_data["AssociatedNeeds"].append(need)
                    
                    # Update last used timestamp
                    skill_data["last_used"] = datetime.now().isoformat()
                    
                    # Save updated skill data
                    with open(skill_file, 'w') as f:
                        json.dump(skill_data, f, indent=4)
                    
                    self.logger.info(f"Updated skill associations for {skill_name}")
        
        except Exception as e:
            self.logger.error(f"Error updating skill associations: {e}")
    
    def _record_action_history(self, action_context: Dict, execution_result: Dict):
        """Record action execution in history for learning."""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "action_context": action_context,
                "execution_result": execution_result
            }
            self.action_history.append(history_entry)
            
            # Keep only last 100 entries
            if len(self.action_history) > 100:
                self.action_history = self.action_history[-100:]
                
        except Exception as e:
            self.logger.error(f"Error recording action history: {e}")
    
    def add_pending_action(self, action_name: str):
        """Add an action to the pending actions set."""
        self.pending_actions.add(action_name)
        self.logger.info(f"Added pending action: {action_name}")
    
    def remove_pending_action(self, action_name: str):
        """Remove an action from the pending actions set."""
        if action_name in self.pending_actions:
            self.pending_actions.remove(action_name)
            self.logger.info(f"Removed pending action: {action_name}")
    
    def has_pending_actions(self) -> bool:
        """Check if there are any pending EZ-Robot actions."""
        return len(self.pending_actions) > 0
    
    def get_pending_actions(self) -> List[str]:
        """Get list of currently pending actions."""
        return list(self.pending_actions)
    

    
    async def wait_for_action_completion(self, action_name: str, timeout: float = None):
        """
        Wait for a specific action to complete.
        
        Args:
            action_name: Name of the action to wait for
            timeout: Maximum time to wait in seconds (uses estimated completion time if None)
        """
        if not timeout:
            # Use estimated completion time for this action
            timeout = self.action_completion_times.get(action_name.lower(), 5.0)
        
        start_time = time.time()
        while action_name in self.pending_actions:
            if time.time() - start_time > timeout:
                self.logger.warning(f"Timeout waiting for action completion: {action_name}")
                # Remove from pending even if timeout
                self.remove_pending_action(action_name)
                break
            
            # Wait a short time before checking again
            await asyncio.sleep(0.1)
        
        self.logger.info(f"Action completed: {action_name}")
    
    async def wait_for_all_actions(self, timeout: float = 30.0):
        """
        Wait for all pending EZ-Robot actions to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        if not self.has_pending_actions():
            return
        
        start_time = time.time()
        pending_list = self.get_pending_actions()
        self.logger.info(f"Waiting for {len(pending_list)} pending actions to complete: {pending_list}")
        
        while self.has_pending_actions():
            if time.time() - start_time > timeout:
                self.logger.warning(f"Timeout waiting for all actions to complete. Remaining: {self.get_pending_actions()}")
                # Clear all pending actions on timeout
                self.pending_actions.clear()
                break
            
            # Wait a short time before checking again
            await asyncio.sleep(0.1)
        
        self.logger.info("All pending actions completed")
    
    def start_action_completion_tracker(self):
        """Start background task to track action completion times."""
        import threading
        
        def completion_tracker():
            """Background thread to track action completion times."""
            while True:
                try:
                    current_time = time.time()
                    actions_to_remove = []
                    
                    # Check each pending action
                    for action_name in self.pending_actions.copy():
                        # Get the estimated completion time for this action
                        estimated_time = self.action_completion_times.get(action_name.lower(), 5.0)
                        
                        # If we've tracked this action for longer than estimated time, mark it as complete
                        if hasattr(self, '_action_start_times') and action_name in self._action_start_times:
                            start_time = self._action_start_times[action_name]
                            if current_time - start_time >= estimated_time:
                                actions_to_remove.append(action_name)
                    
                    # Remove completed actions
                    for action_name in actions_to_remove:
                        self.remove_pending_action(action_name)
                        if hasattr(self, '_action_start_times'):
                            self._action_start_times.pop(action_name, None)
                    
                    # Sleep for a short time before next check
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error in action completion tracker: {e}")
                    time.sleep(1.0)
        
        # Start the background thread
        self.completion_tracker_thread = threading.Thread(target=completion_tracker, daemon=True)
        self.completion_tracker_thread.start()
        self.logger.info("Action completion tracker started")
    
    def _track_action_start(self, action_name: str):
        """Track when an action started for completion timing."""
        if not hasattr(self, '_action_start_times'):
            self._action_start_times = {}
        self._action_start_times[action_name] = time.time()
    
    def _initialize_body_position_tracking(self):
        """Initialize body position tracking system."""
        # Try to load last known position, otherwise default to standing
        last_position = self._load_last_position()
        if last_position:
            self.current_body_position = last_position["position"]
            self.body_position_history = last_position.get("history", [])
            self.logger.info(f"Restored last position: {self.current_body_position}")
        else:
            # Set initial position to standing for fresh startup
            self.update_body_position("standing")
            self.logger.info("Body position tracking initialized with default position: standing")
    
    def update_body_position(self, new_position: str):
        """Update CARL's current body position and maintain history."""
        timestamp = datetime.now().isoformat()
        
        # Add to history
        position_entry = {
            "position": new_position,
            "timestamp": timestamp
        }
        
        self.body_position_history.append(position_entry)
        
        # Keep only the last 7 positions
        if len(self.body_position_history) > self.max_position_history:
            self.body_position_history = self.body_position_history[-self.max_position_history:]
        
        # Update current position
        self.current_body_position = new_position
        
        # Save position to file for persistence
        self._save_last_position()
        
        # Save position to settings file
        self._save_position_to_settings(new_position)
        
        self.logger.info(f"Body position updated to: {new_position}")
    
    def get_current_body_position(self) -> str:
        """Get CARL's current body position."""
        return self.current_body_position
    
    def set_default_position(self, position: str):
        """Set the default body position for CARL."""
        self.current_body_position = position
        self._save_position_to_settings(position)
        self.logger.info(f"Default body position set to: {position}")
        self.logger.info(f"🔍 DEBUG: Position set via set_default_position - this should only happen during startup")
    
    def get_body_position_history(self) -> List[Dict]:
        """Get the last 7 body positions."""
        return self.body_position_history.copy()
    
    def is_in_position(self, position: str) -> bool:
        """Check if CARL is currently in a specific position."""
        return self.current_body_position.lower() == position.lower()
    
    def get_position_context_for_openai(self) -> str:
        """Get body position and direction context for OpenAI prompts."""
        position_context = ""
        direction_context = ""
        
        # Body position context
        if not self.body_position_history:
            position_context = "Body position: unknown"
        else:
            recent_positions = [entry["position"] for entry in self.body_position_history[-3:]]
            position_summary = ", ".join(recent_positions)
            position_context = f"Current body position: {self.current_body_position}. Recent positions: {position_summary}"
        
        # Direction context
        direction_context = self.get_direction_context_for_openai()
        
        return f"{position_context}\n{direction_context}"
    
    def _save_last_position(self):
        """Save current position to file for persistence across sessions."""
        try:
            import json
            position_data = {
                "position": self.current_body_position,
                "history": self.body_position_history,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.position_file, 'w') as f:
                json.dump(position_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save position: {e}")
    
    def _load_last_position(self):
        """Load last position from file."""
        try:
            import json
            import os
            if os.path.exists(self.position_file):
                with open(self.position_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load last position: {e}")
        return None
    
    def _load_position_from_settings(self):
        """Load position from settings file."""
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # Try to load from current settings first, then default
            settings_files = ['settings_current.ini', 'settings_default.ini']
            position_loaded = False
            
            for settings_file in settings_files:
                if os.path.exists(settings_file):
                    config.read(settings_file)
                    if 'position' in config:
                        current_pos = config.get('position', 'current_position', fallback='standing')
                        default_pos = config.get('position', 'default_position', fallback='standing')
                        
                        # Use current position if available, otherwise default
                        if current_pos and current_pos != 'unknown':
                            self.current_body_position = current_pos
                            self.logger.info(f"Loaded position from settings: {current_pos}")
                            position_loaded = True
                            break
                        elif default_pos and default_pos != 'unknown':
                            self.current_body_position = default_pos
                            self.logger.info(f"Loaded default position from settings: {default_pos}")
                            position_loaded = True
                            break
            
            if not position_loaded:
                self.current_body_position = "standing"
                self.logger.info("Using default position: standing")
                
        except Exception as e:
            self.logger.warning(f"Could not load position from settings: {e}")
            self.current_body_position = "standing"  # Default to standing
    
    def _save_position_to_settings(self, position: str):
        """Save current position to settings file."""
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # Load existing settings
            settings_file = 'settings_current.ini'
            if os.path.exists(settings_file):
                config.read(settings_file)
            
            # Ensure position section exists
            if 'position' not in config:
                config.add_section('position')
            
            # Update position
            config.set('position', 'current_position', position)
            
            # Write back to file
            with open(settings_file, 'w') as f:
                config.write(f)
            
            self.logger.info(f"Position saved to settings: {position}")
            
        except Exception as e:
            self.logger.warning(f"Could not save position to settings: {e}")

    def _initialize_direction_tracking(self):
        """Initialize direction tracking system."""
        # Try to load last known direction, otherwise default to north for fresh startup
        last_direction = self._load_last_direction()
        if last_direction:
            self.current_direction = last_direction["direction"]
            self.direction_history = last_direction.get("history", [])
            self.logger.info(f"Restored last direction: {self.current_direction}")
        else:
            # Set initial direction to north for fresh startup
            self.update_direction("north", "fresh_startup")
            self.logger.info("Direction tracking initialized with default direction: north (fresh startup)")

    def update_direction(self, new_direction: str, reason: str = "unknown"):
        """Update CARL's current direction and maintain history."""
        timestamp = datetime.now().isoformat()
        
        # Add to history
        direction_entry = {
            "direction": new_direction,
            "reason": reason,
            "timestamp": timestamp
        }
        
        self.direction_history.append(direction_entry)
        
        # Keep only the last 10 direction changes
        if len(self.direction_history) > self.max_direction_history:
            self.direction_history = self.direction_history[-self.max_direction_history:]
        
        # Update current direction
        self.current_direction = new_direction
        
        # Save direction to file for persistence
        self._save_last_direction()
        
        self.logger.info(f"Direction updated to: {new_direction} (reason: {reason})")

    def get_current_direction(self) -> str:
        """Get CARL's current direction."""
        return self.current_direction

    def get_direction_history(self) -> List[Dict]:
        """Get the last 10 direction changes."""
        return self.direction_history.copy()

    async def turn_direction(self, turn_command: str, duration: float = None) -> str:
        """Execute a physical turn and update direction accordingly."""
        turn_command = turn_command.lower()
        
        self.logger.info(f"🔄 Starting physical turn: {turn_command}")
        self.logger.info(f"🔍 DEBUG: Current direction before turn: {self.current_direction}")
        
        # Determine turn direction and new direction
        if turn_command in ["left", "turn_left"]:
            if self.current_direction is None:
                self.logger.warning("Cannot turn - no current direction set")
                return "north"  # Default fallback
            
            new_direction = self.direction_turns[self.current_direction]["left"]
            movement_direction = "left"
            action_name = "turn_left"
        elif turn_command in ["right", "turn_right"]:
            if self.current_direction is None:
                self.logger.warning("Cannot turn - no current direction set")
                return "north"  # Default fallback
            
            new_direction = self.direction_turns[self.current_direction]["right"]
            movement_direction = "right"
            action_name = "turn_right"
        else:
            self.logger.warning(f"Unknown turn command: {turn_command}")
            return self.current_direction
        
        # Get turn duration (use provided duration or default from completion times)
        if duration is None:
            duration = self.action_completion_times.get(action_name, 6.0)  # Q4: 6 seconds minimum for 90-degree turn
        
        # Enforce 6-second minimum duration for 90-degree movement
        if duration < 6.0:
            self.logger.info(f"⚠️ Turn duration {duration}s is less than 6s minimum, enforcing 6s minimum")
            duration = 6.0
        
        self.logger.info(f"🔄 Executing physical turn: {movement_direction} for {duration} seconds")
        
        # Log start time for turn movement
        import time
        turn_start_time = time.time()
        self.logger.info(f"⏰ Turn movement started at: {time.strftime('%H:%M:%S', time.localtime(turn_start_time))}")
        
        try:
            # Send movement command to EZ-Robot using send_movement function
            movement_success = self.send_movement(movement_direction)
            
            if movement_success:
                # Add to pending actions for tracking
                self.add_pending_action(action_name)
                self._track_action_start(action_name)
                
                # Wait for estimated duration
                self.logger.info(f"⏳ Waiting {duration} seconds for turn to complete...")
                await asyncio.sleep(duration)
                
                # Log end time for turn movement
                turn_end_time = time.time()
                actual_duration = turn_end_time - turn_start_time
                self.logger.info(f"⏰ Turn movement ended at: {time.strftime('%H:%M:%S', time.localtime(turn_end_time))}")
                self.logger.info(f"⏱️ Actual turn duration: {actual_duration:.2f}s (expected: {duration}s)")
                
                # Send stop command
                self.logger.info(f"🛑 Sending stop command")
                stop_success = self.send_movement("stop")
                
                if stop_success:
                    self.logger.info(f"✅ Stop command sent successfully")
                    
                    # Remove from pending actions
                    self.remove_pending_action(action_name)
                    
                    # Update direction state only after physical turn completes
                    old_direction = self.current_direction
                    self.update_direction(new_direction, action_name)
                    self.log_direction_movement(action_name, f"Physically turned from {old_direction} to {new_direction}")
                    self.logger.info(f"✅ Physical turn completed: {old_direction} -> {new_direction}")
                    return new_direction
                else:
                    self.logger.warning(f"⚠️ Stop command failed")
                    self.remove_pending_action(action_name)
                    return self.current_direction
            else:
                self.logger.error(f"❌ Physical turn failed: {movement_direction}")
                return self.current_direction
                
        except Exception as e:
            self.logger.error(f"❌ Error executing physical turn: {e}")
            return self.current_direction
    
    def send_movement(self, direction: str) -> bool:
        """Send movement command to EZ-Robot via HTTP API."""
        try:
            # Construct movement URL
            movement_url = f"http://192.168.56.1/movement?direction={direction}"
            
            self.logger.info(f"🌐 Sending movement command: {movement_url}")
            
            # Send movement command
            import requests
            response = requests.get(movement_url, timeout=5.0)
            
            if response.status_code == 200:
                self.logger.info(f"✅ Movement command sent successfully: {direction}")
                return True
            else:
                self.logger.error(f"❌ Movement command failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error sending movement command: {e}")
            return False

    async def _execute_physical_turn(self, direction: str, duration: float) -> bool:
        """Execute physical turn movement via EZ-Robot HTTP API."""
        try:
            # Send movement command using send_movement function
            movement_success = self.send_movement(direction)
            
            if movement_success:
                # Add to pending actions for tracking
                self.add_pending_action(f"turn_{direction}")
                self._track_action_start(f"turn_{direction}")
                
                # Wait for estimated duration
                self.logger.info(f"⏳ Waiting {duration} seconds for turn to complete...")
                await asyncio.sleep(duration)
                
                # Send stop command
                self.logger.info(f"🛑 Sending stop command")
                stop_success = self.send_movement("stop")
                
                if stop_success:
                    self.logger.info(f"✅ Stop command sent successfully")
                    
                    # Remove from pending actions
                    self.remove_pending_action(f"turn_{direction}")
                    
                    return True
                else:
                    self.logger.warning(f"⚠️ Stop command failed")
                    self.remove_pending_action(f"turn_{direction}")
                    return False
            else:
                self.logger.error(f"❌ Movement command failed: {direction}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error executing physical turn: {e}")
            return False

    def _parse_turn_command(self, command: str) -> tuple:
        """Parse turn command to extract direction and optional duration."""
        try:
            command_lower = command.lower()
            
            # Extract direction
            direction = None
            if "turn left" in command_lower or "left" in command_lower:
                direction = "left"
            elif "turn right" in command_lower or "right" in command_lower:
                direction = "right"
            
            # Extract duration (look for patterns like "for X seconds" or "X seconds")
            duration = None
            import re
            
            # Pattern 1: "for X seconds"
            duration_match = re.search(r'for (\d+(?:\.\d+)?) seconds?', command_lower)
            if duration_match:
                duration = float(duration_match.group(1))
            
            # Pattern 2: "X seconds" (without "for")
            if duration is None:
                duration_match = re.search(r'(\d+(?:\.\d+)?) seconds?', command_lower)
                if duration_match:
                    duration = float(duration_match.group(1))
            
            # Pattern 3: "90 degrees" - assume 6 seconds for 90 degrees
            if duration is None and "90 degrees" in command_lower:
                duration = 6.0
            
            return direction, duration
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing turn command: {e}")
            return None, None
    
    async def _execute_turn_command(self, command: str) -> bool:
        """Execute turn command with parsed direction and duration."""
        try:
            direction, duration = self._parse_turn_command(command)
            
            if direction is None:
                self.logger.warning(f"Could not parse turn direction from: {command}")
                return False
            
            self.logger.info(f"🔄 Parsed turn command: direction={direction}, duration={duration}")
            
            # Execute the turn
            if hasattr(self, 'loop') and self.loop:
                # Use existing event loop
                future = asyncio.run_coroutine_threadsafe(
                    self.turn_direction(direction, duration), 
                    self.loop
                )
                result = future.result(timeout=30.0)  # 30 second timeout
                return result is not None
            else:
                # Fix: Use proper async execution instead of asyncio.run() in running event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, create a task
                        task = asyncio.create_task(self.turn_direction(direction, duration))
                        result = await task
                        return result is not None
                    else:
                        # No running loop, create new one
                        return asyncio.run(self.turn_direction(direction, duration)) is not None
                except RuntimeError:
                    # Fallback: create new event loop
                    return asyncio.run(self.turn_direction(direction, duration)) is not None
                
        except Exception as e:
            self.logger.error(f"❌ Error executing turn command: {e}")
            return False

    def get_direction_context_for_openai(self) -> str:
        """Get direction context for OpenAI prompts."""
        if not self.direction_history:
            return "Direction: north (fresh startup)"
        
        # Get recent direction changes
        recent_directions = [entry["direction"] for entry in self.direction_history[-3:]]
        direction_summary = ", ".join(recent_directions)
        
        return f"Current direction: {self.current_direction}. Recent directions: {direction_summary}"
    
    def get_direction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive direction tracking statistics."""
        try:
            stats = {
                "current_direction": self.current_direction,
                "total_direction_changes": len(self.direction_history),
                "direction_history": self.direction_history[-10:],  # Last 10 changes
                "most_common_direction": None,
                "direction_patterns": [],
                "session_start_time": None,
                "average_time_between_changes": None
            }
            
            if self.direction_history:
                # Calculate most common direction
                direction_counts = {}
                for entry in self.direction_history:
                    direction = entry["direction"]
                    direction_counts[direction] = direction_counts.get(direction, 0) + 1
                
                if direction_counts:
                    stats["most_common_direction"] = max(direction_counts, key=direction_counts.get)
                
                # Calculate time patterns
                if len(self.direction_history) > 1:
                    timestamps = [entry["timestamp"] for entry in self.direction_history]
                    time_diffs = []
                    for i in range(1, len(timestamps)):
                        try:
                            from datetime import datetime
                            t1 = datetime.fromisoformat(timestamps[i-1])
                            t2 = datetime.fromisoformat(timestamps[i])
                            diff = (t2 - t1).total_seconds()
                            time_diffs.append(diff)
                        except:
                            pass
                    
                    if time_diffs:
                        stats["average_time_between_changes"] = sum(time_diffs) / len(time_diffs)
                
                # Identify direction patterns
                if len(self.direction_history) >= 3:
                    for i in range(len(self.direction_history) - 2):
                        pattern = [
                            self.direction_history[i]["direction"],
                            self.direction_history[i+1]["direction"],
                            self.direction_history[i+2]["direction"]
                        ]
                        stats["direction_patterns"].append(pattern)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting direction statistics: {e}")
            return {"error": str(e)}
    
    def log_direction_movement(self, movement_type: str, details: str = ""):
        """Log detailed movement information for analysis."""
        try:
            movement_log = {
                "timestamp": datetime.now().isoformat(),
                "movement_type": movement_type,
                "current_direction": self.current_direction,
                "details": details,
                "body_position": self.current_body_position
            }
            
            # Save to movement log file
            movement_log_file = "movement_log.json"
            try:
                import json
                import os
                
                # Load existing log or create new one
                if os.path.exists(movement_log_file):
                    with open(movement_log_file, 'r') as f:
                        log_data = json.load(f)
                else:
                    log_data = {"movements": []}
                
                # Add new movement
                log_data["movements"].append(movement_log)
                
                # Keep only last 100 movements
                if len(log_data["movements"]) > 100:
                    log_data["movements"] = log_data["movements"][-100:]
                
                # Save updated log
                with open(movement_log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                    
            except Exception as e:
                self.logger.warning(f"Could not save movement log: {e}")
            
            # Log to console
            self.logger.info(f"🎯 Movement: {movement_type} - Direction: {self.current_direction} - {details}")
            
        except Exception as e:
            self.logger.error(f"Error logging movement: {e}")
    
    def get_movement_analysis(self) -> Dict[str, Any]:
        """Analyze movement patterns and provide insights."""
        try:
            analysis = {
                "total_movements": 0,
                "movement_types": {},
                "direction_preferences": {},
                "activity_patterns": [],
                "recommendations": []
            }
            
            # Load movement log
            movement_log_file = "movement_log.json"
            if os.path.exists(movement_log_file):
                with open(movement_log_file, 'r') as f:
                    log_data = json.load(f)
                
                movements = log_data.get("movements", [])
                analysis["total_movements"] = len(movements)
                
                # Analyze movement types
                for movement in movements:
                    movement_type = movement.get("movement_type", "unknown")
                    analysis["movement_types"][movement_type] = analysis["movement_types"].get(movement_type, 0) + 1
                
                # Analyze direction preferences
                for movement in movements:
                    direction = movement.get("current_direction", "unknown")
                    analysis["direction_preferences"][direction] = analysis["direction_preferences"].get(direction, 0) + 1
                
                # Generate recommendations
                if analysis["total_movements"] > 0:
                    most_common_movement = max(analysis["movement_types"], key=analysis["movement_types"].get)
                    most_common_direction = max(analysis["direction_preferences"], key=analysis["direction_preferences"].get)
                    
                    analysis["recommendations"].append(f"Most common movement: {most_common_movement}")
                    analysis["recommendations"].append(f"Preferred direction: {most_common_direction}")
                    
                    if analysis["total_movements"] < 10:
                        analysis["recommendations"].append("More movement data needed for comprehensive analysis")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing movements: {e}")
            return {"error": str(e)}

    def _save_last_direction(self):
        """Save current direction to file for persistence across sessions."""
        try:
            import json
            direction_data = {
                "direction": self.current_direction,
                "history": self.direction_history,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.direction_file, 'w') as f:
                json.dump(direction_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save direction: {e}")

    def _load_last_direction(self):
        """Load last direction from file."""
        try:
            import json
            import os
            if os.path.exists(self.direction_file):
                with open(self.direction_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load last direction: {e}")
        return None
    
    def resume_last_pose(self):
        """Resume CARL's last pose if he has previous memories."""
        try:
            # Check if there are memories (indicating CARL has previous session data)
            memories_dir = "memories"
            has_memories = False
            
            if os.path.exists(memories_dir):
                memory_files = [f for f in os.listdir(memories_dir) if f.endswith('.json')]
                has_memories = len(memory_files) > 0
            
            if has_memories and self.current_body_position != "unknown":
                self.logger.info(f"🤖 Resuming last pose: {self.current_body_position}")
                
                # Execute the pose command if EZ-Robot is available
                if self.ez_robot:
                    if self.current_body_position == "sitting":
                        from ezrobot import EZRobotSkills
                        self.ez_robot.send_auto_position(EZRobotSkills.Sit_Down)
                        self.logger.info("✅ Resumed sitting position")
                    elif self.current_body_position == "standing":
                        # Don't execute anything since CARL always starts physically standing
                        # set up by the end user
                        self.logger.info("ℹ️ CARL is already standing (default position) - no action needed")
                    
                    return True
                else:
                    self.logger.warning("⚠️ EZ-Robot not available - cannot resume physical pose")
            else:
                if not has_memories:
                    self.logger.info("ℹ️ No previous memories found - starting fresh")
                else:
                    self.logger.info("ℹ️ No previous pose to resume")
                    
        except Exception as e:
            self.logger.error(f"❌ Error resuming last pose: {e}")
        
        return False
    
    def check_prerequisite_pose(self, skill_name: str) -> Tuple[bool, str]:
        """
        Check if a skill can be executed based on prerequisite pose requirements.
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            Tuple of (can_execute, reasoning)
        """
        current_position = self.position_system.current_position
        
        # Load skill data to check prerequisite_pose
        skills_dir = "skills"
        skill_file = os.path.join(skills_dir, f"{skill_name}.json")
        
        if os.path.exists(skill_file):
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill_data = json.load(f)
                
                prerequisite_pose = skill_data.get("prerequisite_pose", "any")
                
                if prerequisite_pose == "any":
                    return True, f"Skill '{skill_name}' can be executed from any position"
                
                if prerequisite_pose == current_position:
                    return True, f"Skill '{skill_name}' requires {prerequisite_pose} and I am {current_position}"
                
                return False, f"Skill '{skill_name}' requires {prerequisite_pose} but I am {current_position}"
                
            except Exception as e:
                self.logger.warning(f"Error checking prerequisite pose for {skill_name}: {e}")
                return True, f"Could not determine prerequisite pose for {skill_name}, allowing execution"
        
        # If skill file doesn't exist, allow execution (backward compatibility)
        return True, f"Skill file for '{skill_name}' not found, allowing execution"
    
    def should_execute_position_command(self, command: str) -> Tuple[bool, str]:
        """
        Determine if a position command should be executed or if CARL should respond intelligently.
        
        Returns:
            Tuple[bool, str]: (should_execute, reasoning)
        """
        command_lower = command.lower()
        
        # Position commands that change body state
        position_commands = {
            "sit": "sitting",
            "sit down": "sitting", 
            "stand": "standing",
            "stand up": "standing",
            "lie down": "lying",
            "get up": "standing"
        }
        
        for cmd, target_position in position_commands.items():
            if cmd in command_lower:
                if self.is_in_position(target_position):
                    # Enhanced logic: Allow sit commands even when already sitting if explicitly requested
                    if cmd in ["sit", "sit down"]:
                        reasoning = f"I am already {target_position}, but I'll execute the sit command as requested."
                        return True, reasoning
                    else:
                        # For other position commands, respond intelligently
                        reasoning = f"I am already {target_position}. I should respond intelligently instead of repeating the action."
                        return False, reasoning
                else:
                    # Need to change position
                    reasoning = f"I am currently {self.position_system.current_position} and need to {target_position}."
                    return True, reasoning
        
        # Non-position commands should always execute
        return True, "This is not a position command."
    
    def is_in_position(self, target_position: str) -> bool:
        """Check if CARL is currently in the specified position."""
        return self.position_system.current_position == target_position
    
    def set_eye_expression(self, emotion: str):
        """Set eye expression based on emotional state."""
        if not self.ez_robot:
            self.logger.warning("EZ-Robot not available for eye expression")
            return False
        
        try:
            result = self.ez_robot.set_eye_expression(emotion)
            if result is not None:
                self.logger.info(f"Set eye expression: {emotion}")
                return True
            else:
                self.logger.warning(f"Failed to set eye expression: {emotion}")
                return False
        except Exception as e:
            self.logger.error(f"Error setting eye expression {emotion}: {e}")
            return False

    def coordinate_eye_with_movement(self, movement: str, emotion: str = None):
        """Coordinate eye expressions with body movements for human-like behavior."""
        if not self.ez_robot:
            return False
        
        try:
            # Map movements to appropriate eye expressions
            movement_to_eye = {
                "look_down": "eyes_down",
                "look_up": "eyes_up", 
                "look_left": "eyes_left",
                "look_right": "eyes_right",
                "head_no": "eyes_closed",  # Close eyes during head shake
                "head_yes": "eyes_open"    # Keep eyes open during head nod
            }
            
            # Determine eye expression
            eye_expression = None
            if emotion:
                # Use emotional expression if provided
                eye_expression = emotion
            elif movement in movement_to_eye:
                # Use movement-specific eye expression
                eye_expression = movement_to_eye[movement]
            else:
                # Default to open eyes
                eye_expression = "eyes_open"
            
            # Set the eye expression
            return self.set_eye_expression(eye_expression)
            
        except Exception as e:
            self.logger.error(f"Error coordinating eye with movement {movement}: {e}")
            return False

    def get_action_statistics(self) -> Dict:
        """Get statistics about action execution."""
        stats = {
            "total_actions": 0,
            "action_types": {},
            "success_rate": 0.0,
            "average_execution_time": 0.0,
            "most_used_skills": {},
            "emotional_expressions": {}
        }
        
        if not self.action_history:
            return stats
        
        stats["total_actions"] = len(self.action_history)
        successful_actions = 0
        total_execution_time = 0.0
        
        for entry in self.action_history:
            # Count action types
            action_type = entry["action_context"].get("action_type")
            if action_type:
                # Handle both enum and string types
                if hasattr(action_type, 'value'):
                    action_type_str = action_type.value
                else:
                    action_type_str = str(action_type)
                stats["action_types"][action_type_str] = stats["action_types"].get(action_type_str, 0) + 1
            
            # Count successful actions
            if entry["execution_result"]["successful_actions"]:
                successful_actions += 1
            
            # Sum execution time
            total_execution_time += entry["execution_result"]["execution_time"]
            
            # Count skills used
            for skill in entry["action_context"].get("skill_requirements", []):
                stats["most_used_skills"][skill] = stats["most_used_skills"].get(skill, 0) + 1
            
            # Count emotional expressions
            expression = entry["execution_result"].get("emotional_expression_applied")
            if expression:
                stats["emotional_expressions"][expression] = stats["emotional_expressions"].get(expression, 0) + 1
        
        # Calculate averages
        if stats["total_actions"] > 0:
            stats["success_rate"] = successful_actions / stats["total_actions"]
            stats["average_execution_time"] = total_execution_time / stats["total_actions"]
        
        return stats
    
    def create_missing_skills(self):
        """Create missing skill files for EZ-Robot commands and body movement reactions."""
        missing_skills = []
        
        # Check for missing EZ-Robot command skills
        for command_name in self.ez_commands.keys():
            skill_file = f"skills/{command_name}.json"
            if not os.path.exists(skill_file):
                missing_skills.append(command_name)
        
        # Check for missing body movement reaction skills
        body_movement_skills = [
            "reaction_amazed",
            "reaction_terrified", 
            "reaction_ecstatic",
            "reaction_amused",
            "reaction_irritated"
        ]
        
        for skill_name in body_movement_skills:
            skill_file = f"skills/{skill_name}.json"
            if not os.path.exists(skill_file):
                missing_skills.append(skill_name)
        
        # Create missing skills
        for skill_name in missing_skills:
            if skill_name in body_movement_skills:
                self._create_body_movement_skill_file(skill_name)
            else:
                self._create_skill_file(skill_name)
    
    def _create_skill_file(self, skill_name: str):
        """Create a new skill file with learning system integration."""
        # Determine command type and duration type
        script_commands_3000ms = ["walk", "look_forward", "look_down", "head_yes", "head_no", "yawn"]
        script_commands_auto_stop = ["arm_right_down", "arm_right_down_sitting", "point_arm_right", "Waiting Fidget"]
        
        if skill_name in script_commands_3000ms:
            command_type = "ScriptCollection"
            duration_type = "3000ms"
        elif skill_name in script_commands_auto_stop:
            command_type = "ScriptCollection"
            duration_type = "auto_stop"
        else:
            command_type = "AutoPositionAction"
            duration_type = "auto_stop"
        
        # Determine prerequisite pose based on skill type
        pose_requirements = {
            "sit_wave": "sitting",
            "walk": "standing",
            "dance": "standing",
            "wave": "standing",
            "bow": "standing",
            "kick": "standing",
            "point": "standing",
            "head_yes": "any",
            "head_no": "any",
            "talk": "any",
            "greet": "any"
        }
        
        prerequisite_pose = pose_requirements.get(skill_name, "any")
        
        # Load skill template if available, otherwise create basic structure
        skill_template = self._load_skill_template()
        
        skill_data = {
            "Name": skill_name,
            "Concepts": self._get_concepts_for_skill(skill_name),
            "Motivators": self._get_motivators_for_skill(skill_name),
            "Techniques": [f"EZRobot-cmd-{skill_name}"],
            "IsUsedInNeeds": False,
            "AssociatedGoals": [],
            "AssociatedNeeds": [],
            "created": datetime.now().isoformat(),
            "last_used": None,
            "command_type": command_type,
            "duration_type": duration_type,
            "command_type_updated": datetime.now().isoformat(),
            "activation_keywords": self._get_activation_keywords_for_skill(skill_name),
            "keywords_updated": datetime.now().isoformat(),
            "prerequisite_pose": prerequisite_pose,
            "prerequisite_pose_updated": datetime.now().isoformat(),
            "Learning_System": skill_template.get("Learning_System", self._create_default_learning_system())
        }
        
        skill_file = f"skills/{skill_name}.json"
        os.makedirs('skills', exist_ok=True)
        
        with open(skill_file, 'w') as f:
            json.dump(skill_data, f, indent=4)
        
        self.logger.info(f"Created skill file: {skill_file} ({command_type}, {duration_type})")
    
    def _create_body_movement_skill_file(self, skill_name: str):
        """Create a new body movement reaction skill file with full configuration."""
        from datetime import datetime
        
        # Define skill configurations for each body movement reaction
        skill_configs = {
            "reaction_amazed": {
                "concepts": ["amazement", "surprise", "wonder", "astonishment", "body_reaction"],
                "motivators": ["express_emotion", "react_to_stimulus", "show_surprise", "communicate_feeling"],
                "techniques": ["ARC-ScriptCollection-reaction_amazed", "coordinated_movement", "emotional_expression"],
                "emotional_triggers": {
                    "primary_emotions": ["surprise"],
                    "sub_emotions": ["amazed", "startled"],
                    "intensity_threshold": 0.5,
                    "neurotransmitter_triggers": {
                        "dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.4
                    }
                },
                "coordination": {
                    "eyes": "eyes_surprise",
                    "timing": "simultaneous",
                    "body_synchronization": True
                },
                "duration": 2000,
                "priority": "HIGH"
            },
            "reaction_terrified": {
                "concepts": ["terror", "fear", "panic", "anxiety", "body_reaction"],
                "motivators": ["express_emotion", "react_to_threat", "show_fear", "communicate_danger"],
                "techniques": ["ARC-ScriptCollection-reaction_terrified", "coordinated_movement", "emotional_expression"],
                "emotional_triggers": {
                    "primary_emotions": ["fear"],
                    "sub_emotions": ["scared"],
                    "intensity_threshold": 0.6,
                    "neurotransmitter_triggers": {
                        "dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.5
                    }
                },
                "coordination": {
                    "eyes": "eyes_sad",
                    "timing": "simultaneous",
                    "body_synchronization": True
                },
                "duration": 2500,
                "priority": "HIGH"
            },
            "reaction_ecstatic": {
                "concepts": ["ecstasy", "extreme_joy", "elation", "thrill", "body_reaction"],
                "motivators": ["express_emotion", "show_joy", "celebrate", "communicate_happiness"],
                "techniques": ["ARC-ScriptCollection-reaction_ecstatic", "coordinated_movement", "emotional_expression"],
                "emotional_triggers": {
                    "primary_emotions": ["happiness"],
                    "sub_emotions": ["joyful"],
                    "intensity_threshold": 0.7,
                    "neurotransmitter_triggers": {
                        "dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2
                    }
                },
                "coordination": {
                    "eyes": "eyes_surprise",
                    "timing": "simultaneous",
                    "body_synchronization": True
                },
                "duration": 3000,
                "priority": "HIGH"
            },
            "reaction_amused": {
                "concepts": ["amusement", "light_joy", "pleasure", "entertainment", "body_reaction"],
                "motivators": ["express_emotion", "show_amusement", "react_to_humor", "communicate_pleasure"],
                "techniques": ["ARC-ScriptCollection-reaction_amused", "coordinated_movement", "emotional_expression"],
                "emotional_triggers": {
                    "primary_emotions": ["happiness"],
                    "sub_emotions": ["amused"],
                    "intensity_threshold": 0.4,
                    "neurotransmitter_triggers": {
                        "dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1
                    }
                },
                "coordination": {
                    "eyes": "eyes_joy",
                    "timing": "simultaneous",
                    "body_synchronization": True
                },
                "duration": 1800,
                "priority": "MEDIUM"
            },
            "reaction_irritated": {
                "concepts": ["irritation", "anger", "frustration", "annoyance", "body_reaction"],
                "motivators": ["express_emotion", "show_frustration", "react_to_annoyance", "communicate_displeasure"],
                "techniques": ["ARC-ScriptCollection-reaction_irritated", "coordinated_movement", "emotional_expression"],
                "emotional_triggers": {
                    "primary_emotions": ["anger"],
                    "sub_emotions": ["frustrated"],
                    "intensity_threshold": 0.4,
                    "neurotransmitter_triggers": {
                        "dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3
                    }
                },
                "coordination": {
                    "eyes": "eyes_sad",
                    "timing": "simultaneous",
                    "body_synchronization": True
                },
                "duration": 2200,
                "priority": "MEDIUM"
            }
        }
        
        config = skill_configs.get(skill_name)
        if not config:
            self.logger.warning(f"Unknown body movement skill: {skill_name}")
            return
        
        # Create skill data structure
        skill_data = {
            "Name": skill_name,
            "Concepts": config["concepts"],
            "Motivators": config["motivators"],
            "Techniques": config["techniques"],
            "script_collection": {
                "script_name": skill_name,
                "execution_type": "body_movement",
                "coordination": config["coordination"]
            },
            "emotional_triggers": config["emotional_triggers"],
            "execution_parameters": {
                "duration": config["duration"],
                "cooldown": 5.0,
                "priority": config["priority"],
                "interruptible": False
            },
            "body_movement_details": {
                "movement_type": "reactive" if "amazed" in skill_name else "defensive" if "terrified" in skill_name else "celebratory" if "ecstatic" in skill_name else "light" if "amused" in skill_name else "agitated",
                "body_parts": ["head", "arms", "torso"],
                "movement_intensity": "moderate" if "amazed" in skill_name else "high" if "terrified" in skill_name or "ecstatic" in skill_name else "low",
                "recovery_time": 1.5 if "amazed" in skill_name else 2.0 if "terrified" in skill_name else 2.5 if "ecstatic" in skill_name else 1.0 if "amused" in skill_name else 1.8
            },
            "learning_integration": {
                "skill_progression": {
                    "current_level": "basic_execution",
                    "mastery_threshold": 0.8,
                    "learning_rate": 0.15
                },
                "context_learning": {
                    "situational_triggers": self._get_situational_triggers_for_skill(skill_name),
                    "environmental_factors": self._get_environmental_factors_for_skill(skill_name)
                }
            },
            "created": datetime.now().isoformat(),
            "command_type": "ScriptCollection",
            "duration_type": f"{config['duration']}ms",
            "command_type_updated": datetime.now().isoformat(),
            "Learning_System": {
                "strategy": "emotional_expression",
                "enabled": True,
                "learning_rate": 0.15,
                "retention_factor": 0.9
            },
            "IsUsedInNeeds": True,
            "AssociatedGoals": ["express_emotions", "react_to_environment", "maintain_emotional_balance"],
            "last_updated": datetime.now().isoformat()
        }
        
        # Create skills directory if it doesn't exist
        os.makedirs('skills', exist_ok=True)
        
        # Write skill file
        skill_file = f"skills/{skill_name}.json"
        with open(skill_file, 'w', encoding='utf-8') as f:
            json.dump(skill_data, f, indent=2)
        
        self.logger.info(f"Created body movement skill file: {skill_file}")
    
    def _get_situational_triggers_for_skill(self, skill_name: str) -> list:
        """Get situational triggers for a body movement skill."""
        triggers = {
            "reaction_amazed": ["unexpected_events", "new_discoveries", "surprising_information"],
            "reaction_terrified": ["threatening_events", "sudden_dangers", "unexpected_threats"],
            "reaction_ecstatic": ["achievements", "pleasant_surprises", "successful_outcomes"],
            "reaction_amused": ["humor", "pleasant_interactions", "entertaining_content"],
            "reaction_irritated": ["frustrating_events", "annoying_situations", "irritating_interactions"]
        }
        return triggers.get(skill_name, [])
    
    def _get_environmental_factors_for_skill(self, skill_name: str) -> list:
        """Get environmental factors for a body movement skill."""
        factors = {
            "reaction_amazed": ["bright_lights", "sudden_sounds", "unusual_objects"],
            "reaction_terrified": ["loud_noises", "dark_spaces", "unknown_objects"],
            "reaction_ecstatic": ["positive_events", "rewarding_experiences", "joyful_moments"],
            "reaction_amused": ["funny_situations", "positive_company", "amusing_events"],
            "reaction_irritated": ["repetitive_tasks", "unpleasant_conditions", "conflicting_demands"]
        }
        return factors.get(skill_name, [])
    
    def _load_skill_template(self) -> dict:
        """Load the skill template for creating new skills."""
        template_path = "skills/skill_template.json"
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load skill template: {e}")
        
        # Return empty dict if template not available
        return {}
    
    def _create_default_learning_system(self) -> dict:
        """Create a default learning system structure for skills."""
        return {
            "skill_progression": {
                "current_level": "beginner",
                "level_progress": 0.0,
                "mastery_threshold": 0.8,
                "progression_stages": [
                    "beginner",
                    "intermediate",
                    "advanced",
                    "expert"
                ]
            },
            "feedback_system": {
                "self_assessment": {
                    "execution_quality": 0.0,
                    "confidence_level": 0.0,
                    "enjoyment_level": 0.0
                },
                "external_feedback": {
                    "user_satisfaction": 0.0,
                    "performance_rating": 0.0
                }
            },
            "learning_principles": {
                "active_learning": {
                    "interleaving": {
                        "enabled": True,
                        "mixing_ratio": 0.3
                    },
                    "retrieval_practice": {
                        "enabled": True,
                        "success_threshold": 0.7
                    }
                },
                "information_processing": {
                    "dual_coding": {
                        "visual_components": [],
                        "verbal_components": []
                    },
                    "spaced_repetition": {
                        "next_review": "",
                        "review_interval": 1.0
                    },
                    "working_memory": {
                        "capacity_used": 0.0,
                        "chunking_strategy": "none"
                    }
                },
                "learning_styles": {
                    "visual": 0.0,
                    "auditory": 0.0,
                    "kinesthetic": 0.0,
                    "social": 0.0,
                    "multimodal": 1.0
                },
                "neurological_basis": {
                    "action_prediction_error": {
                        "repetition_count": 0,
                        "error_rate": 0.1,
                        "improvement_rate": 0.0
                    },
                    "reward_prediction_error": {
                        "expected_reward": 0.5,
                        "actual_reward": 0.0,
                        "learning_rate": 0.1
                    },
                    "habit_formation": {
                        "automaticity_level": 0.0,
                        "habit_strength": 0.0
                    }
                }
            },
            "adaptive_learning": {
                "difficulty_adjustment": {
                    "current_challenge": 0.5,
                    "success_rate": 0.5,
                    "adjustment_factor": 1.0
                },
                "personalization": {
                    "learning_style": "multimodal",
                    "preference_adaptation": 0.5,
                    "motivation_factors": []
                }
            }
        }
    
    def _get_concepts_for_skill(self, skill_name: str) -> List[str]:
        """Get relevant concepts for a skill."""
        concept_mapping = {
            "walk": ["movement", "locomotion", "travel"],
            "yawn": ["tired", "bored", "rest"],
            "wave": ["greeting", "communication", "gesture"],
            "talk": ["communication", "language", "speech"],
            "bow": ["respect", "greeting", "formality"],
            "sit": ["rest", "position", "comfort"],
            "stand": ["position", "readiness", "attention"],
            "kick": ["movement", "action", "physical"],
            "point": ["direction", "indication", "gesture"],
            "headstand": ["balance", "skill", "acrobatics"],
            "somersault": ["movement", "acrobatics", "play"],
            "pushups": ["exercise", "strength", "fitness"],
            "situps": ["exercise", "core", "fitness"],
            "fly": ["movement", "acrobatics", "skill"],
            "getup": ["movement", "recovery", "position"],
            "thinking": ["cognition", "reflection", "processing"]
        }
        
        return concept_mapping.get(skill_name, [skill_name])
    
    def _get_motivators_for_skill(self, skill_name: str) -> List[str]:
        """Get motivators for a skill."""
        motivator_mapping = {
            "walk": ["move", "travel", "explore"],
            "yawn": ["tired", "bored", "sleepy"],
            "wave": ["greet", "hello", "goodbye", "acknowledge"],
            "talk": ["communicate", "express", "share"],
            "bow": ["respect", "greet", "acknowledge"],
            "sit": ["rest", "relax", "position"],
            "stand": ["ready", "attention", "position"],
            "kick": ["play", "exercise", "demonstrate"],
            "point": ["indicate", "direct", "show"],
            "headstand": ["demonstrate", "show_skill", "impress"],
            "somersault": ["play", "demonstrate", "have_fun"],
            "pushups": ["exercise", "demonstrate", "show_strength"],
            "situps": ["exercise", "demonstrate", "show_fitness"],
            "fly": ["demonstrate", "show_skill", "impress"],
            "getup": ["recover", "position", "ready"],
            "thinking": ["process", "reflect", "consider"]
        }
        
        return motivator_mapping.get(skill_name, [skill_name]) 
    
    def _get_activation_keywords_for_skill(self, skill_name: str) -> List[str]:
        """Get activation keywords for a skill."""
        activation_keywords_mapping = {
            "sit": ["sit", "sit down", "take a seat", "have a seat", "rest", "position"],
            "yawn": ["yawn", "tired", "sleepy", "bored"],
            "Waiting Fidget": ["fidget", "waiting fidget", "wait"],
            "sit down": ["sit down", "sit", "take a seat", "have a seat", "rest", "position"],
            "stand": ["stand", "stand up", "get up", "rise", "position"],
            "stand up": ["stand up", "stand", "get up", "rise", "position"],
            "walk": ["walk", "move", "go", "travel", "step"],
            "wave": ["wave", "hello", "hi", "greet", "goodbye", "bye"],
            "bow": ["bow", "bowing", "respect", "greeting", "formal"],
            "talk": ["talk", "speak", "say", "tell", "communicate"],
            "kick": ["kick", "kicking", "foot", "leg", "action"],
            "point": ["point", "indicate", "show", "direct", "gesture"],
            "headstand": ["headstand", "balance", "acrobatics", "skill"],
            "somersault": ["somersault", "summersault", "flip", "roll", "tumble"],
            "pushups": ["pushups", "push up", "exercise", "strength"],
            "situps": ["situps", "sit up", "exercise", "core", "fitness"],
            "fly": ["fly", "flying", "jump", "leap", "acrobatics"],
            "getup": ["get up", "getup", "rise", "stand", "recover"],
            "thinking": ["think", "thinking", "ponder", "reflect", "consider"],
            "head_yes": ["head yes", "head_yes", "nod", "nodding", "shake head yes", "yes gesture"],
            "head_no": ["head no", "head_no", "shake head", "shake head no", "no gesture"],
            "dance": ["dance", "dancing", "move to music", "groove"],
            "stop": ["stop", "halt", "cease", "end", "finish"]
        }
        
        # Return mapped keywords or default to skill name
        return activation_keywords_mapping.get(skill_name, [skill_name])

    def _execute_dance_command(self, dance_command: str) -> bool:
        """
        Execute a specific dance command using ARC HTTP commands.
        
        Args:
            dance_command: The specific dance command to execute
            
        Returns:
            bool: True if command was sent successfully
        """
        try:
            # Map dance commands to ARC HTTP commands
            arc_commands = {
                "disco dance": "Disco Dance",
                "disco_dance": "Disco Dance",
                "hands dance": "Hands Dance", 
                "hands_dance": "Hands Dance",
                "predance": "Predance",
                "ymca dance": "YMCA Dance",
                "ymca_dance": "YMCA Dance"
            }
            
            if dance_command in arc_commands:
                arc_command = arc_commands[dance_command]
                self.logger.info(f"Executing dance command: {dance_command} -> {arc_command}")
                
                # Send the ARC HTTP command using the EZ-Robot's send method
                # The EZ-Robot will construct the proper HTTP URL with the command
                result = self.ez_robot.send("Auto Position", "AutoPositionAction", arc_command)
                
                if result is not None:
                    # Add to pending actions for completion tracking
                    self.add_pending_action(dance_command)
                    self._track_action_start(dance_command)
                    
                    # Update body position
                    self.update_body_position("dancing")
                    
                    self.logger.info(f"Successfully sent dance command: {dance_command}")
                    return True
                else:
                    self.logger.warning(f"Failed to send dance command: {dance_command}")
                    return False
            else:
                self.logger.warning(f"Unknown dance command: {dance_command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing dance command {dance_command}: {e}")
            return False

    def _update_body_position_from_command(self, command: str):
        """Update body position based on the command that was executed."""
        command_lower = command.lower()
        
        # Only update position if we have a valid current position
        if self.current_body_position is None:
            self.logger.warning("Cannot update position - no current position set")
            return
        
        # Map commands to resulting positions
        position_mapping = {
            "sit": "sitting",
            "sit down": "sitting",
            "stand": "standing", 
            "stand up": "standing",
            "getup": "standing",
            "lie down": "lying",
            "headstand": "headstanding",
            "somersault": "lying",  # Usually ends up lying down
            "pushups": "lying",
            "situps": "lying",
            "dance": "dancing",
            "disco dance": "dancing",
            "disco_dance": "dancing",
            "hands dance": "dancing",
            "hands_dance": "dancing",
            "predance": "dancing",
            "ymca dance": "dancing",
            "ymca_dance": "dancing"
        }
        
        for cmd, position in position_mapping.items():
            if cmd in command_lower:
                self.update_body_position(position)
                break 

    async def execute_body_movement_script(self, script_name: str, script_config: Dict[str, Any]) -> bool:
        """
        Execute a body movement script based on NUECOGAR emotional state.
        
        Args:
            script_name: Name of the script to execute
            script_config: Configuration for the script
            
        Returns:
            True if executed successfully, False otherwise
        """
        try:
            current_time = time.time()
            
            # Check cooldown
            if current_time - self.last_body_movement_time < self.body_movement_cooldown:
                self.logger.debug(f"Body movement on cooldown: {script_name}")
                return False
            
            # Check if already executed recently
            if script_name in self.executed_body_movements:
                self.logger.debug(f"Body movement recently executed: {script_name}")
                return False
            
            script_type = script_config.get("type")
            command = script_config.get("command")
            description = script_config.get("description", "")
            
            self.logger.info(f"Executing body movement script: {script_name} ({description})")
            
            if script_type == "eye_expression":
                # Execute eye expression
                success = await self._execute_eye_expression(command)
            elif script_type == "body_movement":
                # Execute body movement through ARC
                success = await self._execute_arc_body_movement(command)
            else:
                self.logger.warning(f"Unknown script type: {script_type}")
                return False
            
            if success:
                # Update tracking
                self.last_body_movement_time = current_time
                self.executed_body_movements.add(script_name)
                
                # Remove from executed set after cooldown
                asyncio.create_task(self._remove_from_executed_after_cooldown(script_name))
                
                self.logger.info(f"Successfully executed body movement script: {script_name}")
                return True
            else:
                self.logger.warning(f"Failed to execute body movement script: {script_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing body movement script {script_name}: {e}")
            return False
    
    async def _execute_eye_expression(self, command: str) -> bool:
        """Execute eye expression command."""
        try:
            if not self.ez_robot:
                self.logger.warning("EZ-Robot not available for eye expression")
                return False
            
            # Map command to EZ-Robot eye expression
            eye_expression_mapping = {
                "eyes_joy": "EYES_JOY",
                "eyes_sad": "EYES_SAD", 
                "eyes_surprise": "EYES_SURPRISE",
                "eyes_anger": "EYES_ANGER",
                "eyes_fear": "EYES_FEAR",
                "eyes_disgust": "EYES_DISGUST",
                "eyes_open": "EYES_OPEN",
                "eyes_closed": "EYES_CLOSED"
            }
            
            if command in eye_expression_mapping:
                # Execute through EZ-Robot
                result = self.ez_robot.send_eye_expression(command)
                return result is not None
            else:
                self.logger.warning(f"Unknown eye expression command: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing eye expression {command}: {e}")
            return False
    
    async def _execute_arc_body_movement(self, command: str) -> bool:
        """Execute body movement command through ARC Script Collection."""
        try:
            # Map command to ARC script collection
            arc_script_mapping = {
                "reaction_amazed": "reaction_amazed",
                "reaction_terrified": "reaction_terrified", 
                "reaction_ecstatic": "reaction_ecstatic",
                "reaction_amused": "reaction_amused",
                "reaction_irritated": "reaction_irritated"
            }
            
            if command in arc_script_mapping:
                script_name = arc_script_mapping[command]
                self.logger.info(f"🎭 Executing ARC Script Collection: {script_name}")
                
                # Execute through EZ-Robot script collection
                if self.ez_robot:
                    result = self.ez_robot.send_script_wait(script_name)
                    if result is not None:
                        self.logger.info(f"✅ Successfully executed ARC script: {script_name}")
                        # Add to pending actions for completion tracking
                        self.add_pending_action(script_name)
                        
                        # CRITICAL: Reaction and speech scripts stop naturally, so mark as complete immediately
                        if command.startswith("reaction_") or command.startswith("speech_"):
                            script_type = "reaction" if command.startswith("reaction_") else "speech"
                            self.logger.info(f"🎭 {script_type.capitalize()} script {script_name} marked as complete (stops naturally)")
                            self.remove_pending_action(script_name)
                        
                        return True
                    else:
                        self.logger.warning(f"❌ Failed to execute ARC script: {script_name}")
                        return False
                else:
                    self.logger.warning("EZ-Robot not available for body movement")
                    return False
            else:
                self.logger.warning(f"Unknown body movement command: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing body movement {command}: {e}")
            return False
    
    async def _execute_coordinated_eye_expression(self, reaction_command: str) -> bool:
        """Execute coordinated eye expression for reaction scripts."""
        try:
            # Map reaction commands to their coordinated eye expressions
            eye_coordination_mapping = {
                "reaction_amazed": "eyes_surprise",
                "reaction_terrified": "eyes_sad", 
                "reaction_ecstatic": "eyes_surprise",
                "reaction_amused": "eyes_joy",
                "reaction_irritated": "eyes_sad"
            }
            
            if reaction_command in eye_coordination_mapping:
                eye_expression = eye_coordination_mapping[reaction_command]
                self.logger.info(f"👁️ Executing coordinated eye expression: {eye_expression} for {reaction_command}")
                
                # Execute the eye expression
                result = await self._execute_eye_expression(eye_expression)
                if result:
                    self.logger.info(f"✅ Successfully executed coordinated eye expression: {eye_expression}")
                else:
                    self.logger.warning(f"❌ Failed to execute coordinated eye expression: {eye_expression}")
                return result
            else:
                self.logger.warning(f"No coordinated eye expression defined for: {reaction_command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing coordinated eye expression for {reaction_command}: {e}")
            return False
    
    async def _remove_from_executed_after_cooldown(self, script_name: str):
        """Remove script from executed set after cooldown period."""
        await asyncio.sleep(self.body_movement_cooldown)
        self.executed_body_movements.discard(script_name)
    
    async def execute_exploration_movement(self, direction: str) -> bool:
        """
        Execute exploration movement command through ARC HTTP interface.
        
        Args:
            direction: Movement direction (forward, reverse, left, right, stop)
            
        Returns:
            True if executed successfully, False otherwise
        """
        try:
            if direction not in self.movement_commands:
                self.logger.warning(f"Unknown movement direction: {direction}")
                return False
            
            current_time = time.time()
            
            # Check exploration cooldown
            if (self.last_exploration_action and 
                current_time - self.last_exploration_action < self.exploration_cooldown):
                self.logger.debug(f"Exploration movement on cooldown: {direction}")
                return False
            
            url = self.movement_commands[direction]
            self.logger.info(f"Executing exploration movement: {direction} -> {url}")
            
            # Send HTTP request to ARC
            import requests
            try:
                response = requests.get(url, timeout=5.0)
                if response.status_code == 200:
                    self.last_exploration_action = current_time
                    self.logger.info(f"Successfully executed exploration movement: {direction}")
                    
                    # Update direction tracking if it's a turn
                    if direction in ["left", "right"]:
                        # Use async turn direction for physical movement
                        if hasattr(self, 'loop') and self.loop:
                            future = asyncio.run_coroutine_threadsafe(
                                self.turn_direction(direction), 
                                self.loop
                            )
                            future.result(timeout=30.0)
                        else:
                            # Fix: Use proper async execution instead of asyncio.run() in running event loop
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # We're in an async context, create a task
                                    task = asyncio.create_task(self.turn_direction(direction))
                                    await task
                                else:
                                    # No running loop, create new one
                                    asyncio.run(self.turn_direction(direction))
                            except RuntimeError:
                                # Fallback: create new event loop
                                asyncio.run(self.turn_direction(direction))
                    
                    return True
                else:
                    self.logger.warning(f"ARC returned status {response.status_code} for {direction}")
                    return False
                    
            except requests.RequestException as e:
                self.logger.error(f"HTTP request failed for {direction}: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing exploration movement {direction}: {e}")
            return False
    
    def check_exploration_need(self) -> Optional[str]:
        """
        Check if exploration need should trigger movement.
        
        Returns:
            Movement direction if should explore, None otherwise
        """
        current_time = time.time()
        
        # Check if exploration need is high enough
        if self.exploration_need_level < self.exploration_threshold:
            return None
        
        # Check cooldown
        if (self.last_exploration_action and 
            current_time - self.last_exploration_action < self.exploration_cooldown):
            return None
        
        # Determine exploration direction based on current state
        # For now, use simple random selection
        import random
        directions = ["forward", "left", "right"]
        return random.choice(directions)
    
    def update_exploration_need(self, level: float):
        """
        Update exploration need level.
        
        Args:
            level: New exploration need level (0.0 to 1.0)
        """
        self.exploration_need_level = max(0.0, min(1.0, level))
        self.logger.debug(f"Updated exploration need level: {self.exploration_need_level}")
    
    async def execute_coordinated_movements(self, movements: List[Dict[str, Any]]) -> bool:
        """
        Execute coordinated eye and body movements simultaneously.
        
        Args:
            movements: List of movement configurations
            
        Returns:
            True if all movements executed successfully, False otherwise
        """
        try:
            if not movements:
                return True
            
            # Group movements by timing
            simultaneous_movements = []
            sequential_movements = []
            
            for movement in movements:
                if movement.get("timing") == "simultaneous":
                    simultaneous_movements.append(movement)
                else:
                    sequential_movements.append(movement)
            
            # Execute simultaneous movements
            if simultaneous_movements:
                tasks = []
                for movement in simultaneous_movements:
                    script_name = movement["script_name"]
                    script_config = {
                        "type": movement["type"],
                        "command": movement["command"],
                        "description": movement["description"]
                    }
                    task = self.execute_body_movement_script(script_name, script_config)
                    tasks.append(task)
                
                # Execute all simultaneous movements
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success = all(isinstance(result, bool) and result for result in results)
                
                if not success:
                    self.logger.warning("Some simultaneous movements failed")
            
            # Execute sequential movements
            for movement in sequential_movements:
                script_name = movement["script_name"]
                script_config = {
                    "type": movement["type"],
                    "command": movement["command"],
                    "description": movement["description"]
                }
                success = await self.execute_body_movement_script(script_name, script_config)
                if not success:
                    self.logger.warning(f"Sequential movement failed: {script_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing coordinated movements: {e}")
            return False
    
    def _load_turn_taking_prompts(self) -> Dict:
        """
        Load turn-taking prompts from JSON file.
        
        Returns:
            Dict containing turn-taking prompts by personality type
        """
        try:
            prompts_file = "social_prompts/turn_taking.json"
            if os.path.exists(prompts_file):
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Turn-taking prompts file not found: {prompts_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading turn-taking prompts: {e}")
            return {}
    
    def get_turn_taking_prompt(self, context: str = "gameplay", personality_type: str = None) -> str:
        """
        Get a personality-appropriate turn-taking prompt.
        
        Args:
            context: The context for the prompt (gameplay, conversation, decision_making)
            personality_type: The personality type (INTP, ENFP, etc.)
            
        Returns:
            str: A turn-taking prompt appropriate for the personality and context
        """
        try:
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_turn_prompt_time < self.turn_prompt_cooldown:
                return None  # Still in cooldown
            
            # Get personality type from main app if not provided
            if not personality_type and self.main_app:
                personality_type = getattr(self.main_app, 'personality_type', 'INTP')
            
            # Get prompts for the personality type
            personality_prompts = self.turn_taking_prompts.get("turn_taking_prompts", {}).get(personality_type, {})
            if not personality_prompts:
                # Fallback to default
                personality_prompts = self.turn_taking_prompts.get("turn_taking_prompts", {}).get("default", {})
            
            # Get context-specific prompts
            context_prompts = personality_prompts.get("contexts", {}).get(context, [])
            if not context_prompts:
                # Fallback to general prompts
                context_prompts = personality_prompts.get("prompts", [])
            
            if not context_prompts:
                # Final fallback
                return "Your turn."
            
            # Select a random prompt
            import random
            selected_prompt = random.choice(context_prompts)
            
            # Update last prompt time
            self.last_turn_prompt_time = current_time
            
            self.logger.info(f"🎤 Selected turn-taking prompt for {personality_type} in {context}: '{selected_prompt}'")
            return selected_prompt
            
        except Exception as e:
            self.logger.error(f"Error getting turn-taking prompt: {e}")
            return "Your turn."
    
    async def perform_turn_taking_prompt(self, context: str = "gameplay", personality_type: str = None) -> bool:
        """
        Perform a turn-taking prompt using the ActionSystem.
        
        Args:
            context: The context for the prompt (gameplay, conversation, decision_making)
            personality_type: The personality type (INTP, ENFP, etc.)
            
        Returns:
            bool: True if prompt was performed successfully
        """
        try:
            # Get the prompt
            prompt = self.get_turn_taking_prompt(context, personality_type)
            if not prompt:
                return False  # Cooldown active
            
            # Perform verbal action
            success = await self.perform_verbal_action(prompt)
            
            if success:
                self.logger.info(f"🎤 Turn-taking prompt performed: '{prompt}'")
                
                # Log to timeline if main app is available
                if self.main_app and hasattr(self.main_app, 'log_timeline_event'):
                    self.main_app.log_timeline_event(
                        event_type="turn_taking_prompt",
                        description=f"Turn-taking prompt: {prompt}",
                        details={
                            "context": context,
                            "personality_type": personality_type,
                            "prompt": prompt
                        }
                    )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error performing turn-taking prompt: {e}")
            return False
    
    def _handle_earthly_game_suggestions(self, action_context: Dict, judgment_result: Dict, event_data: Dict):
        """
        Handle earthly game suggestions and integrate them into action context.
        
        Args:
            action_context: Current action context
            judgment_result: Results from judgment system
            event_data: Original event data
        """
        try:
            # Check if there's an earthly suggestion from judgment
            earthly_suggestion = judgment_result.get("earthly_suggestion")
            if not earthly_suggestion:
                return
            
            # Handle different types of earthly suggestions
            if earthly_suggestion.get("type") == "probe":
                # Execute a probe action
                self._execute_earthly_probe(earthly_suggestion, action_context)
            elif earthly_suggestion.get("type") == "task":
                # Execute a task action
                self._execute_earthly_task(earthly_suggestion, action_context)
            elif earthly_suggestion.get("type") == "idle":
                # Handle idle state
                self._handle_earthly_idle(earthly_suggestion, action_context)
                
        except Exception as e:
            self.logger.error(f"❌ Error handling earthly game suggestions: {e}")
    
    def _execute_earthly_probe(self, suggestion: Dict, action_context: Dict):
        """
        Execute an earthly probe action.
        
        Args:
            suggestion: Earthly suggestion dictionary
            action_context: Current action context
        """
        try:
            action_id = suggestion.get("action_id")
            obs_key = suggestion.get("obs")
            info_gain = suggestion.get("info_gain", 0.0)
            
            # 🔧 FIX: Log game reasoning event for probe execution
            if hasattr(self.main_app, 'consciousness_evaluation'):
                consciousness_eval = self.main_app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    consciousness_eval.increment_pdb_counter('game_reasoning', strength=1.5)
                    self.logger.info(f"🎮 Game Reasoning: Probe execution logged")
            
            # Add probe action to recommended actions
            probe_action = {
                "type": "earthly_probe",
                "action_id": action_id,
                "obs": obs_key,
                "info_gain": info_gain,
                "priority": "medium"
            }
            
            action_context["recommended_actions"].append(probe_action)
            
            # Log the probe action
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🌍 Earthly probe: {action_id} (obs: {obs_key}, info_gain: {info_gain:.3f})")
            
            # Evaluate Purpose Driven Behavior
            if self.main_app and hasattr(self.main_app, 'inner_self'):
                pdb_result = self.main_app.inner_self.evaluate_purpose_driven_behavior(
                    action_type="earthly_probe",
                    context={"obs": obs_key, "result": "probe_initiated", "info_gain": info_gain}
                )
                if pdb_result and pdb_result.get('pdb_score', 0) > 0:
                    self.logger.info(f"🎯 PDB Score: {pdb_result['pdb_score']:.2f} for earthly probe")
            
            # Store in short-term memory
            if self.main_app and hasattr(self.main_app, 'memory_system'):
                self.main_app.memory_system.store_short_term_memory({
                    "type": "pdb_event",
                    "phase": "action",
                    "class": "probe",
                    "obs": obs_key,
                    "result": "probe_initiated"
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error executing earthly probe: {e}")
    
    def _execute_earthly_task(self, suggestion: Dict, action_context: Dict):
        """
        Execute an earthly task action.
        
        Args:
            suggestion: Earthly suggestion dictionary
            action_context: Current action context
        """
        try:
            action_id = suggestion.get("action_id")
            need = suggestion.get("need")
            delta = suggestion.get("delta", 0.0)
            
            # 🔧 FIX: Log game reasoning event for task execution
            if hasattr(self.main_app, 'consciousness_evaluation'):
                consciousness_eval = self.main_app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    consciousness_eval.increment_pdb_counter('game_reasoning', strength=1.0)
                    self.logger.info(f"🎮 Game Reasoning: Task execution logged")
            
            # Add task action to recommended actions
            task_action = {
                "type": "earthly_task",
                "action_id": action_id,
                "need": need,
                "delta": delta,
                "priority": "high" if delta > 0.05 else "medium"
            }
            
            action_context["recommended_actions"].append(task_action)
            
            # Log the task action
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🌍 Earthly task: {action_id} (need: {need}, delta: {delta:.3f})")
            
            # Evaluate Purpose Driven Behavior
            if self.main_app and hasattr(self.main_app, 'inner_self'):
                pdb_result = self.main_app.inner_self.evaluate_purpose_driven_behavior(
                    action_type="earthly_task",
                    context={"need": need, "delta": delta, "result": "task_initiated"}
                )
                if pdb_result and pdb_result.get('pdb_score', 0) > 0:
                    self.logger.info(f"🎯 PDB Score: {pdb_result['pdb_score']:.2f} for earthly task")
            
            # Store in short-term memory
            if self.main_app and hasattr(self.main_app, 'memory_system'):
                self.main_app.memory_system.store_short_term_memory({
                    "type": "pdb_event",
                    "phase": "action",
                    "class": "task",
                    "need": need,
                    "delta": delta
                })
            
            # Add concept graph link
            if hasattr(self.main_app, "concept_graph_system"):
                self.main_app.concept_graph_system.add_concept_link(
                    "game/earthly_life_liig", 
                    f"need/{need}", 
                    0.7
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error executing earthly task: {e}")
    
    def _handle_earthly_idle(self, suggestion: Dict, action_context: Dict):
        """
        Handle earthly idle state.
        
        Args:
            suggestion: Earthly suggestion dictionary
            action_context: Current action context
        """
        try:
            # Log idle state
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log("🌍 Earthly idle state - no specific action needed")
            
            # Store idle state in memory
            if self.main_app and hasattr(self.main_app, 'memory_system'):
                self.main_app.memory_system.store_short_term_memory({
                    "type": "pdb_event",
                    "phase": "action",
                    "class": "idle",
                    "state": "earthly_idle"
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error handling earthly idle: {e}")