#!/usr/bin/env python3
"""
Script to test fresh startup functionality and recreate knowledge files
"""

import os
import json
from datetime import datetime

def create_sample_needs():
    """Create sample need files to test the structure."""
    print("📝 Creating sample need files...")
    
    need_configs = {
        "exploration": {
            "description": "Need for exploration",
            "strategy": "exploration_skills_development",
            "associated_goals": ["exercise", "pleasure"],
            "associated_skills": ["ezvision", "look_down", "look_forward", "walk", "talk"],
            "associated_senses": ["language", "vision"]
        },
        "love": {
            "description": "Need for love",
            "strategy": "social_interaction_skills",
            "associated_goals": ["people", "pleasure"],
            "associated_skills": ["talk", "dance", "wave"],
            "associated_senses": ["language", "vision"]
        },
        "play": {
            "description": "Need for play",
            "strategy": "play_skills_development",
            "associated_goals": ["pleasure", "exercise"],
            "associated_skills": ["dance", "wave", "talk", "imagine_scenario"],
            "associated_senses": ["language", "vision"]
        },
        "safety": {
            "description": "Need for safety",
            "strategy": "safety_awareness_skills",
            "associated_goals": ["exercise"],
            "associated_skills": ["ezvision", "look_down", "look_forward", "walk"],
            "associated_senses": ["language", "vision"]
        },
        "security": {
            "description": "Need for security",
            "strategy": "security_monitoring_skills",
            "associated_goals": ["exercise"],
            "associated_skills": ["ezvision", "look_down", "look_forward", "walk"],
            "associated_senses": ["language", "vision"]
        }
    }
    
    for need_name, config in need_configs.items():
        need_data = {
            "name": need_name,
            "type": "need",
            "description": config["description"],
            "priority": 0.5,
            "satisfaction_level": 0.5,
            "Learning_Integration": {"enabled": False},
            "Learning_System": {"strategy": config["strategy"]},
            "created_at": str(datetime.now()),
            "last_updated": str(datetime.now()),
            "associated_goals": config["associated_goals"],
            "associated_skills": config["associated_skills"],
            "associated_senses": config["associated_senses"]
        }
        
        file_path = f"needs/{need_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(need_data, f, indent=2)
        
        print(f"✅ Created {file_path}")

def create_sample_goals():
    """Create sample goal files to test the structure."""
    print("📝 Creating sample goal files...")
    
    goal_configs = {
        "exercise": {
            "description": "Goal to achieve exercise",
            "strategy": "physical_activity_skills",
            "associated_needs": ["exploration", "safety", "security"],
            "associated_skills": ["walk", "dance", "ezvision", "look_down", "look_forward"]
        },
        "people": {
            "description": "Goal to achieve people",
            "strategy": "social_interaction_skills",
            "associated_needs": ["love", "play"],
            "associated_skills": ["talk", "dance", "wave"]
        },
        "pleasure": {
            "description": "Goal to achieve pleasure",
            "strategy": "enjoyment_skills",
            "associated_needs": ["exploration", "love", "play"],
            "associated_skills": ["dance", "talk", "imagine_scenario", "wave"]
        },
        "production": {
            "description": "Goal to achieve production",
            "strategy": "productive_skills",
            "associated_needs": ["exploration", "safety"],
            "associated_skills": ["thinking", "talk", "imagine_scenario"]
        }
    }
    
    for goal_name, config in goal_configs.items():
        goal_data = {
            "name": goal_name,
            "type": "goal",
            "description": config["description"],
            "priority": 0.5,
            "progress": 0.0,
            "completed": False,
            "Learning_Integration": {"enabled": False},
            "Learning_System": {"strategy": config["strategy"]},
            "created_at": str(datetime.now()),
            "last_updated": str(datetime.now()),
            "associated_needs": config["associated_needs"],
            "associated_skills": config["associated_skills"]
        }
        
        file_path = f"goals/{goal_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(goal_data, f, indent=2)
        
        print(f"✅ Created {file_path}")

def create_sample_skills():
    """Create sample skill files to test the structure."""
    print("📝 Creating sample skill files...")
    
    skill_configs = {
        "ezvision": {
            "description": "Skill to use enhanced vision",
            "strategy": "vision_skills",
            "associated_needs": ["exploration", "safety", "security"],
            "associated_goals": ["exercise"],
            "concepts": ["ezvision"],
            "techniques": ["EZRobot-cmd-ezvision"],
            "command_type": "AutoPositionAction",
            "duration_type": "auto_stop"
        },
        "look_down": {
            "description": "Skill to look down",
            "strategy": "vision_skills",
            "associated_needs": ["exploration", "safety", "security"],
            "associated_goals": ["exercise"],
            "concepts": ["look down"],
            "techniques": ["EZRobot-cmd-look_down"],
            "command_type": "ScriptCollection",
            "duration_type": "3000ms"
        },
        "look_forward": {
            "description": "Skill to look forward",
            "strategy": "vision_skills",
            "associated_needs": ["exploration", "safety", "security"],
            "associated_goals": ["exercise"],
            "concepts": ["look forward"],
            "techniques": ["EZRobot-cmd-look_forward"],
            "command_type": "ScriptCollection",
            "duration_type": "3000ms"
        },
        "walk": {
            "description": "Skill to walk",
            "strategy": "movement_skills",
            "associated_needs": ["exploration", "safety", "security"],
            "associated_goals": ["exercise"],
            "concepts": ["walk"],
            "techniques": ["EZRobot-cmd-walk"],
            "command_type": "ScriptCollection",
            "duration_type": "3000ms"
        },
        "talk": {
            "description": "Skill to talk",
            "strategy": "communication_skills",
            "associated_needs": ["exploration", "love", "play"],
            "associated_goals": ["people", "pleasure", "production"],
            "concepts": ["talk", "speak", "communicate"],
            "techniques": ["EZRobot-cmd-talk"],
            "command_type": "ScriptCollection",
            "duration_type": "3000ms"
        },
        "dance": {
            "description": "Skill to dance",
            "strategy": "entertainment_skills",
            "associated_needs": ["love", "play"],
            "associated_goals": ["people", "pleasure", "exercise"],
            "concepts": ["dance", "move", "entertain"],
            "techniques": ["EZRobot-cmd-dance"],
            "command_type": "ScriptCollection",
            "duration_type": "3000ms"
        }
    }
    
    for skill_name, config in skill_configs.items():
        skill_data = {
            "name": skill_name,
            "type": "skill",
            "description": config["description"],
            "proficiency": 0.5,
            "uses": 0,
            "Learning_Integration": {"enabled": False},
            "Learning_System": {"strategy": config["strategy"]},
            "IsUsedInNeeds": True,
            "AssociatedGoals": config["associated_goals"],
            "AssociatedNeeds": config["associated_needs"],
            "Name": skill_name,
            "Concepts": config["concepts"],
            "Motivators": ["learn", "execute", "improve"],
            "Techniques": config["techniques"],
            "created": str(datetime.now()),
            "command_type": config["command_type"],
            "duration_type": config["duration_type"],
            "command_type_updated": str(datetime.now()),
            "created_at": str(datetime.now()),
            "last_updated": str(datetime.now())
        }
        
        file_path = f"skills/{skill_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(skill_data, f, indent=2)
        
        print(f"✅ Created {file_path}")

def main():
    """Main function to recreate knowledge files."""
    print("🚀 Recreating Knowledge Files")
    print("=" * 50)
    
    # Ensure directories exist
    for directory in ['needs', 'goals', 'skills']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Create sample files
    create_sample_needs()
    create_sample_goals()
    create_sample_skills()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    # Count files created
    for directory in ['needs', 'goals', 'skills']:
        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        print(f"✅ {directory}: {len(files)} files created")
    
    print("\n🎉 Knowledge files have been recreated successfully!")
    print("The application should now work properly with the fresh startup functionality.")

if __name__ == "__main__":
    main()
