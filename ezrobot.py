import requests
import time
import threading
from enum import Enum
from typing import Optional, Callable
from collections import deque

### 
### ControlCommand("Script Collection", "ScriptStart", "sayesb")



class EZRobotSkills(Enum):
    Bow = "Bow"
    Dance = "Disco Dance"  # Fixed: Added space
    Fly = "Fly"
    Getup = "Getup"
    Head_Bob = "Head_Bob"
    Headstand = "Headstand"
    Jump_Jack = "Jump Jack"  # Fixed: Added space
    Kick = "Kick"
    Point = "Point"
    Pushups = "Pushups"
    Sit_Down = "Sit Down"  # Fixed: Added space
    Sit_Wave = "Sit Wave"  # Fixed: Added space
    Situps = "Situps"
    Stand_From_Sit = "Stand From Sit"  # Fixed: Added spaces
    Stop = "Stop"
    Summersault = "Summersault"
    Thinking = "Thinking"
    Walk = "Walk"
    Wave = "Wave"
    CameraSnapshot = "Camera Snapshot"  # Fixed: Added space
    # New head movement skills
    Head_No = "head_no"
    Head_Yes = "head_yes"
    Look_Forward = "look_forward"
    Look_Down = "look_down"
    Look_Left = "look_left"
    Look_Right = "look_right"
    # New eye expression for waiting state
    Eyes_Waiting = "eyes_waiting"

class EZRobotEyeExpressions(Enum):
    """Eye RGB expressions for human-like behavior."""
    EYES_CLOSED = "eyes_closed"
    EYES_DOWN = "eyes_down"
    EYES_LEFT = "eyes_left"
    EYES_OPEN = "eyes_open"
    EYES_RIGHT = "eyes_right"
    EYES_UP = "eyes_up"
    EYES_ANGER = "eyes_anger"
    EYES_SURPRISE = "eyes_surprise"
    EYES_FEAR = "eyes_fear"
    EYES_DISGUST = "eyes_disgust"
    EYES_SAD = "eyes_sad"
    EYES_JOY = "eyes_joy"
    EYES_WAITING = "eyes_waiting"  # New: For waiting state during processing
    EYES_SPIN = "eyes_spin"  # New: For cognitive processing phases

class EZRwindowName(Enum):
    Auto_Position = "Auto Position"
    Script_Collection = "Script Collection"
    Camera = "Camera"
    RGB_Animator = "RGB Animator"
    Camera_Snapshot = "Camera Snapshot"
    Bing_Speech_Recognition = "Bing Speech Recognition"

class EZRccParameter(Enum):
    AutoPositionAction = "AutoPositionAction"
    AutoPositionFrame = "AutoPositionFrame"
    ScriptStart = "ScriptStart"
    ScriptStartWait = "ScriptStartWait"
    StartListening = "StartListening"
    StopListening = "StopListening"

class EZRobot:
    def __init__(self, base_address="http://192.168.56.1/Exec?password=admin&script=ControlCommand("):
        self.base_url = base_address
        self.is_connected = False
        self.speech_recognition_active = False
        self.speech_callback = None
        self.speech_thread = None
        self.last_speech_text = ""
        self.bing_speech_variable = "$BingSpeech"
        
        # Eye state management
        self.previous_eye_expression = None
        self.is_in_waiting_state = False
        
        # Enhanced rate limiting for HTTP calls to prevent overwhelming JD's ARC controller
        self.last_request_time = 0
        self.min_request_interval = 1.5  # Increased to 1.5 seconds minimum between requests
        self.max_request_interval = 5.0  # Increased maximum interval for adaptive rate limiting
        self.request_history = deque(maxlen=10)  # Track last 10 request response times
        self.adaptive_interval = 1.5  # Increased current adaptive interval
        self.consecutive_failures = 0  # Track consecutive failures
        self.max_consecutive_failures = 3  # Reset adaptive interval after this many failures
        
        # Duplicate request prevention
        self.last_request_url = None
        self.last_request_time_strict = 0
        self.min_duplicate_interval = 0.5  # Reduced to 0.5 seconds for more responsive eye expressions
        
        # Request queuing to prevent overlapping requests
        self.request_lock = threading.Lock()
        self.request_queue = deque()
        self.processing_request = False
        
        # Connection health monitoring
        self.last_successful_request = 0
        self.connection_health_score = 1.0  # 1.0 = perfect, 0.0 = poor
        
        # Connection recovery system
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        self.recovery_cooldown = 30.0  # 30 seconds between recovery attempts
        self.last_recovery_attempt = 0
        
    def test_connection(self) -> bool:
        """Test connection to EZ-Robot and initialize if successful."""
        try:
            # Test basic connection using a minimal system status command
            # This avoids sending movement commands that could overwhelm ARC
            test_url = f'{self.base_url}%22System%22,%22GetStatus%22,%22%22)'
            response = requests.get(test_url, timeout=5)
            response.raise_for_status()
            
            self.is_connected = True
            print("EZ-Robot connection successful!")
            
            # Initialize JD without sending movement commands
            self._initialize_jd()
            
            return True
            
        except requests.RequestException as ex:
            self.is_connected = False
            print(f"EZ-Robot connection failed: {ex}")
            print("💡 TROUBLESHOOTING TIP: Please check if the HTTP server has been started in ARC.")
            print("   - Open ARC (EZ-Robot software)")
            print("   - Go to 'System' window")
            print("   - Make sure 'HTTP Server' is enabled and running")
            print("   - Verify JD is powered on and connected to the network")
            return False
    
    def _initialize_jd(self):
        """Initialize JD when connection is established."""
        try:
            # Initialize JD without hardcoded actions - let cognitive processing decide
            print("Initializing JD - ready for cognitive processing...")
            
            print("JD initialization complete!")
            
        except Exception as e:
            print(f"Error during JD initialization: {e}")
    
    def start_speech_recognition(self, callback: Callable[[str], None]):
        """Start continuous speech recognition with callback."""
        if not self.is_connected:
            print("Cannot start speech recognition - EZ-Robot not connected")
            return False
        
        # 🔧 FIX: Prevent starting speech recognition if already active
        if self.speech_recognition_active:
            print("⚠️ Speech recognition already active - not starting again")
            return True
            
        self.speech_callback = callback
        self.speech_recognition_active = True
        
        # Start speech recognition thread
        self.speech_thread = threading.Thread(target=self._speech_recognition_loop, daemon=True)
        self.speech_thread.start()
        
        print("Speech recognition started - CARL is now listening!")
        return True
    
    def stop_speech_recognition(self):
        """Stop speech recognition."""
        print("🔍 Stopping speech recognition...")
        self.speech_recognition_active = False
        
        # 🔧 FIX: Send stop command to EZ-Robot to ensure listening stops
        try:
            self._send_speech_command(EZRccParameter.StopListening)
            print("🔍 Sent stop listening command to EZ-Robot")
        except Exception as e:
            print(f"⚠️ Error sending stop command: {e}")
        
        # Wait for speech thread to finish
        if self.speech_thread and self.speech_thread.is_alive():
            print("🔍 Waiting for speech thread to finish...")
            self.speech_thread.join(timeout=5)  # Increased timeout to 5 seconds
            if self.speech_thread.is_alive():
                print("⚠️ Speech thread did not stop within timeout")
            else:
                print("✅ Speech thread stopped successfully")
        
        print("Speech recognition stopped")
    
    def _speech_recognition_loop(self):
        """Single-shot speech recognition - start once, process, then stop."""
        print("🔍 Starting single-shot speech recognition...")
        
        try:
            # Step 1: Start listening via HTTP command
            print("🔍 Starting listening via HTTP command...")
            start_result = self._send_speech_command(EZRccParameter.StartListening)
            if start_result is None:
                print("❌ Failed to start listening")
                return
            
            # Step 2: Wait for Bing API to process speech (10 seconds)
            print("🔍 Waiting for Bing API to process speech (10 seconds)...")
            for _ in range(10):  # 10 seconds, checking every second
                if not self.speech_recognition_active:
                    print("🔍 Speech recognition stopped during Bing API wait")
                    return
                time.sleep(1)
            
            # Step 3: Speech is handled via HTTP responses from ARC
            print("🔍 Speech recognition now uses HTTP responses from ARC")
            print("🔍 Waiting for speech data via Flask server...")
            
            # Step 4: Wait for speech data to be received via Flask
            for _ in range(5):  # 5 seconds, checking every second
                if not self.speech_recognition_active:
                    print("🔍 Speech recognition stopped during Flask wait")
                    return
                time.sleep(1)
            
            # Step 5: Stop listening after processing
            print("🔍 Stopping listening after single-shot processing...")
            stop_result = self._send_speech_command(EZRccParameter.StopListening)
            if stop_result is None:
                print("❌ Failed to stop listening")
            
            print("🔍 Single-shot speech recognition completed - not restarting automatically")
            
        except Exception as e:
            print(f"Error in single-shot speech recognition: {e}")
            # Ensure we stop listening even if there's an error
            try:
                self._send_speech_command(EZRccParameter.StopListening)
            except:
                pass
        
        print("🔍 Single-shot speech recognition finished")
    
    def _simulate_speech_capture(self) -> str:
        """Capture actual speech from Bing Speech Recognition using getBingSpeech script."""
        try:
            # The getBingSpeech script handles the entire capture cycle
            captured_text = self._get_speech_variable()
            
            # The script should automatically clear the variable after capture
            return captured_text.strip() if captured_text else ""
            
        except Exception as e:
            print(f"Error capturing speech: {e}")
            return ""
    
    def test_arc_endpoints(self):
        """Test various ARC API endpoints to find variable access."""
        print("Testing ARC API endpoints...")
        test_endpoints = [
            "Variables",
            "Global Variables", 
            "System",
            "Script Collection",
            "Bing Speech Recognition"
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f'{self.base_url}%22{endpoint}%22,%22Get%22,%22test%22)'
                response = requests.get(url, timeout=2)
                print(f"Endpoint {endpoint}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"Endpoint {endpoint}: Error - {e}")
    
    def test_speech_variable_access(self):
        """Test access to the Bing Speech variable."""
        print("Testing Bing Speech variable access...")
        
        # Test getting the variable
        print("Testing getBingSpeech script...")
        try:
            result = self.execute_script("getBingSpeech")
            print(f"getBingSpeech result: '{result}'")
        except Exception as e:
            print(f"getBingSpeech failed: {e}")
        
        # Test clearing the variable
        # DISABLED: clearBingSpeech functionality disabled
        # print("Testing clearBingSpeech script...")
        # try:
        #     result = self.execute_script("clearBingSpeech")
        #     print(f"clearBingSpeech result: '{result}'")
        # except Exception as e:
        #     print(f"clearBingSpeech failed: {e}")
        
        # Test direct variable access
        print("Testing direct variable access...")
        try:
            result = self._get_speech_variable()
            print(f"Direct access result: '{result}'")
        except Exception as e:
            print(f"Direct access failed: {e}")
    
    def setup_speech_scripts(self):
        """Display the required scripts for ARC speech recognition setup."""
        print("=== ARC Speech Recognition Scripts Setup ===")
        print("Note: ScriptStart getBingSpeech methods have been removed.")
        print("Speech recognition now uses HTTP responses from ARC.")
        
        print("\n=== Setup Instructions ===")
        print("1. Open ARC (EZ-Robot software)")
        print("2. Go to 'Bing Speech Recognition' window")
        print("3. Configure Bing Speech API credentials")
        print("4. Make sure the $BingSpeech variable exists in your Variables window")
        print("5. Ensure Bing Speech Recognition is properly configured")
        print("\nSpeech recognition now uses HTTP responses instead of script calls.")
    
    # REMOVED: execute_script method - no longer needed with HTTP responses
    
    def _send_speech_command(self, command: EZRccParameter):
        """Send speech recognition command."""
        command_script = f'%22{EZRwindowName.Bing_Speech_Recognition.value}%22,%22{command.value}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)
    
    # REMOVED: _get_speech_variable method - no longer needed with HTTP responses
    
    def _clear_speech_variable(self):
        """Clear the Bing Speech variable using clearBingSpeech script."""
        # DISABLED: clearBingSpeech functionality disabled
        print("🔍 clearBingSpeech functionality has been disabled")
        # try:
        #     # Execute the clearBingSpeech script
        #     clear_script_url = f'{self.base_url}%22Script%20Collection%22,%22ScriptStart%22,%22clearBingSpeech%22)'
        #     response = requests.get(clear_script_url, timeout=5)
        #     
        #     if response.status_code == 200:
        #         print("🔍 clearBingSpeech script executed successfully")
        #     else:
        #         print(f"🔍 clearBingSpeech script failed with status: {response.status_code}")
        #         
        # except Exception as e:
        #     print(f"Error executing clearBingSpeech script: {e}")

    def send(self, window_name, param, skill_or_eye_movement):
        command_script = f'%22{window_name.value.replace("_", "%20")}%22,%22{param.value}%22,%22{skill_or_eye_movement.value.replace("_", "%20")}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)

    def _coerce_command_name(self, command) -> str:
        """Accept either Enum or string for command names and return the string name."""
        return command.value if hasattr(command, 'value') else str(command)

    def send_auto_position(self, command):
        """Send auto position command with enhanced rate limiting for skill execution."""
        import time
        
        cmd_name = self._coerce_command_name(command)
        
        # Special handling for critical position commands
        critical_commands = ["Sit Down", "Stand From Sit", "Stop"]
        is_critical = cmd_name in critical_commands
        
        # Enhanced rate limiting for skill execution to prevent HTTP spam
        current_time = time.time()
        if hasattr(self, 'last_skill_execution_time'):
            time_since_last_skill = current_time - self.last_skill_execution_time
            
            # Use shorter interval for critical commands
            min_interval = 0.5 if is_critical else 2.0
            
            if time_since_last_skill < min_interval:
                print(f"⏳ Skill execution rate limited: {cmd_name} (last skill {time_since_last_skill:.1f}s ago)")
                if is_critical:
                    print(f"🔄 Overriding rate limit for critical command: {cmd_name}")
                else:
                    return None
        
        self.last_skill_execution_time = current_time
        command_script = f'%22Auto%20Position%22,AutoPositionAction,%22{cmd_name}%22'
        request_url = f'{self.base_url}{command_script})'
        result = self._send_request(request_url)
        
        # Check if the command failed due to missing action
        if result and "Error: ControlCommand Error for 'Auto Position'" in result:
            print(f"⚠️ Auto Position action '{cmd_name}' not configured in EZ-Robot")
            print(f"💡 Please configure the action in ARC: ControlCommand('Auto Position', 'AutoPositionAction', '{cmd_name}')")
            return None
        
        return result

    def send_auto_position_wait(self, command):
        """Send an auto position command that waits for completion before multitasking."""
        # Note: AutoPositionActionWait is not supported by EZ-Robot, using AutoPositionAction instead
        cmd_name = self._coerce_command_name(command)
        command_script = f'%22Auto%20Position%22,AutoPositionAction,%22{cmd_name}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)

    def send_auto_frame(self, command):
        cmd_name = self._coerce_command_name(command)
        command_script = f'%22Auto%20Position%22,AutoPositionFrame,%22{cmd_name}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)

    def send_auto_script(self, command):
        cmd_name = self._coerce_command_name(command)
        command_script = f'%22Script%20Collection%22,%22ScriptStart%22,%22{cmd_name}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)

    def send_script_wait(self, command):
        """Send a script command with ScriptStartWait parameter."""
        cmd_name = self._coerce_command_name(command)
        command_script = f'%22Script%20Collection%22,%22ScriptStartWait%22,%22{cmd_name}%22'
        request_url = f'{self.base_url}{command_script})'
        return self._send_request(request_url)

    def send_eye_expression(self, eye_expression: EZRobotEyeExpressions):
        """Send an eye RGB expression command with suppression of redundant repeats."""
        # Suppress if same expression is already active
        if hasattr(self, 'current_eye_expression') and self.current_eye_expression == eye_expression:
            print(f"👁️ Eye expression unchanged; skipping duplicate send: {eye_expression.value}")
            return "SKIPPED"

        command_script = f'%22RGB%20Animator%22,AutoPositionAction,%22{eye_expression.value}%22'
        request_url = f'{self.base_url}{command_script})'
        result = self._send_request(request_url)
        if result is not None:
            # Update current eye state tracking
            self.current_eye_expression = eye_expression
        return result

    def send_head_no(self):
        """Send head_no script command."""
        return self.send_script_wait(EZRobotSkills.Head_No)

    def send_head_yes(self):
        """Send head_yes script command."""
        return self.send_script_wait(EZRobotSkills.Head_Yes)

    def set_eye_expression(self, emotion: str):
        """Set eye expression based on emotional state."""
        emotion_to_eye = {
            'joy': EZRobotEyeExpressions.EYES_JOY,
            'happiness': EZRobotEyeExpressions.EYES_JOY,
            'happy': EZRobotEyeExpressions.EYES_JOY,
            'anger': EZRobotEyeExpressions.EYES_ANGER,
            'angry': EZRobotEyeExpressions.EYES_ANGER,
            'fear': EZRobotEyeExpressions.EYES_FEAR,
            'afraid': EZRobotEyeExpressions.EYES_FEAR,
            'surprise': EZRobotEyeExpressions.EYES_SURPRISE,
            'surprised': EZRobotEyeExpressions.EYES_SURPRISE,
            'disgust': EZRobotEyeExpressions.EYES_DISGUST,
            'disgusted': EZRobotEyeExpressions.EYES_DISGUST,
            'sadness': EZRobotEyeExpressions.EYES_SAD,
            'sad': EZRobotEyeExpressions.EYES_SAD,
            'default': EZRobotEyeExpressions.EYES_OPEN,
            'neutral': EZRobotEyeExpressions.EYES_OPEN
        }
        
        eye_expression = emotion_to_eye.get(emotion.lower(), EZRobotEyeExpressions.EYES_OPEN)
        return self.send_eye_expression(eye_expression)
    
    def set_waiting_eye_expression(self):
        """Set eyes to waiting state with persistent RGB animation."""
        if not self.is_in_waiting_state:
            # Store current eye expression before changing to waiting
            if hasattr(self, 'current_eye_expression'):
                self.previous_eye_expression = self.current_eye_expression
            
            # Set waiting expression with enhanced rate limiting
            result = self.send_eye_expression(EZRobotEyeExpressions.EYES_WAITING)
            if result is not None:
                self.is_in_waiting_state = True
                self.current_eye_expression = EZRobotEyeExpressions.EYES_WAITING
                print("🔍 Set eyes to waiting state (persistent RGB animation)")
            return result
        return None
    
    def restore_previous_eye_expression(self):
        """Restore the previous eye expression after waiting state."""
        if self.is_in_waiting_state and self.previous_eye_expression:
            result = self.send_eye_expression(self.previous_eye_expression)
            if result is not None:
                self.is_in_waiting_state = False
                # current_eye_expression updated inside send_eye_expression
                if result != "SKIPPED":
                    print(f"🔍 Restored previous eye expression: {self.previous_eye_expression.value}")
            return result
        elif self.is_in_waiting_state:
            # If no previous expression, default to open eyes
            result = self.send_eye_expression(EZRobotEyeExpressions.EYES_OPEN)
            if result is not None:
                self.is_in_waiting_state = False
                if result != "SKIPPED":
                    print("🔍 Restored default eye expression: eyes_open")
            return result
        return None
    
    def set_eye_expression_with_tracking(self, emotion: str):
        """Set eye expression and track the current state."""
        result = self.set_eye_expression(emotion)
        if result is not None:
            # Map emotion to eye expression for tracking
            emotion_to_eye = {
                'joy': EZRobotEyeExpressions.EYES_JOY,
                'happiness': EZRobotEyeExpressions.EYES_JOY,
                'happy': EZRobotEyeExpressions.EYES_JOY,
                'anger': EZRobotEyeExpressions.EYES_ANGER,
                'angry': EZRobotEyeExpressions.EYES_ANGER,
                'fear': EZRobotEyeExpressions.EYES_FEAR,
                'afraid': EZRobotEyeExpressions.EYES_FEAR,
                'surprise': EZRobotEyeExpressions.EYES_SURPRISE,
                'surprised': EZRobotEyeExpressions.EYES_SURPRISE,
                'disgust': EZRobotEyeExpressions.EYES_DISGUST,
                'disgusted': EZRobotEyeExpressions.EYES_DISGUST,
                'sadness': EZRobotEyeExpressions.EYES_SAD,
                'sad': EZRobotEyeExpressions.EYES_SAD,
                'default': EZRobotEyeExpressions.EYES_OPEN,
                'neutral': EZRobotEyeExpressions.EYES_OPEN
            }
            
            eye_expression = emotion_to_eye.get(emotion.lower(), EZRobotEyeExpressions.EYES_OPEN)
            self.current_eye_expression = eye_expression
            self.is_in_waiting_state = False
            
        return result

    def _send_request(self, url):
        """Send HTTP request to EZ-Robot with enhanced rate limiting and adaptive timing."""
        import time
        
        with self.request_lock:
            # Check if we're already processing a request
            if self.processing_request:
                print(f"⏳ Request queued: {url.split('=')[-1].split(')')[0] if '=' in url else 'unknown'}")
                self.request_queue.append(url)
                return None
            
            self.processing_request = True
        
        try:
            # Check for duplicate requests to prevent spam
            current_time = time.time()
            if url == self.last_request_url:
                time_since_duplicate = current_time - self.last_request_time_strict
                
                # Use different intervals for different types of commands
                if "RGB%20Animator" in url or "eyes_" in url:
                    # Eye expressions can be sent more frequently
                    duplicate_interval = 0.3  # 0.3 seconds for eye expressions
                else:
                    # Other commands use the standard interval
                    duplicate_interval = self.min_duplicate_interval
                
                if time_since_duplicate < duplicate_interval:
                    print(f"🚫 Duplicate request blocked: {url.split('=')[-1].split(')')[0] if '=' in url else 'unknown'} (last sent {time_since_duplicate:.1f}s ago)")
                    return None
            
            # Adaptive rate limiting based on connection health and response times
            time_since_last = current_time - self.last_request_time
            
            # Use adaptive interval, but respect minimum
            required_interval = max(self.adaptive_interval, self.min_request_interval)
            
            if time_since_last < required_interval:
                sleep_time = required_interval - time_since_last
                print(f"⏳ Enhanced rate limiting: Waiting {sleep_time:.2f}s (adaptive: {self.adaptive_interval:.2f}s) to prevent ARC controller overload")
                time.sleep(sleep_time)
            
            # Record request start time for response time calculation
            request_start = time.time()
            
            print(f"🔍 Sending EZ-Robot request: {url}")
            response = requests.get(url, timeout=10)  # Increased timeout
            response.raise_for_status()
            
            # Calculate response time and update adaptive interval
            response_time = time.time() - request_start
            self._update_adaptive_interval(response_time, True)
            
            print(f"✅ EZ-Robot response: {response.status_code} - {response.text[:100]}... (response time: {response_time:.2f}s)")
            
            # Update last request time and track for duplicate prevention
            self.last_request_time = time.time()
            self.last_successful_request = time.time()
            self.last_request_url = url
            self.last_request_time_strict = time.time()
            
            # Process queued requests
            self._process_request_queue()
            
            return response.text
            
        except requests.RequestException as ex:
            # Handle failures and update adaptive interval
            self._update_adaptive_interval(0, False)
            print(f"❌ EZ-Robot request error: {ex}")
            
            # Update connection health
            self.connection_health_score = max(0.0, self.connection_health_score - 0.2)
            
            # If we have too many consecutive failures, attempt recovery
            if self.consecutive_failures >= self.max_consecutive_failures:
                print(f"🔄 Connection issues detected - attempting recovery...")
                if self.attempt_connection_recovery():
                    # Recovery successful, reset failures
                    self.consecutive_failures = 0
                    self.adaptive_interval = self.min_request_interval
                else:
                    # Recovery failed, increase interval
                    self.adaptive_interval = min(self.adaptive_interval * 1.5, self.max_request_interval)
                    print(f"🔄 Increased adaptive interval to {self.adaptive_interval:.2f}s due to connection issues")
            
            # Process queued requests even on failure
            self._process_request_queue()
            return None
        
        finally:
            with self.request_lock:
                self.processing_request = False
    
    def _update_adaptive_interval(self, response_time: float, success: bool):
        """Update adaptive interval based on response time and success."""
        if success:
            self.consecutive_failures = 0
            
            # Add response time to history
            self.request_history.append(response_time)
            
            # Calculate average response time
            if len(self.request_history) >= 3:
                avg_response_time = sum(self.request_history) / len(self.request_history)
                
                # Adjust adaptive interval based on response time
                if avg_response_time > 2.0:  # Slow responses
                    self.adaptive_interval = min(self.adaptive_interval * 1.2, self.max_request_interval)
                    print(f"📈 Increased adaptive interval to {self.adaptive_interval:.2f}s (slow responses: {avg_response_time:.2f}s)")
                elif avg_response_time < 0.5:  # Fast responses
                    self.adaptive_interval = max(self.adaptive_interval * 0.9, self.min_request_interval)
                    print(f"📉 Decreased adaptive interval to {self.adaptive_interval:.2f}s (fast responses: {avg_response_time:.2f}s)")
        else:
            self.consecutive_failures += 1
            print(f"⚠️ Consecutive failures: {self.consecutive_failures}/{self.max_consecutive_failures}")
    
    def _process_request_queue(self):
        """Process any queued requests."""
        with self.request_lock:
            if self.request_queue and not self.processing_request:
                next_request = self.request_queue.popleft()
                print(f"🔄 Processing queued request: {next_request.split('=')[-1].split(')')[0] if '=' in next_request else 'unknown'}")
                # Process the next request asynchronously
                threading.Thread(target=self._send_request, args=(next_request,), daemon=True).start()
    
    def set_request_interval(self, interval_seconds: float):
        """Set the minimum interval between HTTP requests to prevent overwhelming JD's ARC controller."""
        self.min_request_interval = interval_seconds
        self.adaptive_interval = max(self.adaptive_interval, interval_seconds)
        print(f"🔧 Rate limiting minimum interval set to {interval_seconds}s between requests")
    
    def get_request_interval(self) -> float:
        """Get the current adaptive interval between HTTP requests."""
        return self.adaptive_interval
    
    def get_rate_limiting_stats(self) -> dict:
        """Get current rate limiting statistics."""
        import time
        current_time = time.time()
        
        return {
            "min_interval": self.min_request_interval,
            "adaptive_interval": self.adaptive_interval,
            "max_interval": self.max_request_interval,
            "consecutive_failures": self.consecutive_failures,
            "queue_length": len(self.request_queue),
            "avg_response_time": sum(self.request_history) / len(self.request_history) if self.request_history else 0,
            "connection_health": self.connection_health_score,
            "time_since_last_request": current_time - self.last_request_time,
            "last_request_url": self.last_request_url,
            "time_since_duplicate": current_time - self.last_request_time_strict if self.last_request_time_strict else 0,
            "duplicate_interval": self.min_duplicate_interval
        }
    
    def reset_rate_limiting(self):
        """Reset rate limiting to default values."""
        self.adaptive_interval = self.min_request_interval
        self.consecutive_failures = 0
        self.request_history.clear()
        self.request_queue.clear()
        self.connection_health_score = 1.0
        print("🔄 Rate limiting reset to default values")
    
    def attempt_connection_recovery(self):
        """Attempt to recover from connection issues with WiFi-specific troubleshooting."""
        import time
        
        current_time = time.time()
        
        # Check if we should attempt recovery
        if self.recovery_attempts >= self.max_recovery_attempts:
            print("❌ Max recovery attempts reached - manual intervention required")
            print("💡 Please check:")
            print("   - JD's WiFi connection status")
            print("   - ARC HTTP Server is running")
            print("   - IP address hasn't changed (should be 192.168.56.1)")
            print("   - WiFi router connectivity")
            return False
        
        # Check cooldown period
        if hasattr(self, 'last_recovery_attempt'):
            time_since_last_recovery = current_time - self.last_recovery_attempt
            if time_since_last_recovery < self.recovery_cooldown:
                print(f"⏳ Recovery cooldown active ({self.recovery_cooldown - time_since_last_recovery:.1f}s remaining)")
                return False
        
        self.last_recovery_attempt = current_time
        self.recovery_attempts += 1
        
        print(f"🔄 Attempting WiFi connection recovery (attempt {self.recovery_attempts}/{self.max_recovery_attempts})")
        
        # Step 1: Reset connection state
        self.is_connected = False
        self.connection_health_score = 0.0
        self.consecutive_failures = 0
        
        # Step 2: Increase timeout for recovery attempts
        original_timeout = 5
        recovery_timeout = min(15, 5 + (self.recovery_attempts * 2))  # Progressive timeout
        print(f"🔄 Using extended timeout: {recovery_timeout}s for recovery")
        
        # Step 3: Test connection with extended timeout
        try:
            test_url = f"{self.base_address}ControlCommand(%22System%22,%22GetStatus%22,%22%22))"
            print(f"🔍 Testing connection to: {test_url}")
            
            response = requests.get(test_url, timeout=recovery_timeout)
            if response.status_code == 200:
                print("✅ WiFi connection recovery successful!")
                self.is_connected = True
                self.recovery_attempts = 0
                self.connection_health_score = 1.0
                self.consecutive_failures = 0
                
                # Reset rate limiting to more conservative values after recovery
                self.adaptive_interval = self.min_request_interval * 1.5
                print(f"🔄 Reset to conservative rate limiting: {self.adaptive_interval:.2f}s")
                
                return True
            else:
                print(f"⚠️ HTTP response but not 200: {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"⏰ Connection timeout after {recovery_timeout}s")
        except requests.exceptions.ConnectionError:
            print("🚫 WiFi connection error - JD may be disconnected")
        except Exception as e:
            print(f"❌ Unexpected recovery error: {e}")
        
        print(f"❌ WiFi connection recovery failed (attempt {self.recovery_attempts}/{self.max_recovery_attempts})")
        
        # Progressively increase intervals after failed recovery
        self.adaptive_interval = min(self.adaptive_interval * 1.5, self.max_request_interval)
        print(f"📈 Increased interval to {self.adaptive_interval:.2f}s due to failed recovery")
        
        return False
    
    def send_urgent_request(self, url):
        """Send an urgent request with minimal rate limiting (use sparingly for critical operations)."""
        try:
            print(f"🚨 Sending URGENT EZ-Robot request (minimal rate limiting): {url}")
            
            # Only apply minimal rate limiting for urgent requests
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < 0.2:  # Only 200ms minimum for urgent requests
                sleep_time = 0.2 - time_since_last
                print(f"⏳ Urgent request rate limiting: Waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            response = requests.get(url, timeout=15)  # Longer timeout for urgent requests
            response.raise_for_status()
            print(f"✅ EZ-Robot urgent response: {response.status_code} - {response.text[:100]}...")
            
            # Update last request time but don't affect adaptive interval
            self.last_request_time = time.time()
            
            return response.text
        except requests.RequestException as ex:
            print(f"❌ EZ-Robot urgent request error: {ex}")
            return None

# Example usage
if __name__ == "__main__":
    robot = EZRobot()
    if robot.test_connection():
        def speech_callback(text):
            print(f"Received speech: {text}")
        
        robot.start_speech_recognition(speech_callback)
        time.sleep(30)  # Run for 30 seconds
        robot.stop_speech_recognition()
    else:
        print("Failed to connect to EZ-Robot")