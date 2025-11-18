#!/usr/bin/env python3
"""
Unit Tests for AIML Reflex Layer

This module contains comprehensive tests for the AIML reflex system,
including pattern matching, dynamic pattern addition, and integration testing.
"""

import unittest
import tempfile
import os
import json
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules to test
from aiml_reflex_layer import AIMLReflexEngine, AIMLReflexIntegration
from perception_system import PerceptionSystem
from judgment_system import JudgmentSystem
from concept_system import ConceptSystem
from memory_system import MemorySystem


class TestAIMLReflexEngine(unittest.TestCase):
    """Test cases for AIMLReflexEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.aiml_engine = AIMLReflexEngine(aiml_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test AIML engine initialization."""
        self.assertIsNotNone(self.aiml_engine)
        self.assertEqual(self.aiml_engine.aiml_dir, self.temp_dir)
        self.assertIsInstance(self.aiml_engine.static_patterns, dict)
        self.assertIsInstance(self.aiml_engine.dynamic_patterns, dict)
    
    def test_add_dynamic_pattern(self):
        """Test adding dynamic patterns."""
        # Test adding a simple pattern
        success = self.aiml_engine.add_dynamic_pattern(
            input_text="hello",
            response_text="Hi there!",
            source="test"
        )
        
        self.assertTrue(success)
        self.assertIn("HELLO", self.aiml_engine.dynamic_patterns)
        
        # Test pattern matching
        response = self.aiml_engine.get_reflex_response("Hello")
        self.assertEqual(response, "Hi there!")
    
    def test_wildcard_pattern_matching(self):
        """Test wildcard pattern matching."""
        # Add wildcard pattern
        self.aiml_engine.add_dynamic_pattern(
            input_text="what is *",
            response_text="That's an interesting question about *",
            source="test"
        )
        
        # Test wildcard matching
        response = self.aiml_engine.get_reflex_response("what is love")
        self.assertEqual(response, "That's an interesting question about *")
        
        # Test another wildcard
        response = self.aiml_engine.get_reflex_response("what is happiness")
        self.assertEqual(response, "That's an interesting question about *")
    
    def test_pattern_prioritization(self):
        """Test that static patterns take priority over dynamic ones."""
        # Add static pattern (simulated)
        self.aiml_engine.static_patterns["HELLO"] = {
            'template': 'Static response',
            'source': 'static',
            'file': 'test.aiml',
            'created': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        # Add dynamic pattern with same input
        self.aiml_engine.add_dynamic_pattern(
            input_text="hello",
            response_text="Dynamic response",
            source="test"
        )
        
        # Static should take priority
        response = self.aiml_engine.get_reflex_response("Hello")
        self.assertEqual(response, "Static response")
    
    def test_pattern_statistics(self):
        """Test pattern usage statistics."""
        # Add some patterns
        self.aiml_engine.add_dynamic_pattern("hello", "Hi!", "test")
        self.aiml_engine.add_dynamic_pattern("goodbye", "Bye!", "test")
        
        # Use patterns
        self.aiml_engine.get_reflex_response("Hello")
        self.aiml_engine.get_reflex_response("Hello")  # Use twice
        self.aiml_engine.get_reflex_response("Goodbye")
        
        # Check statistics
        stats = self.aiml_engine.get_pattern_statistics()
        self.assertGreater(stats['total_patterns'], 0)
        self.assertGreater(stats['total_usage'], 0)
        self.assertIn('most_used_patterns', stats)
    
    def test_export_import_patterns(self):
        """Test pattern export and import functionality."""
        # Add test patterns
        self.aiml_engine.add_dynamic_pattern("test1", "response1", "test")
        self.aiml_engine.add_dynamic_pattern("test2", "response2", "test")
        
        # Export patterns
        export_file = os.path.join(self.temp_dir, "export.json")
        success = self.aiml_engine.export_patterns(export_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_file))
        
        # Verify export content
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        self.assertIn('patterns', export_data)
        self.assertIn('statistics', export_data)
    
    def test_create_aiml_pattern(self):
        """Test AIML pattern creation."""
        pattern_xml = self.aiml_engine.create_aiml_pattern(
            input_text="hello world",
            response_text="Hello to you too!"
        )
        
        # Parse XML to verify structure
        root = ET.fromstring(f"<root>{pattern_xml}</root>")
        pattern_elem = root.find('pattern')
        template_elem = root.find('template')
        
        self.assertIsNotNone(pattern_elem)
        self.assertIsNotNone(template_elem)
        self.assertEqual(pattern_elem.text.strip(), "HELLO WORLD")
        self.assertEqual(template_elem.text.strip(), "Hello to you too!")


class TestAIMLReflexIntegration(unittest.TestCase):
    """Test cases for AIMLReflexIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.aiml_engine = AIMLReflexEngine(aiml_dir=self.temp_dir)
        
        # Mock memory and concept systems
        self.mock_memory_system = Mock()
        self.mock_concept_system = Mock()
        
        self.integration = AIMLReflexIntegration(
            aiml_engine=self.aiml_engine,
            memory_system=self.mock_memory_system,
            concept_system=self.mock_concept_system
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_process_input_with_reflex(self):
        """Test processing input that has a reflex response."""
        # Add a pattern
        self.aiml_engine.add_dynamic_pattern("hello", "Hi there!", "test")
        
        # Process input
        result = self.integration.process_input("Hello", {"context": "test"})
        
        self.assertIsNotNone(result)
        self.assertEqual(result['response'], "Hi there!")
        self.assertEqual(result['source'], 'reflex')
        self.assertTrue(result['pattern_matched'])
    
    def test_process_input_without_reflex(self):
        """Test processing input that has no reflex response."""
        # Process input with no matching pattern
        result = self.integration.process_input("unknown input", {"context": "test"})
        
        self.assertIsNotNone(result)
        self.assertIsNone(result['response'])
        self.assertEqual(result['source'], 'none')
        self.assertFalse(result['pattern_matched'])
    
    def test_learn_from_openai_response(self):
        """Test learning from OpenAI responses."""
        # Test with random action tag
        success = self.integration.learn_from_openai_response(
            user_input="Do ants dream?",
            openai_response="[[random_action]] Maybe in their own tiny alien minds!"
        )
        
        self.assertTrue(success)
        
        # Test pattern was learned
        response = self.aiml_engine.get_reflex_response("Do ants dream?")
        self.assertEqual(response, "Maybe in their own tiny alien minds!")
    
    def test_learn_from_openai_response_no_tag(self):
        """Test learning from OpenAI responses without random action tag."""
        success = self.integration.learn_from_openai_response(
            user_input="What is the weather?",
            openai_response="I don't have access to weather data."
        )
        
        # Should not learn without the tag
        self.assertFalse(success)
    
    def test_get_learning_statistics(self):
        """Test getting learning statistics."""
        # Add some reflex hits
        self.integration._log_reflex_hit("hello", "hi", {"context": "test"})
        self.integration._log_reflex_hit("goodbye", "bye", {"context": "test"})
        
        stats = self.integration.get_learning_statistics()
        self.assertIn('total_reflex_hits', stats)
        self.assertIn('pattern_statistics', stats)
        self.assertGreater(stats['total_reflex_hits'], 0)


class TestPerceptionSystemIntegration(unittest.TestCase):
    """Test cases for PerceptionSystem with AIML integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock config
        self.mock_config = Mock()
        self.mock_config.getboolean.return_value = True
        self.mock_config.get.return_value = './aiml'
        
        # Mock main app
        self.mock_main_app = Mock()
        self.mock_main_app.memory_system = Mock()
        self.mock_main_app.concept_system = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('perception_system.configparser.ConfigParser')
    def test_perception_system_with_aiml(self, mock_config_parser):
        """Test PerceptionSystem initialization with AIML."""
        # Mock config
        mock_config = Mock()
        mock_config.getboolean.return_value = True
        mock_config.get.return_value = './aiml'
        mock_config_parser.return_value = mock_config
        
        # Create perception system
        perception = PerceptionSystem(main_app=self.mock_main_app)
        
        # Check AIML is enabled
        self.assertTrue(perception.aiml_enabled)
        self.assertIsNotNone(perception.aiml_engine)
        self.assertIsNotNone(perception.aiml_integration)
    
    def test_check_reflex_response(self):
        """Test checking for reflex responses."""
        # This would require more complex mocking of the perception system
        # For now, we'll test the basic structure
        pass


class TestJudgmentSystemIntegration(unittest.TestCase):
    """Test cases for JudgmentSystem with OpenAI fallback."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock config
        self.mock_config = Mock()
        self.mock_config.get.return_value = 'test-api-key'
        self.mock_config.getboolean.return_value = True
        
        # Mock main app
        self.mock_main_app = Mock()
        self.mock_main_app.memory_system = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('judgment_system.configparser.ConfigParser')
    @patch('judgment_system.openai')
    def test_generate_openai_response(self, mock_openai, mock_config_parser):
        """Test OpenAI response generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "[[random_action]] Maybe in their own tiny alien minds!"
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        # Mock config
        mock_config = Mock()
        mock_config.get.return_value = 'test-api-key'
        mock_config.getboolean.return_value = True
        mock_config_parser.return_value = mock_config
        
        # Create judgment system
        judgment = JudgmentSystem(main_app=self.mock_main_app)
        
        # Test OpenAI response generation
        response = judgment.generate_openai_response("Do ants dream?")
        
        self.assertIsNotNone(response)
        self.assertTrue(response.startswith("[[random_action]]"))
    
    @patch('judgment_system.configparser.ConfigParser')
    def test_process_openai_fallback(self, mock_config_parser):
        """Test OpenAI fallback processing."""
        # Mock config
        mock_config = Mock()
        mock_config.get.return_value = 'test-api-key'
        mock_config.getboolean.return_value = True
        mock_config_parser.return_value = mock_config
        
        # Create judgment system
        judgment = JudgmentSystem(main_app=self.mock_main_app)
        
        # Mock the generate_openai_response method
        with patch.object(judgment, 'generate_openai_response') as mock_generate:
            mock_generate.return_value = "[[random_action]] Test response"
            
            result = judgment.process_openai_fallback("Test input")
            
            self.assertIsNotNone(result)
            self.assertEqual(result['response'], "[[random_action]] Test response")
            self.assertEqual(result['source'], 'openai')
            self.assertTrue(result['learnable'])


class TestConceptSystemIntegration(unittest.TestCase):
    """Test cases for ConceptSystem with reflex learning."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.concept_system = ConceptSystem()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_learn_new_reflex(self):
        """Test learning new reflex patterns."""
        # Test learning a reflex
        success = self.concept_system.learn_new_reflex(
            input_text="hello world",
            response_text="Hello to you too!"
        )
        
        self.assertTrue(success)
    
    def test_extract_concepts_from_text(self):
        """Test concept extraction from text."""
        concepts = self.concept_system._extract_concepts_from_text(
            "hello world this is a test"
        )
        
        self.assertIsInstance(concepts, list)
        self.assertIn("hello", concepts)
        self.assertIn("world", concepts)
        self.assertIn("test", concepts)


class TestMemorySystemIntegration(unittest.TestCase):
    """Test cases for MemorySystem with reflex logging."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_system = MemorySystem()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_log_reflex_hit(self):
        """Test logging reflex hits."""
        memory_id = self.memory_system.log_reflex_hit(
            user_input="hello",
            response="hi there",
            pattern="HELLO"
        )
        
        self.assertIsNotNone(memory_id)
        self.assertNotEqual(memory_id, "")
    
    def test_log_openai_fallback(self):
        """Test logging OpenAI fallbacks."""
        memory_id = self.memory_system.log_openai_fallback(
            user_input="Do ants dream?",
            response="[[random_action]] Maybe in their own tiny alien minds!",
            confidence=0.8
        )
        
        self.assertIsNotNone(memory_id)
        self.assertNotEqual(memory_id, "")
    
    def test_get_common_unlearned_phrases(self):
        """Test getting common unlearned phrases."""
        # This test would require setting up memory data
        phrases = self.memory_system.get_common_unlearned_phrases(threshold=1)
        
        self.assertIsInstance(phrases, list)


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_reflex_flow(self):
        """Test complete reflex flow from input to response."""
        # Create AIML engine
        aiml_engine = AIMLReflexEngine(aiml_dir=self.temp_dir)
        
        # Add a pattern
        aiml_engine.add_dynamic_pattern(
            input_text="hello",
            response_text="Hi there! How can I help you?",
            source="test"
        )
        
        # Test the flow
        response = aiml_engine.get_reflex_response("Hello")
        self.assertEqual(response, "Hi there! How can I help you?")
        
        # Test with different case
        response = aiml_engine.get_reflex_response("HELLO")
        self.assertEqual(response, "Hi there! How can I help you?")
    
    def test_learning_flow(self):
        """Test learning flow from OpenAI response."""
        # Create integration
        aiml_engine = AIMLReflexEngine(aiml_dir=self.temp_dir)
        integration = AIMLReflexIntegration(aiml_engine=aiml_engine)
        
        # Simulate learning from OpenAI
        success = integration.learn_from_openai_response(
            user_input="Do ants dream?",
            openai_response="[[random_action]] Maybe in their own tiny alien minds!"
        )
        
        self.assertTrue(success)
        
        # Test that pattern was learned
        response = aiml_engine.get_reflex_response("Do ants dream?")
        self.assertEqual(response, "Maybe in their own tiny alien minds!")


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestAIMLReflexEngine,
        TestAIMLReflexIntegration,
        TestPerceptionSystemIntegration,
        TestJudgmentSystemIntegration,
        TestConceptSystemIntegration,
        TestMemorySystemIntegration,
        TestEndToEndIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running AIML Reflex Layer Tests...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)
