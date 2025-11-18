import asyncio
import requests
from urllib.parse import quote
import configparser
from ezrobot import EZRobot, EZRobotSkills, EZRwindowName, EZRccParameter
import aiohttp
import os
import sys
import time
import openai
from openai import OpenAI
import backoff  # For exponential backoff

class APIClient:
    def __init__(self):
        # Add Windows-specific event loop policy to avoid aiohttp error
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        self.config = configparser.ConfigParser()
        
        # Try to read current settings, fall back to default if needed
        if os.path.exists('settings_current.ini'):
            self.config.read('settings_current.ini')
        elif os.path.exists('settings_default.ini'):
            self.config.read('settings_default.ini')
            # Save as current settings
            with open('settings_current.ini', 'w') as configfile:
                self.config.write(configfile)
        else:
            # Create a minimal config if neither file exists
            self.config['settings'] = {
                'twinwordkey': '',
                'OpenAIAPIKey': '',
                'meaningcloudkey': '',
                'wordsapikey': ''
            }
            with open('settings_current.ini', 'w') as configfile:
                self.config.write(configfile)
        
        self.conceptnet_base_url = "http://api.conceptnet.io"
        self.ezrobot_base_url = "http://192.168.56.1/Exec?password=admin&script=ControlCommand("
        self.ezrobot = EZRobot(self.ezrobot_base_url)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.config.get('settings', 'OpenAIAPIKey'))
        
        # Initialize call history tracking
        self.call_history = []
        
    def reload_api_key(self):
        """Reload API key from settings after they've been updated."""
        try:
            # Reload config from file
            if os.path.exists('settings_current.ini'):
                self.config.read('settings_current.ini')
            
            # Get new API key
            api_key = self.config.get('settings', 'OpenAIAPIKey')
            
            # Update OpenAI client with new key
            self.openai_client = OpenAI(api_key=api_key)
            
            return True
        except Exception as e:
            print(f"Error reloading API key: {e}")
            return False
        
        # Add session management
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def ensure_session(self):
        """Ensures an aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def conceptnet_api(self, word_to_send, time_delay=False):
        if time_delay:
            await asyncio.sleep(3)  # Delay for 3 seconds if needed

        url = f"{self.conceptnet_base_url}/c/en/{quote(word_to_send)}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching ConceptNet data: {e}")
            return None

    @backoff.on_exception(backoff.expo, 
                         (openai.RateLimitError, 
                          openai.APIConnectionError, 
                          openai.APIError),
                         max_tries=5)
    async def openai_api(self, prompt, api_key, time_delay=False):
        if time_delay:
            await asyncio.sleep(3)

        # Track API call
        call_start_time = time.time()
        call_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Calculate call metrics
            call_end_time = time.time()
            response_time = call_end_time - call_start_time
            
            # Extract token usage if available
            tokens_used = 0
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
            
            # Estimate cost (rough estimate for gpt-4o-mini)
            estimated_cost = tokens_used * 0.00015 / 1000  # $0.15 per 1M tokens
            
            # Log the API call
            call_record = {
                'timestamp': call_timestamp,
                'model': 'gpt-4o-mini',
                'purpose': 'cognitive_processing',
                'tokens_used': tokens_used,
                'cost': estimated_cost,
                'response_time': response_time,
                'status': 'success',
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'full_prompt': prompt  # Store the complete prompt without truncation
            }
            self.call_history.append(call_record)
            
            # Extract the content from the response
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                return {
                    'choices': [{
                        'content': content
                    }]
                }
            return None
            
        except openai.APIError as e:
            # Log failed API call
            call_end_time = time.time()
            response_time = call_end_time - call_start_time
            call_record = {
                'timestamp': call_timestamp,
                'model': 'gpt-4o-mini',
                'purpose': 'cognitive_processing',
                'tokens_used': 0,
                'cost': 0,
                'response_time': response_time,
                'status': 'api_error',
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'full_prompt': prompt,  # Store the complete prompt without truncation
                'error': str(e)
            }
            self.call_history.append(call_record)
            print(f"OpenAI API returned an API Error: {e}")
            raise
        except openai.APIConnectionError as e:
            # Log failed API call
            call_end_time = time.time()
            response_time = call_end_time - call_start_time
            call_record = {
                'timestamp': call_timestamp,
                'model': 'gpt-4o-mini',
                'purpose': 'cognitive_processing',
                'tokens_used': 0,
                'cost': 0,
                'response_time': response_time,
                'status': 'connection_error',
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'full_prompt': prompt,  # Store the complete prompt without truncation
                'error': str(e)
            }
            self.call_history.append(call_record)
            print(f"Failed to connect to OpenAI API: {e}")
            raise
        except openai.RateLimitError as e:
            # Log failed API call
            call_end_time = time.time()
            response_time = call_end_time - call_start_time
            call_record = {
                'timestamp': call_timestamp,
                'model': 'gpt-4o-mini',
                'purpose': 'cognitive_processing',
                'tokens_used': 0,
                'cost': 0,
                'response_time': response_time,
                'status': 'rate_limit_error',
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'full_prompt': prompt,  # Store the complete prompt without truncation
                'error': str(e)
            }
            self.call_history.append(call_record)
            print(f"OpenAI API request exceeded rate limit: {e}")
            raise
        except Exception as e:
            # Log failed API call
            call_end_time = time.time()
            response_time = call_end_time - call_start_time
            call_record = {
                'timestamp': call_timestamp,
                'model': 'gpt-4o-mini',
                'purpose': 'cognitive_processing',
                'tokens_used': 0,
                'cost': 0,
                'response_time': response_time,
                'status': 'unexpected_error',
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'full_prompt': prompt,  # Store the complete prompt without truncation
                'error': str(e)
            }
            self.call_history.append(call_record)
            print(f"Unexpected error calling OpenAI API: {e}")
            raise

    async def conceptnet_lookup(self, word):
        url = f"http://api.conceptnet.io/c/en/{word}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error calling ConceptNet API: {e}")
            return None

    async def twinword_lookup(self, text):
        """
        Performs emotion analysis using Twinword API with proper timeout and error handling.
        """
        # Create default response structure at the start of the method
        default_response = {
            "emotions_detected": [],
            "emotion_scores": {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "disgust": 0.0
            }
        }
        
        try:
            # Reload config file to ensure we have latest settings
            self.config.read('settings_current.ini')
            
            # Get API key with error handling
            try:
                twinword_api_key = self.config.get('settings', 'twinwordkey')
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                print(f"Error reading Twinword API key from config: {e}")
                return default_response
            
            if not twinword_api_key:
                print("Twinword API key is empty")
                return default_response
            
            url = f"https://api.twinword.com/api/emotion/analyze/latest/?text={quote(text)}"
            headers = {
                "x-rapidapi-host": "api.twinword.com",
                "X-Twaip-Key": twinword_api_key,
                "useQueryString": "true"
            }
            
            # Add timeout and proper error handling
            timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Ensure the response has the expected structure
                        if isinstance(data, dict):
                            # Use the raw emotion scores directly from the API response
                            emotion_scores = data.get('emotion_scores', {})
                            
                            # Ensure all required emotions are present with default values
                            for emotion in ["joy", "sadness", "anger", "fear", "surprise", "disgust"]:
                                if emotion not in emotion_scores:
                                    emotion_scores[emotion] = 0.0
                            
                            # Log the raw and processed scores for debugging
                            print(f"Raw Twinword scores: {data}")
                            print(f"Processed emotion scores: {emotion_scores}")
                            
                            return {
                                "emotions_detected": data.get("emotions_detected", []),
                                "emotion_scores": emotion_scores
                            }
                    print(f"Twinword API error: Status {response.status}")
                    return default_response
                    
        except asyncio.TimeoutError:
            print("Twinword API timeout")
            return default_response
        except aiohttp.ClientError as e:
            print(f"Twinword API connection error: {e}")
            return default_response
        except Exception as e:
            print(f"Unexpected error in Twinword API call: {e}")
            return default_response

    def send_robot_command(self, window_name, param, skill_or_eye_movement):
        return self.ezrobot.send(window_name, param, skill_or_eye_movement)

    def send_robot_auto_position(self, command):
        return self.ezrobot.send_auto_position(command)

    def send_robot_auto_frame(self, command):
        return self.ezrobot.send_auto_frame(command)

    def send_robot_auto_script(self, command):
        return self.ezrobot.send_auto_script(command)

# Example usage
if __name__ == "__main__":
    api_client = APIClient()
    api_key = api_client.config.get('settings', 'OpenAIAPIKey')
    
    if not api_key:
        print("Error: OpenAI API key not found in settings")
        exit(1)
        
    # Sample user input for testing
    user_input = "Hello, how are you feeling today?"
    
    prompt = (
        "Can you figure out the meaning and context of this sentence just spoken to you from another person you are learning about (you are a small humanoid robot that simulates human behavior named Carl): '{user_input}', Return the values to understand, only in first person point of view, the WHO WHAT WHEN WHERE WHY HOW and the expectation of the common reply the sentence provided and provide a list of nouns, a list of verbs, a list of people, a list of subject(s), what is the intent of the sentence (use only: inform,query,answer,request,command,promise,acknowledge,share,unknown )? return the result in json format."
    ).format(user_input=user_input)
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            result = asyncio.run(api_client.openai_api(prompt, api_key, time_delay=True))
            if result:
                print("OpenAI API Result:", result)
                break
            else:
                print(f"Attempt {attempt + 1} failed: No result returned")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Please try again later.")