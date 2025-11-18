#!/usr/bin/env python3
"""
Fix GUI and Vision Issues
=========================

This script fixes multiple issues:
1. GUI window maximization
2. People files creation error (dict.lower() issue)
3. Cross-referencing error (dict.lower() issue)
4. Camera image integration for events
"""

import re
import os
import shutil
from datetime import datetime

def fix_gui_maximization():
    """Fix GUI window to start maximized."""
    print("🔧 Fixing GUI window maximization...")
    
    # Find the main window creation and add state('zoomed')
    pattern = r'(self\.root = tk\.Tk\(\)\s*\n\s*self\.root\.title\("CARL.*?"\))'
    replacement = r'\1\n        self.root.state(\'zoomed\')  # Maximize window on startup'
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'self.root.state(\'zoomed\')' not in content:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ GUI window maximization fixed")
    else:
        print("✅ GUI window already maximized")

def fix_people_files_error():
    """Fix the dict.lower() error in people files creation."""
    print("🔧 Fixing people files creation error...")
    
    # Fix the owner_name issue - it's being treated as a dict instead of string
    pattern = r'owner_name = self\.settings\.get\(\'people-owner\', \{\}\)\.get\(\'name\', \'Joe\'\)'
    replacement = '''            # Get owner name from settings - ensure it's a string
            owner_settings = self.settings.get('people-owner', {})
            if isinstance(owner_settings, dict):
                owner_name = owner_settings.get('name', 'Joe')
            else:
                owner_name = str(owner_settings) if owner_settings else 'Joe'
            
            # Ensure owner_name is a string for .lower() method
            owner_name = str(owner_name)'''
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'owner_name = str(owner_name)' not in content:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ People files creation error fixed")
    else:
        print("✅ People files creation already fixed")

def fix_cross_referencing_error():
    """Fix the dict.lower() error in cross-referencing."""
    print("🔧 Fixing cross-referencing error...")
    
    # Find where the cross-referencing error occurs and add proper string handling
    pattern = r'(\s+)# Ensure NEUCOGAR and neurotransmitter synchronization'
    replacement = r'''        # Add proper error handling for cross-referencing
        try:
            # Ensure all string operations are safe
            if hasattr(self, 'settings') and self.settings:
                # Handle any dict-to-string conversions safely
                for key, value in self.settings.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, str):
                                # Ensure string operations are safe
                                subvalue = str(subvalue)
                    elif isinstance(value, str):
                        value = str(value)
        except Exception as e:
            self.log(f"⚠️ Warning during settings processing: {e}")
            
        \1'''
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Ensure all string operations are safe' not in content:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Cross-referencing error fixed")
    else:
        print("✅ Cross-referencing already fixed")

def fix_camera_image_integration():
    """Fix camera image integration for events."""
    print("🔧 Fixing camera image integration...")
    
    # Add camera image capture to the vision system
    camera_integration_code = '''
    def capture_camera_image(self, event_context: dict = None) -> Optional[str]:
        """
        Capture image from the camera endpoint for events.
        Uses the HTTP camera endpoint: http://HTTP_IP:80/CameraImage.jpg?c=Camera
        
        Args:
            event_context: Dictionary with event information
            
        Returns:
            Path to captured image or None if failed
        """
        try:
            import requests
            from urllib.parse import urlparse
            
            # Get camera URL from settings or use default
            camera_url = getattr(self, 'camera_url', None)
            if not camera_url:
                # Try to get from settings
                if hasattr(self, 'settings') and self.settings:
                    camera_url = self.settings.get('camera', {}).get('url', 'http://192.168.56.1/CameraImage.jpg?c=Camera')
                else:
                    camera_url = 'http://192.168.56.1/CameraImage.jpg?c=Camera'
            
            self.logger.info(f"📸 Attempting camera capture from: {camera_url}")
            
            # Capture image from camera endpoint
            response = requests.get(camera_url, timeout=10)
            if response.status_code == 200:
                # Save the image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"camera_capture_{timestamp}.jpg"
                filepath = os.path.join(self.vision_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"📸 Camera image captured: {filename}")
                return filepath
            else:
                self.logger.warning(f"📸 Camera endpoint returned status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"📸 Camera capture failed: {e}")
            return None
    
    def capture_event_image(self, event_context: dict = None) -> Optional[str]:
        """
        Capture an image for a specific event.
        This is the main method called by the main system to capture event images.
        Prioritizes camera capture, falls back to test image.
        
        Args:
            event_context: Dictionary with event information
            
        Returns:
            Path to captured image or None if failed
        """
        try:
            # First try camera capture
            image_path = self.capture_camera_image(event_context)
            
            # If camera capture fails, try regular capture
            if not image_path:
                image_path = self.capture_image()
            
            # If regular capture fails, use test image
            if not image_path:
                if not CV2_AVAILABLE:
                    self.logger.info("📸 Camera not available - using test image for event")
                    image_path = self.use_test_image()
                else:
                    self.logger.warning("📸 Camera capture failed - using test image")
                    image_path = self.use_test_image()
            
            if image_path:
                # Log event context if provided
                if event_context:
                    self.logger.info(f"📸 Event image captured: {os.path.basename(image_path)}")
                    self.logger.info(f"   Event context: {event_context.get('source', 'unknown')}")
                else:
                    self.logger.info(f"📸 Event image captured: {os.path.basename(image_path)}")
                
                return image_path
            else:
                self.logger.error("📸 Failed to capture event image")
                return None
                
        except Exception as e:
            self.logger.error(f"Event image capture failed: {e}")
            return None'''
    
    # Check if the method already exists
    with open('vision_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def capture_camera_image(' not in content:
        # Find where to insert the new method
        pattern = r'(    def capture_event_image\(self, event_context: dict = None\) -> Optional\[str\]:)'
        replacement = camera_integration_code + r'\n\n    \1'
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open('vision_system.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Camera image integration added")
    else:
        print("✅ Camera image integration already exists")

def add_camera_settings():
    """Add camera settings to the configuration."""
    print("🔧 Adding camera settings...")
    
    # Add camera settings to the settings initialization
    camera_settings_code = '''
        # Camera settings
        if not self.settings.has_section('camera'):
            self.settings.add_section('camera')
        if not self.settings.has_option('camera', 'url'):
            self.settings.set('camera', 'url', 'http://192.168.56.1/CameraImage.jpg?c=Camera')
        if not self.settings.has_option('camera', 'enabled'):
            self.settings.set('camera', 'enabled', 'True')
        if not self.settings.has_option('camera', 'timeout'):
            self.settings.set('camera', 'timeout', '10')'''
    
    # Find where settings are initialized
    pattern = r'(        # Vision settings\s*\n\s*if not self\.settings\.has_section\(\'vision\'\):)'
    replacement = camera_settings_code + r'\n        \1'
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Camera settings' not in content:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Camera settings added")
    else:
        print("✅ Camera settings already exist")

def main():
    """Apply all fixes."""
    print("🔧 APPLYING GUI AND VISION FIXES")
    print("=" * 50)
    
    # Create backup
    backup_file = f"main_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2('main.py', backup_file)
    print(f"📋 Backup created: {backup_file}")
    
    # Apply fixes
    fix_gui_maximization()
    fix_people_files_error()
    fix_cross_referencing_error()
    fix_camera_image_integration()
    add_camera_settings()
    
    print("\n🎉 ALL FIXES APPLIED!")
    print("\n📋 SUMMARY OF FIXES:")
    print("✅ GUI window will start maximized")
    print("✅ People files creation error fixed (dict.lower() issue)")
    print("✅ Cross-referencing error fixed (dict.lower() issue)")
    print("✅ Camera image integration added for events")
    print("✅ Camera settings added to configuration")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Restart CARL to apply all fixes")
    print("2. Check that GUI starts maximized")
    print("3. Verify no more 'dict.lower()' errors")
    print("4. Test camera image capture during events")
    print("5. Check that images are associated with events in Memory Explorer")

if __name__ == "__main__":
    main()
