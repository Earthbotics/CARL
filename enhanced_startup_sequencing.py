#!/usr/bin/env python3
"""
Enhanced Startup Sequencing System for CARL

This module provides controlled startup sequencing to prevent ARC overload:
1. Staggered command execution during initialization
2. Connection health monitoring during startup
3. Graceful fallback if commands fail
4. Proper timing between startup commands
"""

import time
import threading
from typing import Optional, Dict, List
from enum import Enum
import logging

class StartupPhase(Enum):
    """Startup phases for controlled initialization."""
    CONNECTION_TEST = "connection_test"
    EYE_EXPRESSION = "eye_expression"
    SPEECH_TEST = "speech_test"
    ENHANCED_SYSTEMS = "enhanced_systems"
    COMPLETE = "complete"

class EnhancedStartupSequencing:
    """
    Enhanced startup sequencing with proper rate limiting and error handling.
    """
    
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Startup configuration
        self.startup_delay = 2.0  # seconds between startup commands
        self.connection_test_delay = 1.0  # seconds after connection test
        self.eye_expression_delay = 1.5  # seconds after eye expression
        self.speech_test_delay = 2.0  # seconds after speech test
        
        # Startup tracking
        self.current_phase = None
        self.startup_complete = False
        self.startup_errors = []
        self.startup_log = []
        
        # Connection health
        self.connection_healthy = False
        self.consecutive_failures = 0
        self.max_startup_failures = 3
        
    def log_startup_event(self, phase: str, message: str, success: bool = True):
        """Log startup events for debugging."""
        event = {
            'timestamp': time.time(),
            'phase': phase,
            'message': message,
            'success': success
        }
        self.startup_log.append(event)
        
        if success:
            self.logger.info(f"✅ Startup {phase}: {message}")
        else:
            self.logger.warning(f"❌ Startup {phase}: {message}")
    
    def execute_startup_sequence(self) -> bool:
        """
        Execute the complete startup sequence with proper timing.
        
        Returns:
            True if startup completed successfully, False otherwise
        """
        try:
            self.logger.info("🚀 Starting enhanced startup sequence...")
            
            # Phase 1: Connection Test (with minimal command)
            if not self._execute_connection_test():
                self.logger.error("❌ Connection test failed - aborting startup")
                return False
            
            time.sleep(self.connection_test_delay)
            
            # Phase 2: Eye Expression (if connection successful)
            if self.connection_healthy:
                self._execute_eye_expression_setup()
                time.sleep(self.eye_expression_delay)
            
            # Phase 3: Speech Test (if connection still healthy)
            if self.connection_healthy:
                self._execute_speech_test()
                time.sleep(self.speech_test_delay)
            
            # Phase 4: Enhanced Systems (if all previous phases successful)
            if self.connection_healthy:
                self._execute_enhanced_systems_setup()
            
            # Phase 5: Complete startup
            self.startup_complete = True
            self.current_phase = StartupPhase.COMPLETE
            
            # Note: Stand command removed from startup sequence to prevent errors
            # Stand command can be executed manually when needed
            
            self.logger.info("🎉 Enhanced startup sequence completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Startup sequence failed: {e}")
            return False
    
    def _execute_connection_test(self) -> bool:
        """Execute connection test using Waiting Fidget command to verify HTTP server."""
        try:
            self.current_phase = StartupPhase.CONNECTION_TEST
            self.logger.info("🔍 Testing HTTP server connectivity with Waiting Fidget...")
            
            if not self.main_app or not self.main_app.ez_robot:
                self.log_startup_event("connection_test", "EZ-Robot not available", False)
                return False
            
            # Test HTTP server by attempting Waiting Fidget command
            try:
                test_success = self.main_app.ez_robot.send_auto_position("Waiting Fidget")
                if test_success:
                    self.connection_healthy = True
                    self.main_app.ez_robot_connected = True
                    self.log_startup_event("connection_test", "HTTP server is running - Waiting Fidget command successful", True)
                    return True
                else:
                    self.connection_healthy = False
                    self.main_app.ez_robot_connected = False
                    self.log_startup_event("connection_test", "HTTP server test failed - Waiting Fidget command unsuccessful", False)
                    self.logger.warning("💡 TROUBLESHOOTING TIP: Please manually press the Start button in the HTTP server ARC skill.")
                    self.logger.warning("   - Open ARC (EZ-Robot software)")
                    self.logger.warning("   - Go to 'System' window") 
                    self.logger.warning("   - Make sure 'HTTP Server' is enabled and running")
                    self.logger.warning("   - Press the Start button in the HTTP server skill")
                    return False
            except Exception as http_test_error:
                self.connection_healthy = False
                self.main_app.ez_robot_connected = False
                self.log_startup_event("connection_test", f"HTTP server connectivity test failed: {http_test_error}", False)
                self.logger.warning("💡 TROUBLESHOOTING TIP: Please manually press the Start button in the HTTP server ARC skill.")
                self.logger.warning("   - Open ARC (EZ-Robot software)")
                self.logger.warning("   - Go to 'System' window")
                self.logger.warning("   - Make sure 'HTTP Server' is enabled and running")
                self.logger.warning("   - Press the Start button in the HTTP server skill")
                return False
                
        except Exception as e:
            self.log_startup_event("connection_test", f"Connection test error: {e}", False)
            return False
    
    def _execute_eye_expression_setup(self):
        """Execute eye expression setup with rate limiting."""
        try:
            self.current_phase = StartupPhase.EYE_EXPRESSION
            self.logger.info("👁️ Setting up initial eye expression...")
            
            if not self.main_app or not self.main_app.ez_robot:
                self.log_startup_event("eye_expression", "EZ-Robot not available", False)
                return
            
            # Set eye expression to eyes_joy
            if hasattr(self.main_app, 'enhanced_eye_system') and self.main_app.enhanced_eye_system:
                success = self.main_app.enhanced_eye_system.set_eye_expression("eyes_joy", force=True)
                if success:
                    self.log_startup_event("eye_expression", "Enhanced eye expression set to eyes_joy", True)
                else:
                    self.log_startup_event("eye_expression", "Enhanced eye expression failed", False)
            else:
                # Fallback to original method
                if hasattr(self.main_app, '_update_eye_expression'):
                    self.main_app._update_eye_expression("eyes_joy")
                    self.log_startup_event("eye_expression", "Fallback eye expression set to eyes_joy", True)
                else:
                    self.log_startup_event("eye_expression", "No eye expression method available", False)
                    
        except Exception as e:
            self.log_startup_event("eye_expression", f"Eye expression error: {e}", False)
    
    def _execute_speech_test(self):
        """Execute speech test with rate limiting."""
        try:
            self.current_phase = StartupPhase.SPEECH_TEST
            self.logger.info("🎤 Testing speech system...")
            
            if not self.main_app:
                self.log_startup_event("speech_test", "Main app not available", False)
                return
            
            # Use the existing speech test method
            if hasattr(self.main_app, '_speak_to_computer_speakers'):
                success = self.main_app._speak_to_computer_speakers("Startup speech test successful. I am initializing my knowledge system.")
                if success:
                    self.log_startup_event("speech_test", "Speech test successful", True)
                    
                    # Immediately test body function by running waiting fidget
                    if (self.main_app.ez_robot and 
                        hasattr(self.main_app, 'ez_robot_connected') and 
                        self.main_app.ez_robot_connected):
                        try:
                            # Check if EZ-Robot is actually responsive before testing
                            if hasattr(self.main_app.ez_robot, 'test_connection'):
                                connection_test = self.main_app.ez_robot.test_connection()
                                if not connection_test:
                                    self.log_startup_event("body_function_test", "EZ-Robot connection test failed - skipping body function test", False)
                                    return
                            
                            # Try a simpler command first to test basic functionality
                            try:
                                # Test with a simple command first
                                test_success = self.main_app.ez_robot.send_auto_position("Stop")
                                if not test_success:
                                    self.log_startup_event("body_function_test", "EZ-Robot basic command test failed", False)
                                    return
                            except Exception as test_e:
                                self.log_startup_event("body_function_test", f"EZ-Robot basic command test error: {test_e}", False)
                                return
                            
                            # 🔧 ENHANCEMENT: Try multiple fallback commands with better error handling
                            fidget_commands = ["Waiting Fidget", "Fidget", "Stand", "Stop", "Wave"]
                            fidget_success = False
                            
                            for cmd in fidget_commands:
                                try:
                                    self.logger.info(f"🔧 Trying body function test command: {cmd}")
                                    success = self.main_app.ez_robot.send_auto_position(cmd)
                                    if success:
                                        self.log_startup_event("body_function_test", f"Body function test successful - {cmd} executed", True)
                                        fidget_success = True
                                        break
                                    else:
                                        self.logger.warning(f"⚠️ Command {cmd} failed, trying next...")
                                except Exception as cmd_e:
                                    self.logger.warning(f"⚠️ Command {cmd} error: {cmd_e}, trying next...")
                                    continue
                            
                            if not fidget_success:
                                # 🔧 ENHANCEMENT: Try HTTP command as final fallback
                                try:
                                    self.logger.info("🔧 Trying HTTP command as final fallback...")
                                    http_success = self.main_app.ez_robot.send_auto_position("Stop")
                                    if http_success:
                                        self.log_startup_event("body_function_test", "Body function test successful - HTTP stop command executed", True)
                                    else:
                                        self.log_startup_event("body_function_test", "Body function test failed - all commands unsuccessful, but connection is working", False)
                                except Exception as http_e:
                                    self.log_startup_event("body_function_test", f"Body function test failed - HTTP fallback error: {http_e}", False)
                        except Exception as e:
                            self.log_startup_event("body_function_test", f"Body function test error: {e}", False)
                    else:
                        self.log_startup_event("body_function_test", "EZ-Robot not connected - skipping body function test", False)
                else:
                    self.log_startup_event("speech_test", "Speech test failed", False)
            else:
                self.log_startup_event("speech_test", "No speech test method available", False)
                
        except Exception as e:
            self.log_startup_event("speech_test", f"Speech test error: {e}", False)
    
    def _execute_enhanced_systems_setup(self):
        """Execute enhanced systems setup."""
        try:
            self.current_phase = StartupPhase.ENHANCED_SYSTEMS
            self.logger.info("🎯 Setting up enhanced systems...")
            
            if not self.main_app:
                self.log_startup_event("enhanced_systems", "Main app not available", False)
                return
            
            # Initialize enhanced systems if not already done
            if hasattr(self.main_app, '_initialize_enhanced_systems'):
                self.main_app._initialize_enhanced_systems()
                self.log_startup_event("enhanced_systems", "Enhanced systems initialized", True)
            else:
                self.log_startup_event("enhanced_systems", "No enhanced systems method available", False)
                
        except Exception as e:
            self.log_startup_event("enhanced_systems", f"Enhanced systems error: {e}", False)
    
    def get_startup_stats(self) -> Dict:
        """Get startup statistics."""
        return {
            'startup_complete': self.startup_complete,
            'current_phase': self.current_phase.value if self.current_phase else None,
            'connection_healthy': self.connection_healthy,
            'consecutive_failures': self.consecutive_failures,
            'total_events': len(self.startup_log),
            'successful_events': len([e for e in self.startup_log if e['success']]),
            'failed_events': len([e for e in self.startup_log if not e['success']]),
            'recent_events': self.startup_log[-5:] if self.startup_log else []
        }
    
    def reset_startup(self):
        """Reset startup state for retry."""
        self.startup_complete = False
        self.current_phase = None
        self.startup_errors.clear()
        self.startup_log.clear()
        self.connection_healthy = False
        self.consecutive_failures = 0
        self.logger.info("🔄 Startup state reset for retry") 