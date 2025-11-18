#!/usr/bin/env python3
"""
CARL Curiosity Module

This module implements CARL's curiosity system that triggers when:
1. Fresh startup with no known WHO present
2. Unknown persons, pets, or environments are introduced
3. New objects or concepts are detected without prior memory

The curiosity module helps CARL engage proactively with its environment
and ask appropriate questions to learn about new entities.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

class CuriosityModule:
    """
    CARL's curiosity system for proactive learning and engagement.
    """
    
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Curiosity triggers
        self.curiosity_triggers = {
            'unknown_person': True,
            'unknown_pet': True,
            'unknown_environment': True,
            'unknown_object': True,
            'fresh_startup': True
        }
        
        # Known entities cache
        self.known_entities = {
            'people': set(),
            'pets': set(),
            'environments': set(),
            'objects': set()
        }
        
        # Curiosity questions
        self.curiosity_questions = {
            'person': [
                "What is your name?",
                "Have we met before?",
                "How are you doing today?",
                "What brings you here?"
            ],
            'pet': [
                "What's your pet's name?",
                "How long have you had them?",
                "What kind of animal is that?",
                "Are they friendly?"
            ],
            'environment': [
                "Where are we?",
                "What kind of place is this?",
                "Have I been here before?",
                "What should I know about this place?"
            ],
            'object': [
                "What is that?",
                "What does it do?",
                "Have I seen that before?",
                "Can you tell me about it?"
            ]
        }
        
        # Load known entities from memory
        self._load_known_entities()
    
    def _load_known_entities(self):
        """Load known entities from memory files."""
        try:
            # Load from people directory
            people_dir = "people"
            if os.path.exists(people_dir):
                for file in os.listdir(people_dir):
                    if file.endswith('.json'):
                        name = file.replace('.json', '')
                        self.known_entities['people'].add(name.lower())
            
            # Load from pets directory
            pets_dir = "pets"
            if os.path.exists(pets_dir):
                for file in os.listdir(pets_dir):
                    if file.endswith('.json'):
                        name = file.replace('.json', '')
                        self.known_entities['pets'].add(name.lower())
            
            # Load from places directory
            places_dir = "places"
            if os.path.exists(places_dir):
                for file in os.listdir(places_dir):
                    if file.endswith('.json'):
                        name = file.replace('.json', '')
                        self.known_entities['environments'].add(name.lower())
            
            # Load from things directory
            things_dir = "things"
            if os.path.exists(things_dir):
                for file in os.listdir(things_dir):
                    if file.endswith('.json'):
                        name = file.replace('.json', '')
                        self.known_entities['objects'].add(name.lower())
            
            self.logger.info(f"Loaded known entities: {len(self.known_entities['people'])} people, "
                           f"{len(self.known_entities['pets'])} pets, "
                           f"{len(self.known_entities['environments'])} environments, "
                           f"{len(self.known_entities['objects'])} objects")
            
        except Exception as e:
            self.logger.error(f"Error loading known entities: {e}")
    
    def check_fresh_startup_curiosity(self) -> List[str]:
        """
        Check if this is a fresh startup and generate appropriate curiosity questions.
        
        Returns:
            List of curiosity questions to ask
        """
        try:
            questions = []
            
            # Check if we have any known people
            if not self.known_entities['people']:
                questions.extend([
                    "What is your name?",
                    "Have we met before?"
                ])
                self.logger.info("🧠 Fresh startup detected - no known people, generating curiosity questions")
            
            # Check if we have any known environments
            if not self.known_entities['environments']:
                questions.append("Where are we?")
                self.logger.info("🧠 Fresh startup detected - no known environments, generating curiosity questions")
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Error checking fresh startup curiosity: {e}")
            return []
    
    def check_entity_curiosity(self, entity_type: str, entity_name: str) -> List[str]:
        """
        Check if an entity is unknown and generate curiosity questions.
        
        Args:
            entity_type: Type of entity (person, pet, environment, object)
            entity_name: Name or description of the entity
            
        Returns:
            List of curiosity questions to ask
        """
        try:
            questions = []
            entity_lower = entity_name.lower()
            
            # Check if entity is unknown
            if entity_type in self.known_entities:
                if entity_lower not in self.known_entities[entity_type]:
                    # Generate appropriate questions
                    if entity_type in self.curiosity_questions:
                        questions.extend(self.curiosity_questions[entity_type][:2])  # Take first 2 questions
                        self.logger.info(f"🧠 Unknown {entity_type} detected: {entity_name}, generating curiosity questions")
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Error checking entity curiosity: {entity_type}, {entity_name}: {e}")
            return []
    
    def process_vision_curiosity(self, vision_data: Dict) -> List[str]:
        """
        Process vision data for curiosity triggers.
        
        Args:
            vision_data: Vision analysis data
            
        Returns:
            List of curiosity questions to ask
        """
        try:
            questions = []
            
            if not vision_data or not vision_data.get('vision_active'):
                return questions
            
            # Check detected objects for unknown entities
            objects_detected = vision_data.get('recent_objects', [])
            for obj in objects_detected:
                if obj.lower() not in self.known_entities['objects']:
                    questions.extend(self.curiosity_questions['object'][:1])  # Take first question
                    self.logger.info(f"🧠 Unknown object detected in vision: {obj}")
                    break  # Only ask about first unknown object to avoid overwhelming
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Error processing vision curiosity: {e}")
            return []
    
    def process_conversation_curiosity(self, conversation_data: Dict) -> List[str]:
        """
        Process conversation data for curiosity triggers.
        
        Args:
            conversation_data: Conversation analysis data
            
        Returns:
            List of curiosity questions to ask
        """
        try:
            questions = []
            
            # Extract entities from conversation
            what = conversation_data.get('WHAT', '').lower()
            who = conversation_data.get('WHO', '').lower()
            
            # Check for person mentions
            if who and who not in ['user', 'carl'] and who not in self.known_entities['people']:
                questions.extend(self.curiosity_questions['person'][:2])
                self.logger.info(f"🧠 Unknown person mentioned in conversation: {who}")
            
            # Check for pet mentions
            pet_keywords = ['cat', 'dog', 'pet', 'animal', 'molly']
            for keyword in pet_keywords:
                if keyword in what and keyword not in self.known_entities['pets']:
                    questions.extend(self.curiosity_questions['pet'][:2])
                    self.logger.info(f"🧠 Unknown pet mentioned in conversation: {keyword}")
                    break
            
            # Check for environment mentions
            env_keywords = ['condo', 'house', 'room', 'place', 'here']
            for keyword in env_keywords:
                if keyword in what and keyword not in self.known_entities['environments']:
                    questions.extend(self.curiosity_questions['environment'][:1])
                    self.logger.info(f"🧠 Unknown environment mentioned in conversation: {keyword}")
                    break
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Error processing conversation curiosity: {e}")
            return []
    
    def generate_curiosity_response(self, questions: List[str]) -> str:
        """
        Generate a natural curiosity response from questions.
        
        Args:
            questions: List of curiosity questions
            
        Returns:
            Natural curiosity response string
        """
        try:
            if not questions:
                return ""
            
            # If only one question, ask it directly
            if len(questions) == 1:
                return questions[0]
            
            # If multiple questions, combine them naturally
            if len(questions) == 2:
                return f"{questions[0]} {questions[1]}"
            
            # If more than 2, take the first two
            return f"{questions[0]} {questions[1]}"
            
        except Exception as e:
            self.logger.error(f"Error generating curiosity response: {e}")
            return ""
    
    def update_known_entities(self, entity_type: str, entity_name: str):
        """
        Update known entities when new information is learned.
        
        Args:
            entity_type: Type of entity (person, pet, environment, object)
            entity_name: Name of the entity
        """
        try:
            if entity_type in self.known_entities:
                self.known_entities[entity_type].add(entity_name.lower())
                self.logger.info(f"🧠 Updated known entities: {entity_type} = {entity_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating known entities: {e}")
    
    def get_curiosity_summary(self) -> Dict:
        """
        Get a summary of curiosity system status.
        
        Returns:
            Dictionary with curiosity system information
        """
        return {
            'known_people': len(self.known_entities['people']),
            'known_pets': len(self.known_entities['pets']),
            'known_environments': len(self.known_entities['environments']),
            'known_objects': len(self.known_entities['objects']),
            'curiosity_triggers': self.curiosity_triggers,
            'is_fresh_startup': len(self.known_entities['people']) == 0
        }
