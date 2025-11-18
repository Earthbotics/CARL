"""
CARL's Learning System - Implements Advanced Learning Principles

This module provides CARL with autonomous learning capabilities based on:
1. Active Learning and Engagement (Interleaving, Retrieval Practice, Constructive Learning)
2. Information Processing and Memory (Dual Coding, Spaced Repetition, Working Memory)
3. Learning Styles and Individual Differences (Multimodal Learning)
4. Neurological Basis of Learning (Action Prediction Error, Reward Prediction Error, Dual Learning System)
"""

import json
import os
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio


class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    SOCIAL = "social"
    MULTIMODAL = "multimodal"


class LearningLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class LearningSession:
    """Represents a learning session with tracking data."""
    session_id: str
    skill_name: str
    concept_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success_rate: float = 0.0
    difficulty_level: str = "beginner"
    learning_style_used: LearningStyle = LearningStyle.MULTIMODAL
    emotional_context: str = "neutral"
    notes: str = ""


class LearningSystem:
    """
    CARL's comprehensive learning system that implements advanced learning principles.
    """
    
    def __init__(self, base_dirs: Dict[str, str]):
        self.base_dirs = base_dirs
        self.learning_sessions: List[LearningSession] = []
        self.current_session: Optional[LearningSession] = None
        
        # Learning parameters
        self.spaced_repetition_intervals = [1, 3, 7, 14, 30]  # days
        self.working_memory_capacity = 7  # ±2 items
        self.interleaving_ratio = 0.3  # 30% mixing of different skills
        self.retrieval_practice_threshold = 0.7
        
        # Neurological learning parameters
        self.action_prediction_error_rate = 0.1
        self.reward_prediction_error_rate = 0.1
        self.habit_formation_threshold = 10
        
        # Load learning templates
        skill_template_path = os.path.join(self.base_dirs['skills'], 'skill_template.json')
        concept_template_path = os.path.join(self.base_dirs['concepts'], 'concept_template.json')
        self.skill_template = self._load_template(skill_template_path)
        self.concept_template = self._load_template(concept_template_path)
    
    def _load_template(self, template_path: str) -> Dict:
        """Load a template file."""
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
                print(f"Loaded template from {template_path}: {len(template_data)} keys")
                
                # Debug: Check for Learning_Integration
                if 'concept_template.json' in template_path:
                    if 'Learning_Integration' in template_data:
                        print(f"✅ Learning_Integration found in template")
                    else:
                        print(f"❌ Learning_Integration NOT found in template")
                        print(f"Available keys: {list(template_data.keys())}")
                        # Try to reload with full path verification
                        import os
                        if os.path.exists(template_path):
                            print(f"Template file exists at: {template_path}")
                            with open(template_path, 'r') as f2:
                                content = f2.read()
                                print(f"File size: {len(content)} characters")
                                if 'Learning_Integration' in content:
                                    print("✅ Learning_Integration found in file content")
                                    # Try to reload JSON
                                    try:
                                        reloaded_data = json.loads(content)
                                        if 'Learning_Integration' in reloaded_data:
                                            print("✅ Learning_Integration found in reloaded JSON")
                                            return reloaded_data
                                        else:
                                            print("❌ Learning_Integration not in reloaded JSON")
                                    except Exception as reload_error:
                                        print(f"JSON reload error: {reload_error}")
                                else:
                                    print("❌ Learning_Integration not in file content")
                
                return template_data
        except FileNotFoundError:
            print(f"Template file not found: {template_path}")
            return {}
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            return {}
    
    async def create_enhanced_skill(self, skill_name: str, context: Dict = None) -> bool:
        """
        Create a new skill with enhanced learning system integration.
        
        Args:
            skill_name: Name of the skill to create
            context: Additional context for skill creation
            
        Returns:
            bool: Whether skill was successfully created
        """
        try:
            # Create enhanced skill data
            skill_data = self._create_enhanced_skill_data(skill_name, context)
            
            # Save skill file
            skill_file = os.path.join(self.base_dirs['skills'], f"{skill_name}.json")
            with open(skill_file, 'w') as f:
                json.dump(skill_data, f, indent=4)
            
            # Create corresponding concept
            await self.create_enhanced_concept(skill_name, context)
            
            return True
            
        except Exception as e:
            print(f"Error creating enhanced skill {skill_name}: {e}")
            return False
    
    def _create_enhanced_skill_data(self, skill_name: str, context: Dict = None) -> Dict:
        """Create enhanced skill data with learning system integration."""
        # Start with template
        skill_data = self.skill_template.copy()
        
        # Determine command type and duration type
        script_commands_3000ms = ["walk", "look_forward", "look_down", "head_yes", "head_no"]
        script_commands_auto_stop = ["arm_right_down", "arm_right_down_sitting", "point_arm_right"]
        
        if skill_name in script_commands_3000ms:
            command_type = "ScriptCollection"
            duration_type = "3000ms"
        elif skill_name in script_commands_auto_stop:
            command_type = "ScriptCollection"
            duration_type = "auto_stop"
        else:
            command_type = "AutoPositionAction"
            duration_type = "auto_stop"
        
        # Update basic fields
        skill_data["Name"] = skill_name
        skill_data["Concepts"] = [skill_name.replace('_', ' ')]
        skill_data["Motivators"] = ["learn", "execute", "improve"]
        skill_data["Techniques"] = [f"EZRobot-cmd-{skill_name}"]
        skill_data["created"] = datetime.now().isoformat()
        
        # Add command type fields
        skill_data["command_type"] = command_type
        skill_data["duration_type"] = duration_type
        skill_data["command_type_updated"] = datetime.now().isoformat()
        
        # Initialize learning system - ensure Learning_System exists
        if "Learning_System" not in skill_data:
            # Import and use the defaults from concept_system
            try:
                from concept_system import ConceptDefaults
                skill_data["Learning_System"] = ConceptDefaults.LEARNING_SYSTEM_DEFAULTS.copy()
            except ImportError:
                # Fallback defaults
                skill_data["Learning_System"] = {
                    "skill_progression": {
                        "current_level": "beginner",
                        "level_progress": 0.0,
                        "mastery_threshold": 0.8,
                        "progression_stages": [
                            "beginner",
                            "intermediate",
                            "advanced",
                            "master"
                        ]
                    },
                    "feedback_system": {
                        "self_assessment": {
                            "execution_quality": 0.0,
                            "confidence_level": 0.0,
                            "enjoyment_level": 0.0
                        }
                    },
                    "learning_principles": {
                        "information_processing": {
                            "spaced_repetition": {
                                "next_review": (datetime.now() + timedelta(days=1)).isoformat()
                            }
                        },
                        "neurological_basis": {
                            "action_prediction_error": {
                                "repetition_count": 0
                            },
                            "reward_prediction_error": {
                                "expected_reward": 0.5
                            }
                        }
                    }
                }
        
        # Now safely initialize learning system fields
        if "skill_progression" in skill_data["Learning_System"]:
            skill_data["Learning_System"]["skill_progression"]["current_level"] = "beginner"
        
        if "feedback_system" in skill_data["Learning_System"] and "self_assessment" in skill_data["Learning_System"]["feedback_system"]:
            skill_data["Learning_System"]["feedback_system"]["self_assessment"]["execution_quality"] = 0.0
            skill_data["Learning_System"]["feedback_system"]["self_assessment"]["confidence_level"] = 0.0
            skill_data["Learning_System"]["feedback_system"]["self_assessment"]["enjoyment_level"] = 0.0
        
        # Set up spaced repetition if structure exists
        if ("learning_principles" in skill_data["Learning_System"] and 
            "information_processing" in skill_data["Learning_System"]["learning_principles"] and
            "spaced_repetition" in skill_data["Learning_System"]["learning_principles"]["information_processing"]):
            skill_data["Learning_System"]["learning_principles"]["information_processing"]["spaced_repetition"]["next_review"] = (
                datetime.now() + timedelta(days=1)
            ).isoformat()
        
        # Initialize neurological learning if structure exists
        if ("learning_principles" in skill_data["Learning_System"] and 
            "neurological_basis" in skill_data["Learning_System"]["learning_principles"]):
            if "action_prediction_error" in skill_data["Learning_System"]["learning_principles"]["neurological_basis"]:
                skill_data["Learning_System"]["learning_principles"]["neurological_basis"]["action_prediction_error"]["repetition_count"] = 0
            if "reward_prediction_error" in skill_data["Learning_System"]["learning_principles"]["neurological_basis"]:
                skill_data["Learning_System"]["learning_principles"]["neurological_basis"]["reward_prediction_error"]["expected_reward"] = 0.5
        
        return skill_data
    
    def _determine_concept_type(self, concept_name: str) -> str:
        """
        Determine the Type field for a concept based on its name and characteristics.
        
        Args:
            concept_name: Name of the concept
            
        Returns:
            String representing the concept type
        """
        # Concept type mappings from requirements
        concept_type_map = {
            "arm_right_down": "pose",
            "arm_right_down_sitting": "pose", 
            "dance": "action",
            "exercise": "goal",
            "exploration": "need",
            "ezvision": "system",
            "headstand": "pose",
            "hello": "action",
            "human": "thing",
            "language": "system",
            "looking_for_objects": "process",
            "look_down": "gaze_action",
            "look_forward": "gaze_action",
            "love": "need",
            "music": "thing",
            "people": "social_category",
            "play": "need",
            "pleasure": "goal",
            "point_arm_right": "action",
            "production": "goal",
            "robot": "thing",
            "safety": "need",
            "security": "need",
            "somersault": "action",
            "talk": "action",
            "thinking": "cognitive_process",
            "vision": "sense",
            "walk": "action",
            "wave": "action"
        }
        
        concept_lower = concept_name.lower().strip()
        
        # Return specific type if found
        if concept_lower in concept_type_map:
            return concept_type_map[concept_lower]
        
        # Default type determination based on name patterns
        if any(keyword in concept_lower for keyword in ["goal", "purpose", "aim"]):
            return "goal"
        elif any(keyword in concept_lower for keyword in ["need", "require", "necessary"]):
            return "need"
        elif any(keyword in concept_lower for keyword in ["action", "do", "perform", "execute"]):
            return "action"
        elif any(keyword in concept_lower for keyword in ["pose", "position", "posture"]):
            return "pose"
        elif any(keyword in concept_lower for keyword in ["sense", "feel", "perceive"]):
            return "sense"
        elif any(keyword in concept_lower for keyword in ["think", "cognitive", "mental"]):
            return "cognitive_process"
        elif any(keyword in concept_lower for keyword in ["system", "process", "mechanism"]):
            return "system"
        elif any(keyword in concept_lower for keyword in ["object", "item", "tool"]):
            return "thing"
        else:
            return "concept"  # Default fallback
    
    async def create_enhanced_concept(self, concept_name: str, context: Dict = None) -> bool:
        """
        Create a new concept with enhanced learning system integration.
        
        Args:
            concept_name: Name of the concept to create
            context: Additional context for concept creation
            
        Returns:
            bool: Whether concept was successfully created
        """
        try:
            # Create enhanced concept data
            concept_data = self._create_enhanced_concept_data(concept_name, context)
            
            # Save concept file
            concept_file = os.path.join(self.base_dirs['concepts'], f"{concept_name}_self_learned.json")
            with open(concept_file, 'w') as f:
                json.dump(concept_data, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error creating enhanced concept {concept_name}: {e}")
            return False
    
    def _create_enhanced_concept_data(self, concept_name: str, context: Dict = None) -> Dict:
        """Create enhanced concept data with learning system integration."""
        # Start with template
        concept_data = self.concept_template.copy()
        print(f"Creating concept data for {concept_name}, template keys: {list(concept_data.keys())}")
        
        # Update basic fields
        concept_data["word"] = concept_name
        concept_data["first_seen"] = datetime.now().isoformat()
        concept_data["last_updated"] = datetime.now().isoformat()
        
        # Add Type field and associations based on concept categorization
        concept_data["Type"] = self._determine_concept_type(concept_name)
        concept_data["IsUsedInNeeds"] = True
        concept_data["AssociatedGoals"] = []
        concept_data["AssociatedNeeds"] = []
        
        # Initialize learning integration - inject if missing
        if "Learning_Integration" not in concept_data:
            print(f"⚠️ Learning_Integration not found in concept template for {concept_name} - injecting defaults")
            # Import and use the defaults from concept_system
            try:
                from concept_system import ConceptDefaults
                concept_data["Learning_Integration"] = ConceptDefaults.LEARNING_INTEGRATION_DEFAULTS.copy()
                print(f"✅ Injected Learning_Integration defaults for {concept_name}")
            except ImportError:
                # Fallback defaults
                concept_data["Learning_Integration"] = {
                    "enabled": False,
                    "strategy": "none",
                    "concept_learning_system": {},
                    "concept_progression": {
                        "current_level": "basic_recognition",
                        "level_progress": 0.0,
                        "mastery_threshold": 0.8,
                        "progression_stages": [
                            "basic_recognition",
                            "contextual_understanding",
                            "flexible_application",
                            "creative_synthesis"
                        ]
                    },
                    "adaptive_learning": {
                        "difficulty_adjustment": {
                            "current_challenge": 0.5,
                            "success_rate": 0.5
                        },
                        "personalization": {
                            "learning_style": "general",
                            "preference_adaptation": 0.5
                        }
                    }
                }
                print(f"✅ Injected fallback Learning_Integration defaults for {concept_name}")
        
        # Initialize concept progression
        if "concept_progression" in concept_data["Learning_Integration"]:
            concept_data["Learning_Integration"]["concept_progression"]["current_level"] = "basic_recognition"
            concept_data["Learning_Integration"]["concept_progression"]["level_progress"] = 0.0
        
        # Set up spaced repetition if the structure exists
        if ("learning_principles" in concept_data["Learning_Integration"] and 
            "information_processing" in concept_data["Learning_Integration"]["learning_principles"] and
            "spaced_repetition" in concept_data["Learning_Integration"]["learning_principles"]["information_processing"]):
            concept_data["Learning_Integration"]["learning_principles"]["information_processing"]["spaced_repetition"]["next_review"] = (
                datetime.now() + timedelta(days=1)
            ).isoformat()
        
        # Initialize neurological learning if the structure exists
        if ("learning_principles" in concept_data["Learning_Integration"] and 
            "neurological_basis" in concept_data["Learning_Integration"]["learning_principles"] and
            "reward_prediction_error" in concept_data["Learning_Integration"]["learning_principles"]["neurological_basis"]):
            concept_data["Learning_Integration"]["learning_principles"]["neurological_basis"]["reward_prediction_error"]["expected_utility"] = 0.5
        
        return concept_data
    
    async def start_learning_session(self, skill_name: str, concept_name: str = None, 
                                   learning_style: LearningStyle = LearningStyle.MULTIMODAL) -> str:
        """
        Start a new learning session.
        
        Args:
            skill_name: Name of the skill to practice
            concept_name: Associated concept (optional)
            learning_style: Preferred learning style
            
        Returns:
            str: Session ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{skill_name}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            skill_name=skill_name,
            concept_name=concept_name or skill_name,
            start_time=datetime.now(),
            learning_style_used=learning_style
        )
        
        self.learning_sessions.append(self.current_session)
        
        print(f"🎓 Started learning session {session_id} for {skill_name}")
        return session_id
    
    async def end_learning_session(self, session_id: str, success_rate: float = 0.0, 
                                 notes: str = "") -> bool:
        """
        End a learning session and update learning progress.
        
        Args:
            session_id: ID of the session to end
            success_rate: Success rate of the session (0.0 to 1.0)
            notes: Additional notes about the session
            
        Returns:
            bool: Whether session was successfully ended
        """
        session = next((s for s in self.learning_sessions if s.session_id == session_id), None)
        if not session:
            return False
        
        session.end_time = datetime.now()
        session.duration = (session.end_time - session.start_time).total_seconds()
        session.success_rate = success_rate
        session.notes = notes
        
        # Update skill and concept learning progress
        await self._update_learning_progress(session)
        
        print(f"✅ Ended learning session {session_id} with {success_rate:.2f} success rate")
        return True
    
    async def _update_learning_progress(self, session: LearningSession):
        """Update learning progress for skill and concept."""
        # Update skill progress
        skill_file = os.path.join(self.base_dirs['skills'], f"{session.skill_name}.json")
        if os.path.exists(skill_file):
            await self._update_skill_progress(skill_file, session)
        
        # Update concept progress
        concept_file = os.path.join(self.base_dirs['concepts'], f"{session.concept_name}_self_learned.json")
        if os.path.exists(concept_file):
            await self._update_concept_progress(concept_file, session)
    
    async def _update_skill_progress(self, skill_file: str, session: LearningSession):
        """Update skill learning progress."""
        try:
            with open(skill_file, 'r') as f:
                skill_data = json.load(f)
            
            # Update usage statistics
            skill_data["usage_count"] = skill_data.get("usage_count", 0) + 1
            skill_data["last_used"] = datetime.now().isoformat()
            
            # Update success rate
            current_success_rate = skill_data.get("success_rate", 0.0)
            usage_count = skill_data["usage_count"]
            skill_data["success_rate"] = (current_success_rate * (usage_count - 1) + session.success_rate) / usage_count
            
            # Update learning progress
            skill_data["learning_progress"] = min(1.0, skill_data.get("learning_progress", 0.0) + (session.success_rate * 0.1))
            
            # Update neurological learning
            neurol = skill_data["Learning_System"]["learning_principles"]["neurological_basis"]
            neurol["action_prediction_error"]["repetition_count"] += 1
            neurol["reward_prediction_error"]["actual_reward"] = session.success_rate
            
            # Check for level progression
            await self._check_skill_level_progression(skill_data)
            
            # Save updated skill data
            with open(skill_file, 'w') as f:
                json.dump(skill_data, f, indent=4)
                
        except Exception as e:
            print(f"Error updating skill progress: {e}")
    
    async def _update_concept_progress(self, concept_file: str, session: LearningSession):
        """Update concept learning progress."""
        try:
            with open(concept_file, 'r') as f:
                concept_data = json.load(f)
            
            # Update occurrences
            concept_data["occurrences"] = concept_data.get("occurrences", 0) + 1
            
            # Update learning progress
            learning_integration = concept_data["Learning_Integration"]
            current_progress = learning_integration["concept_progression"]["level_progress"]
            learning_integration["concept_progression"]["level_progress"] = min(1.0, current_progress + (session.success_rate * 0.1))
            
            # Update neurological learning
            neurol = learning_integration["concept_learning_system"]["neurological_basis"]
            neurol["action_prediction_error"]["repetition_tracking"] += 1
            neurol["reward_prediction_error"]["actual_utility"] = session.success_rate
            
            # Check for level progression
            await self._check_concept_level_progression(concept_data)
            
            # Save updated concept data
            with open(concept_file, 'w') as f:
                json.dump(concept_data, f, indent=4)
                
        except Exception as e:
            print(f"Error updating concept progress: {e}")
    
    async def _check_skill_level_progression(self, skill_data: Dict):
        """Check if skill should progress to next level."""
        progression = skill_data["Learning_System"]["skill_progression"]
        current_level = progression["current_level"]
        level_progress = skill_data.get("learning_progress", 0.0)
        
        # Find current level index
        levels = progression["difficulty_levels"]
        current_index = next((i for i, level in enumerate(levels) if level["level"] == current_level), 0)
        
        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            if level_progress >= next_level["next_level_threshold"]:
                progression["current_level"] = next_level["level"]
                print(f"🎉 Skill {skill_data['Name']} progressed to {next_level['level']} level!")
    
    async def _check_concept_level_progression(self, concept_data: Dict):
        """Check if concept should progress to next level."""
        progression = concept_data["Learning_Integration"]["concept_progression"]
        current_level = progression["current_level"]
        level_progress = progression["level_progress"]
        
        # Find current level index
        levels = progression["understanding_levels"]
        current_index = next((i for i, level in enumerate(levels) if level["level"] == current_level), 0)
        
        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            if level_progress >= next_level["next_level_threshold"]:
                progression["current_level"] = next_level["level"]
                print(f"🧠 Concept {concept_data['word']} progressed to {next_level['level']} level!")
    
    async def get_learning_recommendations(self, skill_name: str = None, concept_name: str = None) -> Dict:
        """
        Get personalized learning recommendations based on current progress and learning principles.
        
        Args:
            skill_name: Specific skill to get recommendations for
            concept_name: Specific concept to get recommendations for
            
        Returns:
            Dict: Learning recommendations
        """
        recommendations = {
            "spaced_repetition": [],
            "interleaving": [],
            "retrieval_practice": [],
            "learning_style_adaptations": [],
            "neurological_optimizations": []
        }
        
        # Get skills that need review
        skills_needing_review = await self._get_skills_needing_review()
        recommendations["spaced_repetition"] = skills_needing_review
        
        # Get interleaving recommendations
        interleaving_skills = await self._get_interleaving_recommendations(skill_name)
        recommendations["interleaving"] = interleaving_skills
        
        # Get retrieval practice opportunities
        retrieval_practice = await self._get_retrieval_practice_opportunities(skill_name, concept_name)
        recommendations["retrieval_practice"] = retrieval_practice
        
        # Get learning style adaptations
        style_adaptations = await self._get_learning_style_adaptations(skill_name)
        recommendations["learning_style_adaptations"] = style_adaptations
        
        # Get neurological optimizations
        neuro_optimizations = await self._get_neurological_optimizations(skill_name)
        recommendations["neurological_optimizations"] = neuro_optimizations
        
        return recommendations
    
    async def _get_skills_needing_review(self) -> List[Dict]:
        """Get skills that need spaced repetition review."""
        skills_needing_review = []
        
        skills_dir = self.base_dirs['skills']
        for filename in os.listdir(skills_dir):
            if filename.endswith('.json') and filename != 'skill_template.json':
                skill_file = os.path.join(skills_dir, filename)
                try:
                    with open(skill_file, 'r') as f:
                        skill_data = json.load(f)
                    
                    # Check if review is needed
                    spaced_rep = skill_data.get("Learning_System", {}).get("learning_principles", {}).get("information_processing", {}).get("spaced_repetition", {})
                    next_review_str = spaced_rep.get("next_review")
                    
                    if next_review_str:
                        next_review = datetime.fromisoformat(next_review_str)
                        if datetime.now() >= next_review:
                            skills_needing_review.append({
                                "skill_name": skill_data["Name"],
                                "last_reviewed": spaced_rep.get("last_reviewed"),
                                "mastery_level": spaced_rep.get("mastery_level", 0)
                            })
                            
                except Exception as e:
                    print(f"Error checking skill {filename}: {e}")
        
        return skills_needing_review
    
    async def _get_interleaving_recommendations(self, current_skill: str = None) -> List[Dict]:
        """Get interleaving recommendations for skill practice."""
        recommendations = []
        
        # Get all skills
        skills_dir = self.base_dirs['skills']
        all_skills = []
        for filename in os.listdir(skills_dir):
            if filename.endswith('.json') and filename != 'skill_template.json':
                skill_name = filename[:-5]
                all_skills.append(skill_name)
        
        # Select skills for interleaving
        if current_skill and current_skill in all_skills:
            all_skills.remove(current_skill)
        
        # Select random skills for interleaving
        num_to_select = min(3, len(all_skills))
        selected_skills = random.sample(all_skills, num_to_select)
        
        for skill_name in selected_skills:
            recommendations.append({
                "skill_name": skill_name,
                "practice_duration": 300,  # 5 minutes
                "reason": "interleaving_practice"
            })
        
        return recommendations
    
    async def _get_retrieval_practice_opportunities(self, skill_name: str = None, concept_name: str = None) -> List[Dict]:
        """Get retrieval practice opportunities."""
        opportunities = []
        
        # Check if current skill needs retrieval practice
        if skill_name:
            skill_file = os.path.join(self.base_dirs['skills'], f"{skill_name}.json")
            if os.path.exists(skill_file):
                try:
                    with open(skill_file, 'r') as f:
                        skill_data = json.load(f)
                    
                    success_rate = skill_data.get("success_rate", 0.0)
                    if success_rate < self.retrieval_practice_threshold:
                        opportunities.append({
                            "type": "skill_retrieval",
                            "target": skill_name,
                            "reason": "low_success_rate",
                            "current_rate": success_rate
                        })
                        
                except Exception as e:
                    print(f"Error checking skill {skill_name}: {e}")
        
        return opportunities
    
    async def _get_learning_style_adaptations(self, skill_name: str = None) -> List[Dict]:
        """Get learning style adaptation recommendations."""
        adaptations = []
        
        # For now, recommend multimodal approach
        adaptations.append({
            "learning_style": "multimodal",
            "adaptation": "combine_visual_auditory_kinesthetic",
            "reason": "enhanced_retention"
        })
        
        return adaptations
    
    async def _get_neurological_optimizations(self, skill_name: str = None) -> List[Dict]:
        """Get neurological optimization recommendations."""
        optimizations = []
        
        # Action Prediction Error optimization
        optimizations.append({
            "type": "action_prediction_error",
            "optimization": "increase_repetition_frequency",
            "reason": "habit_formation"
        })
        
        # Reward Prediction Error optimization
        optimizations.append({
            "type": "reward_prediction_error",
            "optimization": "adjust_expected_reward",
            "reason": "learning_rate_optimization"
        })
        
        return optimizations
    
    async def apply_learning_principles(self, skill_name: str, context: Dict = None) -> Dict:
        """
        Apply learning principles to a specific skill.
        
        Args:
            skill_name: Name of the skill to apply principles to
            context: Additional context
            
        Returns:
            Dict: Applied learning principles and results
        """
        results = {
            "active_learning": {},
            "information_processing": {},
            "learning_styles": {},
            "neurological_basis": {}
        }
        
        # Apply Active Learning principles
        results["active_learning"] = await self._apply_active_learning(skill_name, context)
        
        # Apply Information Processing principles
        results["information_processing"] = await self._apply_information_processing(skill_name, context)
        
        # Apply Learning Styles
        results["learning_styles"] = await self._apply_learning_styles(skill_name, context)
        
        # Apply Neurological Basis
        results["neurological_basis"] = await self._apply_neurological_basis(skill_name, context)
        
        return results
    
    async def _apply_active_learning(self, skill_name: str, context: Dict = None) -> Dict:
        """Apply active learning principles."""
        return {
            "retrieval_practice": "enabled",
            "constructive_learning": "enabled",
            "discovery_oriented": "enabled",
            "goal_directed": "enabled"
        }
    
    async def _apply_information_processing(self, skill_name: str, context: Dict = None) -> Dict:
        """Apply information processing principles."""
        return {
            "dual_coding": "visual_auditory_kinesthetic",
            "spaced_repetition": "scheduled",
            "working_memory_optimization": "chunked_learning"
        }
    
    async def _apply_learning_styles(self, skill_name: str, context: Dict = None) -> Dict:
        """Apply learning style adaptations."""
        return {
            "multimodal": "enabled",
            "visual_adaptations": "diagrams_and_videos",
            "auditory_adaptations": "verbal_instructions",
            "kinesthetic_adaptations": "hands_on_practice",
            "social_adaptations": "collaborative_learning"
        }
    
    async def _apply_neurological_basis(self, skill_name: str, context: Dict = None) -> Dict:
        """Apply neurological learning principles."""
        return {
            "action_prediction_error": "tracking_enabled",
            "reward_prediction_error": "adaptive_learning_rate",
            "dual_learning_system": "reward_maximization_and_repetition"
        }
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics."""
        stats = {
            "total_sessions": len(self.learning_sessions),
            "total_duration": sum(s.duration or 0 for s in self.learning_sessions),
            "average_success_rate": 0.0,
            "learning_styles_used": {},
            "skill_progress": {},
            "concept_progress": {}
        }
        
        if self.learning_sessions:
            stats["average_success_rate"] = sum(s.success_rate for s in self.learning_sessions) / len(self.learning_sessions)
            
            # Count learning styles
            for session in self.learning_sessions:
                style = session.learning_style_used.value
                stats["learning_styles_used"][style] = stats["learning_styles_used"].get(style, 0) + 1
        
        return stats 