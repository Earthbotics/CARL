#!/usr/bin/env python3
"""
CARL Mapping Updater - Updates existing system files to use completed mappings.

This script reads the carl_completed_mappings.json file and updates existing 
needs, goals, skills, and concepts files to include the proper associations
and baseline mental concept associations.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class MappingUpdater:
    """Updates CARL's system files based on completed mappings."""
    
    def __init__(self):
        self.mappings = self._load_mappings()
        self.base_dirs = {
            'goals': 'goals',
            'needs': 'needs', 
            'skills': 'skills',
            'concepts': 'concepts'
        }
        
    def _load_mappings(self) -> Dict:
        """Load the completed mappings from carl_completed_mappings.json."""
        try:
            with open('carl_completed_mappings.json', 'r') as f:
                mappings = json.load(f)
                print(f"✅ Loaded mappings with {len(mappings.get('needs', []))} needs, "
                      f"{len(mappings.get('goals', []))} goals, "
                      f"{len(mappings.get('skills', []))} skills, "
                      f"{len(mappings.get('concepts', []))} concepts")
                return mappings
        except FileNotFoundError:
            print("❌ carl_completed_mappings.json not found!")
            return {'needs': [], 'goals': [], 'skills': [], 'concepts': []}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing carl_completed_mappings.json: {e}")
            return {'needs': [], 'goals': [], 'skills': [], 'concepts': []}
    
    def _get_mapping_by_name(self, mappings_list: List[Dict], name: str) -> Optional[Dict]:
        """Find a mapping entry by name."""
        for mapping in mappings_list:
            if mapping.get("Name", "").lower() == name.lower():
                return mapping
        return None
    
    def update_needs_files(self):
        """Update existing needs files with mapping associations."""
        print("\n🔄 Updating needs files...")
        needs_dir = self.base_dirs['needs']
        
        if not os.path.exists(needs_dir):
            os.makedirs(needs_dir, exist_ok=True)
            
        needs_mappings = self.mappings.get('needs', [])
        
        for need_mapping in needs_mappings:
            need_name = need_mapping.get("Name", "")
            if not need_name:
                continue
                
            need_file = os.path.join(needs_dir, f"{need_name}.json")
            
            # Load existing file or create new one
            if os.path.exists(need_file):
                with open(need_file, 'r') as f:
                    need_data = json.load(f)
                print(f"  📝 Updating existing need: {need_name}")
            else:
                need_data = {
                    "name": need_name,
                    "urgency": 0.5,
                    "satisfaction": 1.0,
                    "decay_rate": 0.1,
                    "associated_skills": [],
                    "associated_senses": [],
                    "concepts": [need_name],
                    "skill_class": {
                        "category": "Cognitive Skill",
                        "related_intelligence": "Intrapersonal"
                    },
                    "prerequisites": [],
                    "future_steps": []
                }
                print(f"  ✨ Creating new need: {need_name}")
            
            # Update with mapping data
            need_data["priority"] = need_mapping.get("Priority", 0.0)
            need_data["IsUsedInNeeds"] = need_mapping.get("IsUsedInNeeds", True)
            need_data["AssociatedGoals"] = need_mapping.get("AssociatedGoals", [])
            need_data["AssociatedNeeds"] = need_mapping.get("AssociatedNeeds", [])
            need_data["last_updated"] = str(datetime.now())
            
            # Save updated file
            with open(need_file, 'w') as f:
                json.dump(need_data, f, indent=4)
                
            print(f"    Goals: {need_data['AssociatedGoals']}")
            print(f"    Needs: {need_data['AssociatedNeeds']}")
    
    def update_goals_files(self):
        """Update existing goals files with mapping associations."""
        print("\n🎯 Updating goals files...")
        goals_dir = self.base_dirs['goals']
        
        if not os.path.exists(goals_dir):
            os.makedirs(goals_dir, exist_ok=True)
            
        goals_mappings = self.mappings.get('goals', [])
        
        for goal_mapping in goals_mappings:
            goal_name = goal_mapping.get("Name", "")
            if not goal_name:
                continue
                
            goal_file = os.path.join(goals_dir, f"{goal_name}.json")
            
            # Load existing file or create new one
            if os.path.exists(goal_file):
                with open(goal_file, 'r') as f:
                    goal_data = json.load(f)
                print(f"  📝 Updating existing goal: {goal_name}")
            else:
                goal_data = {
                    "name": goal_name,
                    "progress": 0.0,
                    "associated_skills": [],
                    "associated_senses": [],
                    "concepts": [goal_name],
                    "skill_class": {
                        "category": "Cognitive Skill",
                        "related_intelligence": "Intrapersonal"
                    },
                    "prerequisites": [],
                    "future_steps": []
                }
                print(f"  ✨ Creating new goal: {goal_name}")
            
            # Update with mapping data
            goal_data["priority"] = goal_mapping.get("Priority", 0.5)
            goal_data["IsUsedInNeeds"] = goal_mapping.get("IsUsedInNeeds", True)
            goal_data["AssociatedGoals"] = goal_mapping.get("AssociatedGoals", [])
            goal_data["AssociatedNeeds"] = goal_mapping.get("AssociatedNeeds", [])
            goal_data["last_updated"] = str(datetime.now())
            
            # Save updated file
            with open(goal_file, 'w') as f:
                json.dump(goal_data, f, indent=4)
                
            print(f"    Goals: {goal_data['AssociatedGoals']}")
            print(f"    Needs: {goal_data['AssociatedNeeds']}")
    
    def update_skills_files(self):
        """Update existing skills files with mapping associations."""
        print("\n🛠️ Updating skills files...")
        skills_dir = self.base_dirs['skills']
        
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir, exist_ok=True)
            
        skills_mappings = self.mappings.get('skills', [])
        
        for skill_mapping in skills_mappings:
            skill_name = skill_mapping.get("Name", "")
            if not skill_name:
                continue
                
            skill_file = os.path.join(skills_dir, f"{skill_name}.json")
            
            # Load existing file or create new one
            if os.path.exists(skill_file):
                with open(skill_file, 'r') as f:
                    skill_data = json.load(f)
                print(f"  📝 Updating existing skill: {skill_name}")
            else:
                skill_data = {
                    "Name": skill_name,
                    "Concepts": [],
                    "Motivators": [],
                    "Techniques": [],
                    "skill_class": {
                        "category": "Generic Skill",
                        "related_intelligence": "General"
                    },
                    "prerequisites": [],
                    "future_steps": []
                }
                print(f"  ✨ Creating new skill: {skill_name}")
            
            # Update with mapping data
            skill_data["Priority"] = skill_mapping.get("Priority", 0.0)
            skill_data["IsUsedInNeeds"] = skill_mapping.get("IsUsedInNeeds", False)
            skill_data["AssociatedGoals"] = skill_mapping.get("AssociatedGoals", [])
            skill_data["AssociatedNeeds"] = skill_mapping.get("AssociatedNeeds", [])
            skill_data["last_updated"] = str(datetime.now())
            
            # Save updated file
            with open(skill_file, 'w') as f:
                json.dump(skill_data, f, indent=4)
                
            print(f"    Goals: {skill_data['AssociatedGoals']}")
            print(f"    Needs: {skill_data['AssociatedNeeds']}")
    
    def update_concepts_files(self):
        """Update existing concepts files with mapping associations."""
        print("\n🧠 Updating concepts files...")
        concepts_dir = self.base_dirs['concepts']
        
        if not os.path.exists(concepts_dir):
            os.makedirs(concepts_dir, exist_ok=True)
            
        concepts_mappings = self.mappings.get('concepts', [])
        
        for concept_mapping in concepts_mappings:
            concept_name = concept_mapping.get("Name", "")
            if not concept_name:
                continue
                
            concept_file = os.path.join(concepts_dir, f"{concept_name}.json")
            
            # Load existing file or create new one
            if os.path.exists(concept_file):
                with open(concept_file, 'r') as f:
                    concept_data = json.load(f)
                print(f"  📝 Updating existing concept: {concept_name}")
            else:
                concept_data = {
                    "word": concept_name,
                    "type": "general",
                    "first_seen": str(datetime.now()),
                    "occurrences": 1,
                    "contexts": [],
                    "emotional_history": [],
                    "conceptnet_data": {
                        "has_data": False,
                        "last_lookup": None,
                        "edges": [],
                        "relationships": []
                    },
                    "related_concepts": []
                }
                print(f"  ✨ Creating new concept: {concept_name}")
            
            # Update with mapping data
            concept_data["IsUsedInNeeds"] = concept_mapping.get("IsUsedInNeeds", False)
            concept_data["AssociatedGoals"] = concept_mapping.get("AssociatedGoals", [])
            concept_data["AssociatedNeeds"] = concept_mapping.get("AssociatedNeeds", [])
            concept_data["last_updated"] = str(datetime.now())
            
            # Save updated file
            with open(concept_file, 'w') as f:
                json.dump(concept_data, f, indent=4)
                
            print(f"    Goals: {concept_data['AssociatedGoals']}")
            print(f"    Needs: {concept_data['AssociatedNeeds']}")
    
    def run_full_update(self):
        """Run the complete mapping update process."""
        print("🚀 Starting CARL mapping update process...")
        print(f"📁 Working in: {os.getcwd()}")
        
        self.update_needs_files()
        self.update_goals_files()
        self.update_skills_files()
        self.update_concepts_files()
        
        print("\n✅ Mapping update complete!")
        print("🎯 All system files now use completed mappings for baseline associations.")
        print("💫 Core emotions will be properly impacted by neurotransmitter processes.")

def main():
    """Main entry point."""
    updater = MappingUpdater()
    updater.run_full_update()

if __name__ == "__main__":
    main()
