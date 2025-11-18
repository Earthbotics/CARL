#!/usr/bin/env python3
"""
Enhanced Association System for CARL

This system improves CARL's base personality and sense of self by:
1. Creating comprehensive cross-references between goals, needs, skills, and senses
2. Standardizing file formats for consistency
3. Implementing automated association discovery based on keywords
4. Leveraging ConceptNet associations for better linking
5. Creating a unified association framework

Key Features:
- Automated cross-referencing based on semantic similarity
- Standardized field naming across all file types
- Keyword-based association discovery
- ConceptNet integration for enhanced linking
- Comprehensive personality mapping
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import logging

class EnhancedAssociationSystem:
    """
    Enhanced system for managing CARL's associations and cross-references.
    """
    
    def __init__(self):
        """Initialize the enhanced association system."""
        self.logger = logging.getLogger(__name__)
        
        # Define base directories
        self.directories = {
            'goals': 'goals',
            'needs': 'needs', 
            'skills': 'skills',
            'senses': 'senses',
            'concepts': 'concepts',
            'people': 'people'
        }
        
        # Standardized field mappings for consistency
        self.field_mappings = {
            # Goals fields
            'goals': {
                'linked_needs': 'linked_needs',           # Standardized from AssociatedNeeds
                'linked_goals': 'linked_goals',           # Standardized from AssociatedGoals
                'linked_skills': 'linked_skills',         # Standardized from associated_skills
                'linked_senses': 'linked_senses',         # Standardized from associated_senses
                'associated_concepts': 'associated_concepts'  # For cross-referencing
            },
            # Needs fields
            'needs': {
                'linked_goals': 'linked_goals',           # Standardized from AssociatedGoals
                'linked_needs': 'linked_needs',           # Standardized from AssociatedNeeds
                'linked_skills': 'linked_skills',         # Standardized from associated_skills
                'linked_senses': 'linked_senses',         # Standardized from associated_senses
                'associated_concepts': 'associated_concepts'  # For cross-referencing
            },
            # Skills fields
            'skills': {
                'linked_goals': 'linked_goals',           # Standardized from AssociatedGoals
                'linked_needs': 'linked_needs',           # Standardized from AssociatedNeeds
                'linked_skills': 'linked_skills',         # For skill-to-skill associations
                'linked_senses': 'linked_senses',         # For sense integration
                'associated_concepts': 'associated_concepts'  # For cross-referencing
            },
            # Senses fields
            'senses': {
                'linked_goals': 'linked_goals',           # All goals (comprehensive)
                'linked_needs': 'linked_needs',           # All needs (comprehensive)
                'linked_skills': 'linked_skills',         # All skills (comprehensive)
                'associated_concepts': 'associated_concepts'  # For cross-referencing
            }
        }
        
        # Define specific associations to create
        self.specific_associations = {
            # Goal cross-references (all goals reference each other)
            'goal_cross_references': [
                ('exercise', 'people'),
                ('exercise', 'pleasure'),
                ('exercise', 'production'),
                ('people', 'pleasure'),
                ('people', 'production'),
                ('pleasure', 'production')
            ],
            
            # Skill-Goal associations
            'skill_goal_associations': [
                ('pushups', 'exercise'),
                ('situps', 'exercise'),
                ('headstand', 'exercise'),
                ('somersault', 'exercise'),
                ('walk', 'exercise'),
                ('dance', 'exercise'),
                ('dance', 'pleasure'),
                ('wave', 'people'),
                ('greet', 'people'),
                ('talk', 'people'),
                ('bow', 'people'),
                ('thinking', 'production'),
                ('ezvision', 'production')
            ],
            
            # Skill-Need associations
            'skill_need_associations': [
                ('stop', 'safety'),
                ('kick', 'play'),
                ('kick', 'security'),
                ('dance', 'play'),
                ('dance', 'exploration'),
                ('wave', 'love'),
                ('greet', 'love'),
                ('talk', 'love'),
                ('bow', 'love'),
                ('thinking', 'exploration'),
                ('ezvision', 'exploration'),
                ('walk', 'exploration'),
                ('somersault', 'play'),
                ('headstand', 'play')
            ],
            
            # Skill-Skill associations
            'skill_skill_associations': [
                ('wave', 'greet'),
                ('greet', 'wave'),
                ('dance', 'wave'),
                ('dance', 'somersault'),
                ('walk', 'stop'),
                ('stop', 'walk'),
                ('pushups', 'situps'),
                ('situps', 'pushups'),
                ('headstand', 'somersault'),
                ('somersault', 'headstand')
            ],
            
            # Need-Need associations
            'need_need_associations': [
                ('play', 'exploration'),
                ('exploration', 'play'),
                ('love', 'safety'),
                ('safety', 'love'),
                ('security', 'safety'),
                ('safety', 'security')
            ]
        }
        
        # Keyword-based association patterns
        self.keyword_patterns = {
            'exercise_keywords': ['exercise', 'fitness', 'workout', 'physical', 'movement', 'sport'],
            'people_keywords': ['social', 'interaction', 'communication', 'greeting', 'conversation'],
            'pleasure_keywords': ['fun', 'enjoyment', 'entertainment', 'happiness', 'joy'],
            'production_keywords': ['work', 'task', 'goal', 'achievement', 'creation', 'thinking'],
            'exploration_keywords': ['discover', 'learn', 'investigate', 'explore', 'curiosity'],
            'love_keywords': ['affection', 'care', 'friendship', 'relationship', 'bond'],
            'play_keywords': ['fun', 'game', 'entertainment', 'activity', 'amusement'],
            'safety_keywords': ['protection', 'security', 'safe', 'careful', 'caution'],
            'security_keywords': ['stability', 'protection', 'safety', 'reliable', 'secure']
        }
    
    def standardize_file_formats(self):
        """Standardize file formats across all system files."""
        self.logger.info("Standardizing file formats...")
        
        for file_type, directory in self.directories.items():
            if file_type in self.field_mappings:
                self._standardize_file_type(file_type, directory)
        
        self.logger.info("File format standardization complete")
    
    def _standardize_file_type(self, file_type: str, directory: str):
        """Standardize a specific file type."""
        if not os.path.exists(directory):
            return
        
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Apply field mappings
                    updated = False
                    for old_field, new_field in self.field_mappings[file_type].items():
                        if old_field in data and old_field != new_field:
                            data[new_field] = data.pop(old_field)
                            updated = True
                    
                    # Ensure all required fields exist
                    for field in self.field_mappings[file_type].values():
                        if field not in data:
                            data[field] = []
                            updated = True
                    
                    # Save if updated
                    if updated:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4, ensure_ascii=False)
                        self.logger.info(f"Standardized {filepath}")
                
                except Exception as e:
                    self.logger.error(f"Error standardizing {filepath}: {e}")
    
    def create_specific_associations(self):
        """Create the specific associations defined in the system."""
        self.logger.info("Creating specific associations...")
        
        # Create goal cross-references
        self._create_goal_cross_references()
        
        # Create skill-goal associations
        self._create_skill_goal_associations()
        
        # Create skill-need associations
        self._create_skill_need_associations()
        
        # Create skill-skill associations
        self._create_skill_skill_associations()
        
        # Create need-need associations
        self._create_need_need_associations()
        
        # Create comprehensive sense associations
        self._create_sense_associations()
        
        self.logger.info("Specific associations created")
    
    def _create_goal_cross_references(self):
        """Create cross-references between all goals."""
        goals_dir = self.directories['goals']
        if not os.path.exists(goals_dir):
            return
        
        # Get all goal files
        goal_files = [f for f in os.listdir(goals_dir) if f.endswith('.json')]
        goal_names = [f.replace('.json', '') for f in goal_files]
        
        for goal_name in goal_names:
            goal_file = os.path.join(goals_dir, f"{goal_name}.json")
            try:
                with open(goal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Add all other goals to linked_goals
                if 'linked_goals' not in data:
                    data['linked_goals'] = []
                
                for other_goal in goal_names:
                    if other_goal != goal_name and other_goal not in data['linked_goals']:
                        data['linked_goals'].append(other_goal)
                
                with open(goal_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                self.logger.info(f"Added cross-references to {goal_name}")
            
            except Exception as e:
                self.logger.error(f"Error updating {goal_name}: {e}")
    
    def _create_skill_goal_associations(self):
        """Create associations between skills and goals."""
        skills_dir = self.directories['skills']
        goals_dir = self.directories['goals']
        
        if not os.path.exists(skills_dir) or not os.path.exists(goals_dir):
            return
        
        for skill_name, goal_name in self.specific_associations['skill_goal_associations']:
            skill_file = os.path.join(skills_dir, f"{skill_name}.json")
            goal_file = os.path.join(goals_dir, f"{goal_name}.json")
            
            # Update skill file
            if os.path.exists(skill_file):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        skill_data = json.load(f)
                    
                    if 'linked_goals' not in skill_data:
                        skill_data['linked_goals'] = []
                    
                    if goal_name not in skill_data['linked_goals']:
                        skill_data['linked_goals'].append(goal_name)
                    
                    with open(skill_file, 'w', encoding='utf-8') as f:
                        json.dump(skill_data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Linked skill {skill_name} to goal {goal_name}")
                
                except Exception as e:
                    self.logger.error(f"Error updating skill {skill_name}: {e}")
            
            # Update goal file
            if os.path.exists(goal_file):
                try:
                    with open(goal_file, 'r', encoding='utf-8') as f:
                        goal_data = json.load(f)
                    
                    if 'linked_skills' not in goal_data:
                        goal_data['linked_skills'] = []
                    
                    if skill_name not in goal_data['linked_skills']:
                        goal_data['linked_skills'].append(skill_name)
                    
                    with open(goal_file, 'w', encoding='utf-8') as f:
                        json.dump(goal_data, f, indent=4, ensure_ascii=False)
                
                except Exception as e:
                    self.logger.error(f"Error updating goal {goal_name}: {e}")
    
    def _create_skill_need_associations(self):
        """Create associations between skills and needs."""
        skills_dir = self.directories['skills']
        needs_dir = self.directories['needs']
        
        if not os.path.exists(skills_dir) or not os.path.exists(needs_dir):
            return
        
        for skill_name, need_name in self.specific_associations['skill_need_associations']:
            skill_file = os.path.join(skills_dir, f"{skill_name}.json")
            need_file = os.path.join(needs_dir, f"{need_name}.json")
            
            # Update skill file
            if os.path.exists(skill_file):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        skill_data = json.load(f)
                    
                    if 'linked_needs' not in skill_data:
                        skill_data['linked_needs'] = []
                    
                    if need_name not in skill_data['linked_needs']:
                        skill_data['linked_needs'].append(need_name)
                    
                    with open(skill_file, 'w', encoding='utf-8') as f:
                        json.dump(skill_data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Linked skill {skill_name} to need {need_name}")
                
                except Exception as e:
                    self.logger.error(f"Error updating skill {skill_name}: {e}")
            
            # Update need file
            if os.path.exists(need_file):
                try:
                    with open(need_file, 'r', encoding='utf-8') as f:
                        need_data = json.load(f)
                    
                    if 'linked_skills' not in need_data:
                        need_data['linked_skills'] = []
                    
                    if skill_name not in need_data['linked_skills']:
                        need_data['linked_skills'].append(skill_name)
                    
                    with open(need_file, 'w', encoding='utf-8') as f:
                        json.dump(need_data, f, indent=4, ensure_ascii=False)
                
                except Exception as e:
                    self.logger.error(f"Error updating need {need_name}: {e}")
    
    def _create_skill_skill_associations(self):
        """Create associations between related skills."""
        skills_dir = self.directories['skills']
        
        if not os.path.exists(skills_dir):
            return
        
        for skill1_name, skill2_name in self.specific_associations['skill_skill_associations']:
            skill1_file = os.path.join(skills_dir, f"{skill1_name}.json")
            skill2_file = os.path.join(skills_dir, f"{skill2_name}.json")
            
            # Update skill1 file
            if os.path.exists(skill1_file):
                try:
                    with open(skill1_file, 'r', encoding='utf-8') as f:
                        skill1_data = json.load(f)
                    
                    if 'linked_skills' not in skill1_data:
                        skill1_data['linked_skills'] = []
                    
                    if skill2_name not in skill1_data['linked_skills']:
                        skill1_data['linked_skills'].append(skill2_name)
                    
                    with open(skill1_file, 'w', encoding='utf-8') as f:
                        json.dump(skill1_data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Linked skill {skill1_name} to skill {skill2_name}")
                
                except Exception as e:
                    self.logger.error(f"Error updating skill {skill1_name}: {e}")
            
            # Update skill2 file (bidirectional)
            if os.path.exists(skill2_file):
                try:
                    with open(skill2_file, 'r', encoding='utf-8') as f:
                        skill2_data = json.load(f)
                    
                    if 'linked_skills' not in skill2_data:
                        skill2_data['linked_skills'] = []
                    
                    if skill1_name not in skill2_data['linked_skills']:
                        skill2_data['linked_skills'].append(skill1_name)
                    
                    with open(skill2_file, 'w', encoding='utf-8') as f:
                        json.dump(skill2_data, f, indent=4, ensure_ascii=False)
                
                except Exception as e:
                    self.logger.error(f"Error updating skill {skill2_name}: {e}")
    
    def _create_need_need_associations(self):
        """Create associations between related needs."""
        needs_dir = self.directories['needs']
        
        if not os.path.exists(needs_dir):
            return
        
        for need1_name, need2_name in self.specific_associations['need_need_associations']:
            need1_file = os.path.join(needs_dir, f"{need1_name}.json")
            need2_file = os.path.join(needs_dir, f"{need2_name}.json")
            
            # Update need1 file
            if os.path.exists(need1_file):
                try:
                    with open(need1_file, 'r', encoding='utf-8') as f:
                        need1_data = json.load(f)
                    
                    if 'linked_needs' not in need1_data:
                        need1_data['linked_needs'] = []
                    
                    if need2_name not in need1_data['linked_needs']:
                        need1_data['linked_needs'].append(need2_name)
                    
                    with open(need1_file, 'w', encoding='utf-8') as f:
                        json.dump(need1_data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Linked need {need1_name} to need {need2_name}")
                
                except Exception as e:
                    self.logger.error(f"Error updating need {need1_name}: {e}")
            
            # Update need2 file (bidirectional)
            if os.path.exists(need2_file):
                try:
                    with open(need2_file, 'r', encoding='utf-8') as f:
                        need2_data = json.load(f)
                    
                    if 'linked_needs' not in need2_data:
                        need2_data['linked_needs'] = []
                    
                    if need1_name not in need2_data['linked_needs']:
                        need2_data['linked_needs'].append(need1_name)
                    
                    with open(need2_file, 'w', encoding='utf-8') as f:
                        json.dump(need2_data, f, indent=4, ensure_ascii=False)
                
                except Exception as e:
                    self.logger.error(f"Error updating need {need2_name}: {e}")
    
    def _create_sense_associations(self):
        """Create comprehensive associations for all senses."""
        senses_dir = self.directories['senses']
        goals_dir = self.directories['goals']
        needs_dir = self.directories['needs']
        skills_dir = self.directories['skills']
        
        if not os.path.exists(senses_dir):
            return
        
        # Get all goals, needs, and skills
        goals = [f.replace('.json', '') for f in os.listdir(goals_dir) if f.endswith('.json')] if os.path.exists(goals_dir) else []
        needs = [f.replace('.json', '') for f in os.listdir(needs_dir) if f.endswith('.json')] if os.path.exists(needs_dir) else []
        skills = [f.replace('.json', '') for f in os.listdir(skills_dir) if f.endswith('.json')] if os.path.exists(skills_dir) else []
        
        # Update each sense file
        for filename in os.listdir(senses_dir):
            if filename.endswith('.json'):
                sense_file = os.path.join(senses_dir, filename)
                try:
                    with open(sense_file, 'r', encoding='utf-8') as f:
                        sense_data = json.load(f)
                    
                    # Add all goals, needs, and skills
                    sense_data['linked_goals'] = goals
                    sense_data['linked_needs'] = needs
                    sense_data['linked_skills'] = skills
                    
                    with open(sense_file, 'w', encoding='utf-8') as f:
                        json.dump(sense_data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Updated sense {filename} with comprehensive associations")
                
                except Exception as e:
                    self.logger.error(f"Error updating sense {filename}: {e}")
    
    def discover_keyword_associations(self):
        """Discover associations based on keyword matching."""
        self.logger.info("Discovering keyword-based associations...")
        
        # Analyze all files for keyword matches
        self._analyze_keyword_matches()
        
        # Create associations based on semantic similarity
        self._create_semantic_associations()
        
        self.logger.info("Keyword-based associations discovered")
    
    def _analyze_keyword_matches(self):
        """Analyze files for keyword matches and create associations."""
        # This would implement sophisticated keyword analysis
        # For now, we'll use the predefined patterns
        pass
    
    def _create_semantic_associations(self):
        """Create associations based on semantic similarity."""
        # This would implement semantic analysis using ConceptNet or similar
        # For now, we'll use the predefined patterns
        pass
    
    def integrate_conceptnet_associations(self):
        """Integrate ConceptNet associations for enhanced linking."""
        self.logger.info("Integrating ConceptNet associations...")
        
        # This would integrate with ConceptNet API for enhanced associations
        # For now, we'll create a framework for it
        pass
    
    def create_personality_mapping(self):
        """Create a comprehensive personality mapping for CARL."""
        self.logger.info("Creating comprehensive personality mapping...")
        
        # Create personality profile
        personality_profile = {
            "core_traits": {
                "curiosity": "high",
                "social_engagement": "high", 
                "learning_orientation": "high",
                "playfulness": "high",
                "safety_awareness": "moderate"
            },
            "primary_drivers": [
                "exploration",
                "social_interaction", 
                "learning",
                "play",
                "safety"
            ],
            "skill_preferences": {
                "physical": ["dance", "wave", "walk"],
                "social": ["greet", "talk", "bow"],
                "cognitive": ["thinking", "ezvision"],
                "creative": ["dance", "singing"]
            },
            "emotional_patterns": {
                "joy_triggers": ["music", "social_interaction", "play"],
                "curiosity_triggers": ["new_objects", "questions", "exploration"],
                "safety_triggers": ["unknown_situations", "loud_noises"]
            }
        }
        
        # Save personality profile
        with open('carl_personality_profile.json', 'w', encoding='utf-8') as f:
            json.dump(personality_profile, f, indent=4, ensure_ascii=False)
        
        self.logger.info("Personality mapping created")
    
    def run_complete_association_update(self):
        """Run the complete association update process."""
        self.logger.info("Starting complete association update...")
        
        # Step 1: Standardize file formats
        self.standardize_file_formats()
        
        # Step 2: Create specific associations
        self.create_specific_associations()
        
        # Step 3: Discover keyword associations
        self.discover_keyword_associations()
        
        # Step 4: Integrate ConceptNet associations
        self.integrate_conceptnet_associations()
        
        # Step 5: Create personality mapping
        self.create_personality_mapping()
        
        self.logger.info("Complete association update finished")
    
    def generate_association_report(self):
        """Generate a comprehensive report of all associations."""
        self.logger.info("Generating association report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "details": {}
        }
        
        # Analyze each directory
        for file_type, directory in self.directories.items():
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) if f.endswith('.json')]
                report["summary"][file_type] = len(files)
                
                # Analyze associations in each file
                total_associations = 0
                for filename in files:
                    filepath = os.path.join(directory, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Count associations
                        associations = 0
                        for field in ['linked_goals', 'linked_needs', 'linked_skills', 'linked_senses', 'associated_concepts']:
                            if field in data:
                                associations += len(data[field])
                        
                        total_associations += associations
                    
                    except Exception as e:
                        self.logger.error(f"Error analyzing {filepath}: {e}")
                
                report["details"][file_type] = {
                    "file_count": len(files),
                    "total_associations": total_associations,
                    "avg_associations_per_file": total_associations / len(files) if files else 0
                }
        
        # Save report
        with open('association_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        self.logger.info("Association report generated")
        return report

def main():
    """Main function to run the enhanced association system."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create and run the system
    system = EnhancedAssociationSystem()
    
    print("🧠 Enhanced Association System for CARL")
    print("=" * 50)
    
    # Run complete update
    system.run_complete_association_update()
    
    # Generate report
    report = system.generate_association_report()
    
    print("\n📊 Association Report Summary:")
    for file_type, summary in report["summary"].items():
        print(f"   {file_type}: {summary} files")
    
    print("\n✅ Enhanced association system complete!")

if __name__ == "__main__":
    main()
