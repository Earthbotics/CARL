#!/usr/bin/env python3
"""
Simple verification script for enhanced vision memory display
"""

def verify_enhancements():
    print("🔍 Verifying Enhanced Vision Memory Display Enhancements")
    print("=" * 55)
    
    try:
        # Import main module
        import main
        print("✅ main.py imports successfully")
        
        # Check if methods exist
        methods = [
            '_format_vision_memory_details',
            '_format_event_memory_details', 
            '_perform_openai_object_detection',
            '_create_vision_memory_file',
            '_on_memory_select'
        ]
        
        for method in methods:
            if hasattr(main.PersonalityBotApp, method):
                print(f"✅ {method} exists")
            else:
                print(f"❌ {method} missing")
                return False
        
        # Check OpenAI prompt enhancement
        import inspect
        source = inspect.getsource(main.PersonalityBotApp._perform_openai_object_detection)
        if "pleasure_detected" in source:
            print("✅ Enhanced OpenAI prompt with pleasure_detected found")
        else:
            print("❌ Enhanced OpenAI prompt not found")
            return False
        
        # Check vision memory formatting enhancement
        source = inspect.getsource(main.PersonalityBotApp._format_vision_memory_details)
        if "ENHANCED ANALYSIS RESULTS" in source:
            print("✅ Enhanced vision memory formatting found")
        else:
            print("❌ Enhanced vision memory formatting not found")
            return False
        
        # Check event memory formatting enhancement
        source = inspect.getsource(main.PersonalityBotApp._format_event_memory_details)
        if "VISION INFORMATION" in source:
            print("✅ Enhanced event memory formatting with vision section found")
        else:
            print("❌ Enhanced event memory formatting not found")
            return False
        
        print("\n🎉 All enhancements verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_enhancements()
    exit(0 if success else 1)
