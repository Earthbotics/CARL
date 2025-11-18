#!/usr/bin/env python3
"""
Add GUI Maximization
====================

Simple script to add window maximization to the GUI.
"""

def add_gui_maximization():
    """Add window maximization to the GUI."""
    print("🔧 Adding GUI window maximization...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the first occurrence of init_app method and add maximization
    pattern = r'(def init_app\(self\):\s*\n\s*self\.title\("PersonalityBot Version 5\.16\.3"\))'
    replacement = r'\1\n        self.state(\'zoomed\')  # Maximize window on startup'
    
    if 'self.state(\'zoomed\')' not in content:
        new_content = content.replace(
            'def init_app(self):\n        self.title("PersonalityBot Version 5.16.3")',
            'def init_app(self):\n        self.title("PersonalityBot Version 5.16.3")\n        self.state(\'zoomed\')  # Maximize window on startup'
        )
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ GUI window maximization added")
    else:
        print("✅ GUI window already maximized")

if __name__ == "__main__":
    add_gui_maximization()
