#!/usr/bin/env python3
"""
Fresh Startup Handler for CARL

This script handles fresh startup scenarios by:
1. Properly recreating settings_current.ini from settings_default.ini
2. Ensuring all knowledge files are created with proper cross-referencing
3. Fixing any case sensitivity issues in configuration
4. Verifying the configuration is working properly
"""

import os
import shutil
import json
from datetime import datetime
from configparser import ConfigParser

def ensure_settings_file():
    """Ensure settings_current.ini exists and has proper structure."""
    print("Ensuring settings file is properly configured...")
    
    # Check if settings_current.ini exists and has proper structure
    if os.path.exists('settings_current.ini'):
        config = ConfigParser()
        config.read('settings_current.ini')
        
        if not config.has_section('settings'):
            print("settings_current.ini missing [settings] section, recreating from default...")
            recreate_settings_from_default()
        else:
            # Check for required keys
            required_keys = ['OpenAIAPIKey', 'twinwordkey']
            missing_keys = []
            for key in required_keys:
                if not config.has_option('settings', key):
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"Missing keys in settings_current.ini: {missing_keys}, recreating from default...")
                recreate_settings_from_default()
            else:
                print("settings_current.ini is properly configured")
                return True
    else:
        print("settings_current.ini not found, creating from default...")
        recreate_settings_from_default()
    
    return True

def recreate_settings_from_default():
    """Recreate settings_current.ini from settings_default.ini with proper case sensitivity."""
    print("Recreating settings_current.ini from settings_default.ini...")
    
    if not os.path.exists('settings_default.ini'):
        print("settings_default.ini not found!")
        return False
    
    # Copy the default file
    shutil.copy2('settings_default.ini', 'settings_current.ini')
    
    # Fix case sensitivity issues
    config = ConfigParser()
    config.read('settings_current.ini')
    
    # Ensure twinwordkey is lowercase (as expected by the code)
    if config.has_option('settings', 'TwinWordKey'):
        twinword_value = config.get('settings', 'TwinWordKey')
        config.remove_option('settings', 'TwinWordKey')
        config.set('settings', 'twinwordkey', twinword_value)
    
    # Write the corrected configuration
    with open('settings_current.ini', 'w') as f:
        config.write(f)
    
    print("settings_current.ini recreated with proper case sensitivity")

def ensure_knowledge_directories():
    """Ensure knowledge directories exist."""
    print("Ensuring knowledge directories exist...")
    
    directories = ['needs', 'goals', 'skills']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory exists: {directory}")

def create_default_needs():
    """Create default need files with proper cross-referencing."""
    print("Creating default need files...")
    
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
        
        print(f"Created {file_path}")

def create_default_goals():
    """Create default goal files with proper cross-referencing."""
    print("Creating default goal files...")
    
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
        
        print(f"Created {file_path}")

def create_default_skills():
    """Create default skill files with proper cross-referencing."""
    print("Creating default skill files...")
    
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
        
        print(f"Created {file_path}")

def verify_configuration():
    """Verify that the configuration is working properly."""
    print("Verifying configuration...")
    
    # Test settings file
    config = ConfigParser()
    config.read('settings_current.ini')
    
    if not config.has_section('settings'):
        print("[settings] section missing!")
        return False
    
    required_keys = ['OpenAIAPIKey', 'twinwordkey']
    for key in required_keys:
        if not config.has_option('settings', key):
            print(f"Missing key: {key}")
            return False
    
    print("Settings file verified")
    
    # Test knowledge files
    directories = ['needs', 'goals', 'skills']
    for directory in directories:
        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        if not files:
            print(f"No files in {directory}")
            return False
        print(f"{directory}: {len(files)} files")
    
    return True

def main():
    """Main fresh startup handler."""
    print("CARL Fresh Startup Handler")
    print("=" * 50)
    
    try:
        # Step 1: Ensure settings file is properly configured
        ensure_settings_file()
        
        # Step 2: Ensure knowledge directories exist
        ensure_knowledge_directories()
        
        # Step 3: Create default knowledge files
        create_default_needs()
        create_default_goals()
        create_default_skills()
        
        # Step 4: Verify configuration
        if verify_configuration():
            print("\n" + "=" * 50)
            print("Fresh startup completed successfully!")
            print("Settings file properly configured")
            print("All knowledge files created with cross-referencing")
            print("Configuration verified and working")
            print("\nCARL is ready to start!")
            return True
        else:
            print("\nConfiguration verification failed!")
            return False
            
    except Exception as e:
        print(f"\nError during fresh startup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
