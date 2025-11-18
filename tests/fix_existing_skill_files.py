#!/usr/bin/env python3
"""
Fix Existing Skill Files
========================

This script checks all existing skill files and adds the command_type and duration_type
fields if they are missing. This ensures that even skill files created before the
command type system was implemented will work correctly.
"""

import json
import os
import glob
from datetime import datetime

# Define command types and duration types
SCRIPT_COMMANDS_3000MS = [
    "walk", "look_forward", "look_down", "head_yes", "head_no"
]

SCRIPT_COMMANDS_AUTO_STOP = [
    "arm_right_down", "arm_right_down_sitting", "point_arm_right"
]

def get_command_type_info(skill_name: str) -> tuple[str, str]:
    """Get command type and duration type for a skill."""
    if skill_name in SCRIPT_COMMANDS_3000MS:
        return "ScriptCollection", "3000ms"
    elif skill_name in SCRIPT_COMMANDS_AUTO_STOP:
        return "ScriptCollection", "auto_stop"
    else:
        return "AutoPositionAction", "auto_stop"

def fix_skill_file(file_path: str) -> bool:
    """Fix a single skill JSON file by adding missing command_type and duration_type fields."""
    try:
        # Read the current skill file
        with open(file_path, 'r', encoding='utf-8') as f:
            skill_data = json.load(f)
        
        # Get the skill name
        skill_name = skill_data.get('Name', '').lower()
        
        # Check if command_type and duration_type fields are missing
        needs_update = False
        
        if 'command_type' not in skill_data:
            needs_update = True
            command_type, duration_type = get_command_type_info(skill_name)
            skill_data['command_type'] = command_type
            skill_data['duration_type'] = duration_type
            skill_data['command_type_updated'] = datetime.now().isoformat()
            print(f"✅ Added missing fields to {file_path}: {command_type} ({duration_type})")
        elif 'duration_type' not in skill_data:
            needs_update = True
            command_type, duration_type = get_command_type_info(skill_name)
            skill_data['duration_type'] = duration_type
            skill_data['command_type_updated'] = datetime.now().isoformat()
            print(f"✅ Added missing duration_type to {file_path}: {duration_type}")
        else:
            print(f"✅ {file_path}: Already has command type fields")
        
        # Write the updated file if changes were made
        if needs_update:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(skill_data, f, indent=4, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all skill JSON files in the skills directory."""
    skills_dir = "skills"
    
    if not os.path.exists(skills_dir):
        print(f"❌ Skills directory not found: {skills_dir}")
        return
    
    # Find all JSON files in the skills directory
    skill_files = glob.glob(os.path.join(skills_dir, "*.json"))
    
    if not skill_files:
        print(f"❌ No skill JSON files found in {skills_dir}")
        return
    
    print(f"🔧 Checking {len(skill_files)} skill files for missing command type fields...")
    print()
    
    success_count = 0
    total_count = len(skill_files)
    
    for file_path in skill_files:
        if fix_skill_file(file_path):
            success_count += 1
    
    print()
    print(f"📊 Summary:")
    print(f"   Total files: {total_count}")
    print(f"   Successfully processed: {success_count}")
    print(f"   Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 All skill files are now properly configured!")
    else:
        print("⚠️  Some files failed to process. Check the errors above.")

if __name__ == "__main__":
    main() 