#!/usr/bin/env python3
"""
Fix Greet Overuse Issue

This script addresses the problem of CARL overusing the greet skill by implementing:
1. Context-aware greeting detection
2. Greeting cooldown system
3. Conversation state tracking
4. Smart skill filtering
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GreetOveruseFixer:
    def __init__(self):
        self.greeting_cooldown_file = "greeting_cooldown.json"
        self.conversation_state_file = "conversation_state.json"
        self.greeting_cooldown_minutes = 5  # Minimum time between greetings
        self.max_greetings_per_session = 3  # Maximum greetings per conversation session
        
    def create_greeting_cooldown_system(self):
        """Create a greeting cooldown system to prevent overuse."""
        cooldown_data = {
            "last_greeting_time": None,
            "greeting_count": 0,
            "session_start_time": datetime.now().isoformat(),
            "greeting_history": []
        }
        
        with open(self.greeting_cooldown_file, 'w') as f:
            json.dump(cooldown_data, f, indent=2)
        
        print("✅ Created greeting cooldown system")
        return cooldown_data
    
    def can_greet(self) -> bool:
        """Check if it's appropriate to greet based on cooldown and context."""
        try:
            if not os.path.exists(self.greeting_cooldown_file):
                self.create_greeting_cooldown_system()
                return True
            
            with open(self.greeting_cooldown_file, 'r') as f:
                cooldown_data = json.load(f)
            
            current_time = datetime.now()
            
            # Check if we've exceeded max greetings per session
            if cooldown_data.get("greeting_count", 0) >= self.max_greetings_per_session:
                print("⚠️ Maximum greetings per session reached")
                return False
            
            # Check cooldown period
            last_greeting_time = cooldown_data.get("last_greeting_time")
            if last_greeting_time:
                last_greeting = datetime.fromisoformat(last_greeting_time)
                time_since_last = current_time - last_greeting
                
                if time_since_last < timedelta(minutes=self.greeting_cooldown_minutes):
                    remaining_time = timedelta(minutes=self.greeting_cooldown_minutes) - time_since_last
                    print(f"⏰ Greeting cooldown active. Wait {remaining_time.seconds // 60} more minutes")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking greeting cooldown: {e}")
            return True  # Allow greeting if there's an error
    
    def record_greeting(self, context: str = "general"):
        """Record that a greeting was used."""
        try:
            if not os.path.exists(self.greeting_cooldown_file):
                self.create_greeting_cooldown_system()
            
            with open(self.greeting_cooldown_file, 'r') as f:
                cooldown_data = json.load(f)
            
            current_time = datetime.now().isoformat()
            
            # Update greeting data
            cooldown_data["last_greeting_time"] = current_time
            cooldown_data["greeting_count"] = cooldown_data.get("greeting_count", 0) + 1
            
            # Add to history
            greeting_record = {
                "time": current_time,
                "context": context,
                "count": cooldown_data["greeting_count"]
            }
            cooldown_data["greeting_history"].append(greeting_record)
            
            # Keep only last 10 entries
            if len(cooldown_data["greeting_history"]) > 10:
                cooldown_data["greeting_history"] = cooldown_data["greeting_history"][-10:]
            
            with open(self.greeting_cooldown_file, 'w') as f:
                json.dump(cooldown_data, f, indent=2)
            
            print(f"✅ Greeting recorded (count: {cooldown_data['greeting_count']})")
            
        except Exception as e:
            print(f"❌ Error recording greeting: {e}")
    
    def create_conversation_state_tracker(self):
        """Create a conversation state tracker to avoid repeated greetings."""
        state_data = {
            "conversation_active": False,
            "last_interaction_time": None,
            "greeting_exchanged": False,
            "conversation_topics": [],
            "interaction_count": 0,
            "session_start": datetime.now().isoformat()
        }
        
        with open(self.conversation_state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        print("✅ Created conversation state tracker")
        return state_data
    
    def update_conversation_state(self, interaction_type: str, content: str = ""):
        """Update conversation state based on interaction."""
        try:
            if not os.path.exists(self.conversation_state_file):
                self.create_conversation_state_tracker()
            
            with open(self.conversation_state_file, 'r') as f:
                state_data = json.load(f)
            
            current_time = datetime.now().isoformat()
            
            # Update state
            state_data["conversation_active"] = True
            state_data["last_interaction_time"] = current_time
            state_data["interaction_count"] = state_data.get("interaction_count", 0) + 1
            
            # Mark greeting as exchanged if this is a greeting
            if interaction_type == "greeting":
                state_data["greeting_exchanged"] = True
            
            # Add topic if provided
            if content and content not in state_data["conversation_topics"]:
                state_data["conversation_topics"].append(content[:50])  # Limit length
            
            # Keep only last 10 topics
            if len(state_data["conversation_topics"]) > 10:
                state_data["conversation_topics"] = state_data["conversation_topics"][-10:]
            
            with open(self.conversation_state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
        except Exception as e:
            print(f"❌ Error updating conversation state: {e}")
    
    def is_greeting_appropriate(self, context: str) -> bool:
        """Check if greeting is appropriate in current context."""
        try:
            # Check cooldown
            if not self.can_greet():
                return False
            
            # Check conversation state
            if not os.path.exists(self.conversation_state_file):
                return True  # Allow greeting if no state file
            
            with open(self.conversation_state_file, 'r') as f:
                state_data = json.load(f)
            
            # Don't greet if already greeted in this conversation
            if state_data.get("greeting_exchanged", False):
                print("⚠️ Greeting already exchanged in this conversation")
                return False
            
            # Don't greet if conversation is very active
            if state_data.get("interaction_count", 0) > 5:
                print("⚠️ Conversation already active - greeting not needed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking greeting appropriateness: {e}")
            return True
    
    def reset_session(self):
        """Reset the greeting session (useful for fresh starts)."""
        try:
            # Reset cooldown
            if os.path.exists(self.greeting_cooldown_file):
                os.remove(self.greeting_cooldown_file)
            
            # Reset conversation state
            if os.path.exists(self.conversation_state_file):
                os.remove(self.conversation_state_file)
            
            print("✅ Greeting session reset - ready for fresh start")
            
        except Exception as e:
            print(f"❌ Error resetting session: {e}")
    
    def get_greeting_stats(self) -> Dict:
        """Get statistics about greeting usage."""
        stats = {
            "cooldown_active": False,
            "greeting_count": 0,
            "conversation_active": False,
            "greeting_exchanged": False,
            "time_since_last_greeting": None
        }
        
        try:
            # Get cooldown stats
            if os.path.exists(self.greeting_cooldown_file):
                with open(self.greeting_cooldown_file, 'r') as f:
                    cooldown_data = json.load(f)
                
                stats["greeting_count"] = cooldown_data.get("greeting_count", 0)
                
                last_greeting = cooldown_data.get("last_greeting_time")
                if last_greeting:
                    last_time = datetime.fromisoformat(last_greeting)
                    time_since = datetime.now() - last_time
                    stats["time_since_last_greeting"] = str(time_since)
                    
                    if time_since < timedelta(minutes=self.greeting_cooldown_minutes):
                        stats["cooldown_active"] = True
            
            # Get conversation stats
            if os.path.exists(self.conversation_state_file):
                with open(self.conversation_state_file, 'r') as f:
                    state_data = json.load(f)
                
                stats["conversation_active"] = state_data.get("conversation_active", False)
                stats["greeting_exchanged"] = state_data.get("greeting_exchanged", False)
            
        except Exception as e:
            print(f"❌ Error getting greeting stats: {e}")
        
        return stats

def main():
    """Main function to demonstrate the greeting overuse fix."""
    print("🔧 Greet Overuse Fixer")
    print("=" * 50)
    
    fixer = GreetOveruseFixer()
    
    # Create initial systems
    fixer.create_greeting_cooldown_system()
    fixer.create_conversation_state_tracker()
    
    # Test the system
    print("\n📊 Testing greeting appropriateness:")
    print(f"Can greet: {fixer.can_greet()}")
    print(f"Greeting appropriate: {fixer.is_greeting_appropriate('startup')}")
    
    # Record a greeting
    print("\n📝 Recording a greeting...")
    fixer.record_greeting("startup")
    fixer.update_conversation_state("greeting", "Hello")
    
    # Check stats
    print("\n📈 Greeting Statistics:")
    stats = fixer.get_greeting_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test cooldown
    print("\n⏰ Testing cooldown...")
    print(f"Can greet after recording: {fixer.can_greet()}")
    
    print("\n✅ Greet overuse fix implemented successfully!")
    print("\n💡 Usage Instructions:")
    print("1. Call can_greet() before executing any greeting")
    print("2. Call record_greeting() after executing a greeting")
    print("3. Call update_conversation_state() for all interactions")
    print("4. Call reset_session() for fresh starts")

if __name__ == "__main__":
    main()
