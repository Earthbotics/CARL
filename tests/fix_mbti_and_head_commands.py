#!/usr/bin/env python3
"""
Fix MBTI Type and Test Head Commands
====================================

This script addresses two issues:
1. Fixes the MBTI type loading to properly set INTP
2. Tests head command execution to ensure Script Collection commands work
"""

import json
import os
import configparser
from datetime import datetime

def fix_mbti_type():
    """Fix the MBTI type in the settings file."""
    print("🔧 Fixing MBTI type...")
    
    # Check if settings file exists
    settings_file = "settings_current.ini"
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    # Read current settings
    config = configparser.ConfigParser()
    config.read(settings_file)
    
    # Check current MBTI type
    current_type = config.get('personality', 'type', fallback='ISFP')
    print(f"📋 Current MBTI type: {current_type}")
    
    if current_type != 'INTP':
        # Update to INTP
        if 'personality' not in config:
            config.add_section('personality')
        
        config.set('personality', 'type', 'INTP')
        
        # Write updated settings
        with open(settings_file, 'w') as f:
            config.write(f)
        
        print(f"✅ Updated MBTI type from {current_type} to INTP")
        return True
    else:
        print(f"✅ MBTI type is already set to INTP")
        return True

def test_head_commands():
    """Test head command execution by checking skill files and action system."""
    print("\n🔧 Testing head commands...")
    
    # Check head_yes skill file
    head_yes_file = "skills/head_yes.json"
    if os.path.exists(head_yes_file):
        with open(head_yes_file, 'r') as f:
            skill_data = json.load(f)
        
        command_type = skill_data.get('command_type')
        duration_type = skill_data.get('duration_type')
        
        print(f"📋 head_yes skill file:")
        print(f"   - command_type: {command_type}")
        print(f"   - duration_type: {duration_type}")
        
        if command_type == "ScriptCollection" and duration_type == "3000ms":
            print("✅ head_yes skill file is correctly configured")
        else:
            print("❌ head_yes skill file has incorrect configuration")
            return False
    else:
        print(f"❌ head_yes skill file not found")
        return False
    
    # Check head_no skill file
    head_no_file = "skills/head_no.json"
    if os.path.exists(head_no_file):
        with open(head_no_file, 'r') as f:
            skill_data = json.load(f)
        
        command_type = skill_data.get('command_type')
        duration_type = skill_data.get('duration_type')
        
        print(f"📋 head_no skill file:")
        print(f"   - command_type: {command_type}")
        print(f"   - duration_type: {duration_type}")
        
        if command_type == "ScriptCollection" and duration_type == "3000ms":
            print("✅ head_no skill file is correctly configured")
        else:
            print("❌ head_no skill file has incorrect configuration")
            return False
    else:
        print(f"❌ head_no skill file not found")
        return False
    
    return True

def test_action_system_integration():
    """Test that the action system can properly read command types."""
    print("\n🔧 Testing action system integration...")
    
    try:
        from action_system import ActionSystem
        
        # Create a mock action system
        action_system = ActionSystem(ez_robot=None)
        
        # Test head_yes command
        command_type, duration_type = action_system._get_skill_command_info("head_yes")
        print(f"📋 Action system head_yes:")
        print(f"   - command_type: {command_type}")
        print(f"   - duration_type: {duration_type}")
        
        if command_type == "ScriptCollection" and duration_type == "3000ms":
            print("✅ Action system correctly reads head_yes command type")
        else:
            print("❌ Action system incorrectly reads head_yes command type")
            return False
        
        # Test head_no command
        command_type, duration_type = action_system._get_skill_command_info("head_no")
        print(f"📋 Action system head_no:")
        print(f"   - command_type: {command_type}")
        print(f"   - duration_type: {duration_type}")
        
        if command_type == "ScriptCollection" and duration_type == "3000ms":
            print("✅ Action system correctly reads head_no command type")
        else:
            print("❌ Action system incorrectly reads head_no command type")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing action system: {e}")
        return False

def test_judgment_system_mbti():
    """Test that the judgment system properly loads INTP cognitive functions."""
    print("\n🔧 Testing judgment system MBTI...")
    
    try:
        from judgment_system import JudgmentSystem
        
        # Create judgment system
        judgment_system = JudgmentSystem()
        
        # Check MBTI type
        print(f"📋 Judgment system MBTI type: {judgment_system.mbti_type}")
        
        if judgment_system.mbti_type != 'INTP':
            print("❌ Judgment system MBTI type is not INTP")
            return False
        
        # Check cognitive functions
        cognitive_functions = judgment_system.cognitive_functions
        dominant_function = cognitive_functions.get('dominant')
        
        if dominant_function:
            function_name, effectiveness = dominant_function
            print(f"📋 Dominant function: {function_name} (effectiveness: {effectiveness})")
            
            if function_name == 'Ti':
                print("✅ Judgment system correctly identifies Ti as dominant function for INTP")
                return True
            else:
                print(f"❌ Judgment system incorrectly identifies {function_name} as dominant function")
                return False
        else:
            print("❌ No dominant function found")
            return False
        
    except Exception as e:
        print(f"❌ Error testing judgment system: {e}")
        return False

def main():
    """Run all tests and fixes."""
    print("🧪 Fixing MBTI Type and Testing Head Commands")
    print("=" * 50)
    
    # Fix MBTI type
    mbti_fixed = fix_mbti_type()
    
    # Test head commands
    head_commands_ok = test_head_commands()
    
    # Test action system integration
    action_system_ok = test_action_system_integration()
    
    # Test judgment system MBTI
    judgment_system_ok = test_judgment_system_mbti()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"   MBTI type fixed: {'✅ YES' if mbti_fixed else '❌ NO'}")
    print(f"   Head commands configured: {'✅ YES' if head_commands_ok else '❌ NO'}")
    print(f"   Action system integration: {'✅ YES' if action_system_ok else '❌ NO'}")
    print(f"   Judgment system MBTI: {'✅ YES' if judgment_system_ok else '❌ NO'}")
    
    all_passed = mbti_fixed and head_commands_ok and action_system_ok and judgment_system_ok
    
    if all_passed:
        print("\n🎉 All tests passed! The system should now work correctly.")
        print("\n💡 Next steps:")
        print("   1. Restart CARL to load the new MBTI type")
        print("   2. Test head movement commands with EZ-Robot")
        print("   3. Check that INTP cognitive functions are working")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 