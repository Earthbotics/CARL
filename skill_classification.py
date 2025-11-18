#!/usr/bin/env python3
"""
CARL's Skill Classification System

This module provides skill classification functionality based on Howard Gardner's
Multiple Intelligences theory and human skill development frameworks.
"""

import json
import os
from typing import Dict, List, Optional, Any


class SkillClassifier:
    """
    Classifies skills based on human intelligence frameworks and provides
    prerequisite and future step relationships.
    """
    
    def __init__(self):
        """Initialize the skill classifier with default classifications."""
        self.skill_classifications = self._load_default_classifications()
    
    def _load_default_classifications(self) -> Dict[str, Dict[str, Any]]:
        """Load default skill classifications."""
        return {
            "wave": {
                "skill_class": {
                    "category": "Physical/Motor",
                    "related_intelligence": "Bodily-Kinesthetic",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "standing position",
                    "arm mobility",
                    "awareness of person to wave at"
                ],
                "future_steps": [
                    "continue conversation",
                    "move to next interaction",
                    "maintain social engagement"
                ]
            },
            "dance": {
                "skill_class": {
                    "category": "Physical/Motor",
                    "related_intelligence": "Bodily-Kinesthetic",
                    "complexity": "Intermediate",
                    "energy_level": "High"
                },
                "prerequisites": [
                    "standing position",
                    "rhythm awareness",
                    "music or beat",
                    "space to move"
                ],
                "future_steps": [
                    "continue dancing",
                    "end sequence",
                    "bow to audience",
                    "transition to next activity"
                ]
            },
            "bow": {
                "skill_class": {
                    "category": "Social",
                    "related_intelligence": "Interpersonal",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "standing position",
                    "awareness of social context",
                    "understanding of respect gesture"
                ],
                "future_steps": [
                    "maintain respectful posture",
                    "continue interaction",
                    "transition to next action"
                ]
            },
            "sit": {
                "skill_class": {
                    "category": "Physical/Motor",
                    "related_intelligence": "Bodily-Kinesthetic",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "standing position",
                    "available seating",
                    "balance and coordination"
                ],
                "future_steps": [
                    "maintain seated position",
                    "engage in seated activity",
                    "stand up when appropriate"
                ]
            },
            "stand": {
                "skill_class": {
                    "category": "Physical/Motor",
                    "related_intelligence": "Bodily-Kinesthetic",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "seated position",
                    "leg strength",
                    "balance"
                ],
                "future_steps": [
                    "maintain standing position",
                    "move to next location",
                    "engage in standing activity"
                ]
            },
            "point": {
                "skill_class": {
                    "category": "Social",
                    "related_intelligence": "Interpersonal",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "arm mobility",
                    "awareness of target",
                    "understanding of pointing gesture"
                ],
                "future_steps": [
                    "maintain attention on target",
                    "explain what is being pointed at",
                    "lower arm when done"
                ]
            },
            "thinking": {
                "skill_class": {
                    "category": "Cognitive",
                    "related_intelligence": "Logical-Mathematical",
                    "complexity": "Advanced",
                    "energy_level": "Medium"
                },
                "prerequisites": [
                    "problem or question to consider",
                    "cognitive resources available",
                    "time for reflection"
                ],
                "future_steps": [
                    "reach conclusion",
                    "formulate response",
                    "take action based on thoughts"
                ]
            },
            "walk": {
                "skill_class": {
                    "category": "Physical/Motor",
                    "related_intelligence": "Bodily-Kinesthetic",
                    "complexity": "Basic",
                    "energy_level": "Medium"
                },
                "prerequisites": [
                    "standing position",
                    "balance",
                    "clear path",
                    "leg mobility"
                ],
                "future_steps": [
                    "continue walking",
                    "reach destination",
                    "stop and engage in activity"
                ]
            },
            "greet": {
                "skill_class": {
                    "category": "Social",
                    "related_intelligence": "Interpersonal",
                    "complexity": "Basic",
                    "energy_level": "Low"
                },
                "prerequisites": [
                    "awareness of person to greet",
                    "understanding of social context",
                    "communication ability"
                ],
                "future_steps": [
                    "continue conversation",
                    "engage in interaction",
                    "maintain social connection"
                ]
            },
            "talk": {
                "skill_class": {
                    "category": "Social",
                    "related_intelligence": "Linguistic",
                    "complexity": "Intermediate",
                    "energy_level": "Medium"
                },
                "prerequisites": [
                    "language ability",
                    "something to communicate",
                    "listener present",
                    "communication context"
                ],
                "future_steps": [
                    "continue conversation",
                    "listen for response",
                    "maintain dialogue"
                ]
            }
        }
    
    def get_skill_classification(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get classification for a specific skill.
        
        Args:
            skill_name: Name of the skill to classify
            
        Returns:
            Dictionary containing skill classification or None if not found
        """
        skill_lower = skill_name.lower().strip()
        
        # Direct match
        if skill_lower in self.skill_classifications:
            return self.skill_classifications[skill_lower]
        
        # Fuzzy matching for common variations
        skill_variations = {
            "sitting": "sit",
            "sitting down": "sit",
            "sit down": "sit",
            "standing": "stand",
            "standing up": "stand",
            "stand up": "stand",
            "waving": "wave",
            "dancing": "dance",
            "bowing": "bow",
            "pointing": "point",
            "thinking": "thinking",
            "walking": "walk",
            "greeting": "greet",
            "talking": "talk",
            "speaking": "talk",
            "conversation": "talk"
        }
        
        if skill_lower in skill_variations:
            base_skill = skill_variations[skill_lower]
            return self.skill_classifications.get(base_skill)
        
        # Default classification for unknown skills
        return {
            "skill_class": {
                "category": "Unknown",
                "related_intelligence": "General",
                "complexity": "Unknown",
                "energy_level": "Unknown"
            },
            "prerequisites": [
                "basic motor control",
                "awareness of action"
            ],
            "future_steps": [
                "complete action",
                "transition to next activity"
            ]
        }
    
    def get_skills_by_category(self, category: str) -> List[str]:
        """
        Get all skills in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of skill names in the category
        """
        category_lower = category.lower()
        skills = []
        
        for skill_name, classification in self.skill_classifications.items():
            skill_category = classification.get("skill_class", {}).get("category", "").lower()
            if category_lower in skill_category or skill_category in category_lower:
                skills.append(skill_name)
        
        return skills
    
    def get_skills_by_intelligence(self, intelligence: str) -> List[str]:
        """
        Get all skills related to a specific intelligence type.
        
        Args:
            intelligence: Intelligence type to filter by
            
        Returns:
            List of skill names related to the intelligence
        """
        intelligence_lower = intelligence.lower()
        skills = []
        
        for skill_name, classification in self.skill_classifications.items():
            related_intelligence = classification.get("skill_class", {}).get("related_intelligence", "").lower()
            if intelligence_lower in related_intelligence or related_intelligence in intelligence_lower:
                skills.append(skill_name)
        
        return skills


# Global instance for easy importing
skill_classifier = SkillClassifier()
