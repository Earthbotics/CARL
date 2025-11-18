#!/usr/bin/env python3
"""
AIML Reflex Layer Example

This example demonstrates the complete AIML reflex system integration
with CARL's cognitive pipeline, showing the flow from perception
through reflex responses to learning and memory integration.
"""

import os
import json
import logging
from datetime import datetime
from aiml_reflex_layer import AIMLReflexEngine, AIMLReflexIntegration
from perception_system import PerceptionSystem
from judgment_system import JudgmentSystem
from concept_system import ConceptSystem
from memory_system import MemorySystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CARLReflexDemo:
    """
    Demonstration of CARL's AIML reflex system integration.
    """
    
    def __init__(self):
        """Initialize the demo system."""
        self.aiml_engine = AIMLReflexEngine(aiml_dir='./aiml')
        self.memory_system = MemorySystem()
        self.concept_system = ConceptSystem()
        
        # Create integration layer
        self.aiml_integration = AIMLReflexIntegration(
            aiml_engine=self.aiml_engine,
            memory_system=self.memory_system,
            concept_system=self.concept_system
        )
        
        # Initialize other systems
        self.perception_system = PerceptionSystem()
        self.judgment_system = JudgmentSystem()
        
        logger.info("CARL Reflex Demo initialized")
    
    def demonstrate_basic_reflex(self):
        """Demonstrate basic reflex pattern matching."""
        print("\n" + "="*60)
        print("DEMONSTRATION: Basic Reflex Pattern Matching")
        print("="*60)
        
        # Add some basic patterns
        patterns = [
            ("hello", "Hi there! How can I help you today?"),
            ("goodbye", "See you later! Take care!"),
            ("how are you", "I'm doing well, thank you for asking!"),
            ("what is *", "That's an interesting question about *. Let me think..."),
            ("tell me about *", "I'd be happy to tell you about *. Here's what I know...")
        ]
        
        for input_text, response_text in patterns:
            success = self.aiml_engine.add_dynamic_pattern(
                input_text=input_text,
                response_text=response_text,
                source="demo"
            )
            print(f"✅ Added pattern: '{input_text}' -> '{response_text}'")
        
        # Test pattern matching
        test_inputs = [
            "Hello",
            "Goodbye",
            "How are you?",
            "What is love?",
            "Tell me about robots"
        ]
        
        print("\nTesting pattern matching:")
        for test_input in test_inputs:
            response = self.aiml_engine.get_reflex_response(test_input)
            if response:
                print(f"  Input: '{test_input}'")
                print(f"  Response: '{response}'")
                print(f"  Source: Reflex (fast response)")
            else:
                print(f"  Input: '{test_input}'")
                print(f"  Response: No reflex match found")
            print()
    
    def demonstrate_learning_flow(self):
        """Demonstrate learning from OpenAI responses."""
        print("\n" + "="*60)
        print("DEMONSTRATION: Learning from OpenAI Responses")
        print("="*60)
        
        # Simulate OpenAI responses with random action tags
        openai_responses = [
            ("Do ants dream?", "[[random_action]] Maybe in their own tiny alien minds!"),
            ("What's the meaning of life?", "[[random_action]] 42, but also pizza and good friends!"),
            ("Can robots feel emotions?", "[[random_action]] I feel like I'm feeling something right now..."),
            ("Why is the sky blue?", "[[random_action]] Because it's reflecting the ocean's mood!"),
            ("What's your favorite color?", "[[random_action]] I'm partial to the color of binary code at sunset!")
        ]
        
        print("Learning from OpenAI responses:")
        for user_input, openai_response in openai_responses:
            print(f"\n  User: '{user_input}'")
            print(f"  OpenAI: '{openai_response}'")
            
            # Learn the pattern
            success = self.aiml_integration.learn_from_openai_response(
                user_input=user_input,
                openai_response=openai_response
            )
            
            if success:
                print(f"  ✅ Learned as reflex pattern")
                
                # Test that it was learned
                reflex_response = self.aiml_engine.get_reflex_response(user_input)
                if reflex_response:
                    print(f"  Reflex: '{reflex_response}'")
                else:
                    print(f"  ❌ Pattern not found in reflex system")
            else:
                print(f"  ❌ Failed to learn pattern")
    
    def demonstrate_memory_integration(self):
        """Demonstrate memory system integration."""
        print("\n" + "="*60)
        print("DEMONSTRATION: Memory System Integration")
        print("="*60)
        
        # Test reflex hit logging
        print("Logging reflex hits to memory:")
        reflex_hits = [
            ("hello", "Hi there!", "HELLO"),
            ("goodbye", "See you later!", "GOODBYE"),
            ("how are you", "I'm doing well!", "HOW ARE YOU")
        ]
        
        for user_input, response, pattern in reflex_hits:
            memory_id = self.memory_system.log_reflex_hit(
                user_input=user_input,
                response=response,
                pattern=pattern
            )
            print(f"  ✅ Logged reflex hit: {memory_id}")
        
        # Test OpenAI fallback logging
        print("\nLogging OpenAI fallbacks to memory:")
        openai_fallbacks = [
            ("Do ants dream?", "[[random_action]] Maybe in their own tiny alien minds!", 0.8),
            ("What's the meaning of life?", "[[random_action]] 42, but also pizza!", 0.7)
        ]
        
        for user_input, response, confidence in openai_fallbacks:
            memory_id = self.memory_system.log_openai_fallback(
                user_input=user_input,
                response=response,
                confidence=confidence
            )
            print(f"  ✅ Logged OpenAI fallback: {memory_id}")
        
        # Test concept learning
        print("\nLearning concepts from reflexes:")
        concept_success = self.concept_system.learn_new_reflex(
            input_text="hello world",
            response_text="Hello to you too!"
        )
        print(f"  ✅ Concept learning: {concept_success}")
    
    def demonstrate_statistics(self):
        """Demonstrate system statistics."""
        print("\n" + "="*60)
        print("DEMONSTRATION: System Statistics")
        print("="*60)
        
        # Get AIML engine statistics
        aiml_stats = self.aiml_engine.get_pattern_statistics()
        print("AIML Engine Statistics:")
        print(f"  Total patterns: {aiml_stats['total_patterns']}")
        print(f"  Static patterns: {aiml_stats['static_patterns']}")
        print(f"  Dynamic patterns: {aiml_stats['dynamic_patterns']}")
        print(f"  Total usage: {aiml_stats['total_usage']}")
        
        # Get learning statistics
        learning_stats = self.aiml_integration.get_learning_statistics()
        print(f"\nLearning Statistics:")
        print(f"  Total reflex hits: {learning_stats['total_reflex_hits']}")
        print(f"  Recent hits: {learning_stats['recent_hits']}")
        
        # Get memory statistics
        memory_stats = self.memory_system.get_memory_statistics()
        print(f"\nMemory Statistics:")
        print(f"  Total memories: {memory_stats['total_memories']}")
        print(f"  Working memories: {memory_stats['working_memories']}")
        print(f"  Episodic memories: {memory_stats['episodic_memories']}")
    
    def demonstrate_complete_flow(self):
        """Demonstrate the complete cognitive flow."""
        print("\n" + "="*60)
        print("DEMONSTRATION: Complete Cognitive Flow")
        print("="*60)
        
        # Simulate user inputs
        user_inputs = [
            "Hello there!",
            "Do ants dream?",
            "What's your favorite color?",
            "Tell me about robots",
            "How are you feeling today?"
        ]
        
        for user_input in user_inputs:
            print(f"\nUser: '{user_input}'")
            
            # Step 1: Check for reflex response
            reflex_result = self.aiml_integration.process_input(user_input)
            
            if reflex_result.get('pattern_matched', False):
                print(f"  🚀 Reflex Response: '{reflex_result['response']}'")
                print(f"  ⚡ Processing time: {reflex_result['processing_time']:.3f}s")
                print(f"  🎯 Confidence: {reflex_result['confidence']:.2f}")
            else:
                print(f"  ❌ No reflex match found")
                
                # Step 2: Fallback to OpenAI (simulated)
                print(f"  🤖 Generating OpenAI response...")
                # In a real system, this would call the judgment system
                simulated_openai_response = f"[[random_action]] That's a fascinating question about {user_input.lower()}!"
                print(f"  🤖 OpenAI Response: '{simulated_openai_response}'")
                
                # Step 3: Learn from OpenAI response
                learn_success = self.aiml_integration.learn_from_openai_response(
                    user_input=user_input,
                    openai_response=simulated_openai_response
                )
                
                if learn_success:
                    print(f"  ✅ Learned new reflex pattern")
                else:
                    print(f"  ❌ Failed to learn pattern")
    
    def run_demo(self):
        """Run the complete demonstration."""
        print("🤖 CARL AIML Reflex System Demonstration")
        print("=" * 60)
        print("This demo shows the integration of AIML reflex patterns")
        print("with CARL's cognitive pipeline.")
        
        try:
            # Run demonstrations
            self.demonstrate_basic_reflex()
            self.demonstrate_learning_flow()
            self.demonstrate_memory_integration()
            self.demonstrate_statistics()
            self.demonstrate_complete_flow()
            
            print("\n" + "="*60)
            print("✅ DEMONSTRATION COMPLETE")
            print("="*60)
            print("The AIML reflex system is now integrated with CARL's")
            print("cognitive pipeline, providing fast responses for known")
            print("patterns while learning new ones from OpenAI fallbacks.")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")


def main():
    """Main function to run the demonstration."""
    # Create demo instance
    demo = CARLReflexDemo()
    
    # Run the demonstration
    demo.run_demo()


if __name__ == "__main__":
    main()
