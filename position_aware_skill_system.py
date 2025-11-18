#!/usr/bin/env python3
"""
Position-Aware Skill System for CARL

This module implements the position-aware skill execution system that:
1. Tracks CARL's current body position (standing/sitting)
2. Checks if a skill requires a specific start position
3. Automatically executes position transitions when needed
4. Prevents injury by ensuring proper positioning before skill execution

Based on human brain processes and scientific research on motor control.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

class PositionAwareSkillSystem:
    """
    Position-aware skill execution system for CARL.
    
    This system simulates human motor control processes where the brain
    automatically knows what position is required for different actions
    and executes necessary transitions before performing the action.
    """
    
    def __init__(self, skills_dir: str = "skills"):
        """
        Initialize the position-aware skill system.
        
        Args:
            skills_dir: Directory containing skill files
        """
        self.skills_dir = skills_dir
        self.current_position = "sitting"  # Default position (CARL starts sitting)
        self.position_history = ["sitting"]  # Track recent positions
        self.max_history_length = 10
        
        # Position transition skills
        self.position_transitions = {
            "sitting_to_standing": ["stand up", "stand", "getup"],
            "standing_to_sitting": ["sit down", "sit"]
        }
        
        # Load all skills with position requirements
        self.skills_with_positions = self._load_skills_with_positions()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_skills_with_positions(self) -> Dict[str, Dict]:
        """
        Load all skill files and extract position requirements.
        
        Returns:
            Dictionary mapping skill names to their position requirements
        """
        skills = {}
        
        if not os.path.exists(self.skills_dir):
            self.logger.warning(f"Skills directory '{self.skills_dir}' not found!")
            return skills
        
        for filename in os.listdir(self.skills_dir):
            if filename.endswith('.json'):
                skill_path = os.path.join(self.skills_dir, filename)
                try:
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        skill_data = json.load(f)
                    
                    skill_name = skill_data.get("Name", filename[:-5])
                    start_position = skill_data.get("start_position", "any")
                    
                    skills[skill_name] = {
                        "start_position": start_position,
                        "prerequisite_pose": skill_data.get("prerequisite_pose", "any"),
                        "command_type": skill_data.get("command_type", "AutoPositionAction"),
                        "file_path": skill_path,
                        "data": skill_data
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error loading skill {filename}: {e}")
        
        return skills
    
    def update_current_position(self, new_position: str) -> None:
        """
        Update CARL's current position and maintain history.
        
        Args:
            new_position: New position (standing/sitting)
        """
        if new_position != self.current_position:
            self.current_position = new_position
            self.position_history.append(new_position)
            
            # Keep only recent history
            if len(self.position_history) > self.max_history_length:
                self.position_history = self.position_history[-self.max_history_length:]
            
            self.logger.info(f"Position updated: {new_position}")
    
    def get_current_position(self) -> str:
        """
        Get CARL's current position.
        
        Returns:
            Current position (standing/sitting)
        """
        return self.current_position
    
    def update_position(self, new_position: str):
        """
        Update CARL's current position and add to history.
        
        Args:
            new_position: The new position (standing/sitting)
        """
        if new_position not in ["standing", "sitting"]:
            logging.warning(f"Invalid position '{new_position}', keeping current position")
            return
            
        self.current_position = new_position
        self.position_history.append(new_position)
        
        # Keep only recent history
        if len(self.position_history) > self.max_history_length:
            self.position_history = self.position_history[-self.max_history_length:]
        
        logging.info(f"Position updated from to: {new_position}")
    
    def get_position_history(self) -> List[str]:
        """
        Get recent position history.
        
        Returns:
            List of recent positions
        """
        return self.position_history.copy()
    
    def check_skill_position_requirement(self, skill_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a skill requires a specific start position.
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            Tuple of (requires_position_change, required_position)
        """
        if skill_name not in self.skills_with_positions:
            # Skill not found, assume no position requirement
            return False, None
        
        skill_data = self.skills_with_positions[skill_name]
        
        # Check for prerequisite_pose first (new system)
        if "prerequisite_pose" in skill_data:
            required_position = skill_data["prerequisite_pose"]
            
            # If prerequisite_pose is "any", no position change needed
            if required_position == "any":
                return False, None
            
            # If current position matches required position, no change needed
            if self.current_position == required_position:
                return False, None
            
            # Position change required
            return True, required_position
        
        # Fallback to old start_position system
        required_position = skill_data.get("start_position", "any")
        
        if required_position == "any":
            return False, None
        
        if self.current_position == required_position:
            return False, None
        
        return True, required_position
    
    def get_required_transition_skills(self, from_position: str, to_position: str) -> List[str]:
        """
        Get the skills needed to transition between positions.
        
        Args:
            from_position: Current position
            to_position: Target position
            
        Returns:
            List of skills to execute for the transition
        """
        if from_position == to_position:
            return []
        
        if from_position == "sitting" and to_position == "standing":
            return ["stand up", "stand", "getup"]
        elif from_position == "standing" and to_position == "sitting":
            return ["sit down", "sit"]
        
        return []
    
    def analyze_skill_execution_plan(self, requested_skill: str) -> Dict:
        """
        Analyze what needs to be done to execute a skill safely.
        
        Args:
            requested_skill: The skill that was requested
            
        Returns:
            Dictionary with execution plan
        """
        plan = {
            "requested_skill": requested_skill,
            "current_position": self.current_position,
            "requires_position_change": False,
            "required_position": None,
            "transition_skills": [],
            "final_skills": [requested_skill],
            "total_skills": [requested_skill],
            "reasoning": []
        }
        
        # Check if skill requires position change
        needs_change, required_position = self.check_skill_position_requirement(requested_skill)
        
        if needs_change:
            plan["requires_position_change"] = True
            plan["required_position"] = required_position
            plan["reasoning"].append(f"Skill '{requested_skill}' requires {required_position} position")
            
            # Get transition skills
            transition_skills = self.get_required_transition_skills(
                self.current_position, required_position
            )
            
            if transition_skills:
                plan["transition_skills"] = transition_skills
                plan["total_skills"] = transition_skills + [requested_skill]
                plan["reasoning"].append(f"Need to execute: {' -> '.join(transition_skills)} -> {requested_skill}")
            else:
                plan["reasoning"].append("No transition skills available")
        else:
            plan["reasoning"].append(f"Skill '{requested_skill}' can be executed from current {self.current_position} position")
        
        return plan
    
    def simulate_human_decision_process(self, requested_skill: str) -> Dict:
        """
        Simulate the human brain's automatic decision process for motor actions.
        
        This simulates how humans automatically know they need to stand
        before dancing, or sit before certain actions, without conscious thought.
        
        Args:
            requested_skill: The skill that was requested
            
        Returns:
            Dictionary with human-like decision process
        """
        plan = self.analyze_skill_execution_plan(requested_skill)
        
        # Add human-like reasoning
        if plan["requires_position_change"]:
            plan["human_reasoning"] = [
                f"I am currently {self.current_position}",
                f"To {requested_skill}, I need to be {plan['required_position']}",
                f"I will automatically {plan['transition_skills'][0] if plan['transition_skills'] else 'adjust position'} first",
                f"Then I can {requested_skill} safely"
            ]
        else:
            plan["human_reasoning"] = [
                f"I am currently {self.current_position}",
                f"I can {requested_skill} from this position",
                f"No position change needed"
            ]
        
        return plan
    
    def get_skill_position_info(self, skill_name: str) -> Optional[Dict]:
        """
        Get detailed position information for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Dictionary with skill position information or None
        """
        if skill_name not in self.skills_with_positions:
            return None
        
        skill_data = self.skills_with_positions[skill_name]
        return {
            "skill_name": skill_name,
            "start_position": skill_data["start_position"],
            "command_type": skill_data["command_type"],
            "current_position": self.current_position,
            "position_match": skill_data["start_position"] == self.current_position or skill_data["start_position"] == "any"
        }
    
    def get_all_skills_by_position(self) -> Dict[str, List[str]]:
        """
        Get all skills organized by their required start position.
        
        Returns:
            Dictionary mapping positions to lists of skills
        """
        skills_by_position = {
            "standing": [],
            "sitting": [],
            "any": []
        }
        
        for skill_name, skill_data in self.skills_with_positions.items():
            position = skill_data["start_position"]
            if position in skills_by_position:
                skills_by_position[position].append(skill_name)
            else:
                skills_by_position["any"].append(skill_name)
        
        return skills_by_position
    
    def validate_skill_execution_safety(self, skill_name: str) -> Dict:
        """
        Validate if it's safe to execute a skill from current position.
        
        Args:
            skill_name: Name of the skill to validate
            
        Returns:
            Dictionary with safety validation results
        """
        validation = {
            "skill_name": skill_name,
            "current_position": self.current_position,
            "is_safe": True,
            "warnings": [],
            "recommendations": []
        }
        
        if skill_name not in self.skills_with_positions:
            validation["warnings"].append("Skill not found in position database")
            return validation
        
        skill_data = self.skills_with_positions[skill_name]
        required_position = skill_data["start_position"]
        
        if required_position == "any":
            validation["recommendations"].append("Skill can be executed from any position")
            return validation
        
        if self.current_position != required_position:
            validation["is_safe"] = False
            validation["warnings"].append(f"Skill requires {required_position} position, but currently {self.current_position}")
            validation["recommendations"].append(f"Execute position transition to {required_position} first")
        else:
            validation["recommendations"].append("Position is correct for safe execution")
        
        return validation

# Example usage and testing
if __name__ == "__main__":
    # Initialize the system
    pos_system = PositionAwareSkillSystem()
    
    # Test scenarios
    test_scenarios = [
        ("dance", "standing"),
        ("sit down", "standing"),
        ("stand up", "sitting"),
        ("wave", "sitting"),
        ("internet_search", "standing")
    ]
    
    print("🧠 Position-Aware Skill System Test")
    print("=" * 50)
    
    for skill, current_pos in test_scenarios:
        print(f"\n📋 Testing: {skill} (current position: {current_pos})")
        pos_system.update_current_position(current_pos)
        
        plan = pos_system.simulate_human_decision_process(skill)
        
        print(f"  🤔 Human reasoning:")
        for reason in plan["human_reasoning"]:
            print(f"    • {reason}")
        
        print(f"  ⚙️  Execution plan:")
        print(f"    • Skills to execute: {' -> '.join(plan['total_skills'])}")
        
        safety = pos_system.validate_skill_execution_safety(skill)
        print(f"  🛡️  Safety validation:")
        print(f"    • Safe to execute: {safety['is_safe']}")
        for warning in safety["warnings"]:
            print(f"    • ⚠️  {warning}")
        for rec in safety["recommendations"]:
            print(f"    • 💡 {rec}")
    
    print(f"\n📊 Position Summary:")
    print(f"  • Current position: {pos_system.get_current_position()}")
    print(f"  • Position history: {' -> '.join(pos_system.get_position_history())}")
    
    skills_by_pos = pos_system.get_all_skills_by_position()
    print(f"\n📁 Skills by position:")
    for position, skills in skills_by_pos.items():
        print(f"  • {position}: {len(skills)} skills") 