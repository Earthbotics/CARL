#!/usr/bin/env python3
"""
Memory Retrieval System for CARL
This implements human-like memory retrieval processes: recall, recognition, recollection, and relearning.
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import difflib

class MemoryRetrievalSystem:
    """
    Human-like memory retrieval system that implements the four main retrieval processes:
    1. Recall - Retrieving information without external cues
    2. Recognition - Identifying information when presented with cues
    3. Recollection - Reconstructing memories with partial information
    4. Relearning - Relearning information that was previously known
    """
    
    def __init__(self, personality_type: str = "INTP"):
        self.personality_type = personality_type
        self.memories_dir = "memories"
        self.working_memory_file = "working_memory.json"
        
        # Personality-based retrieval preferences
        self.retrieval_preferences = self._initialize_retrieval_preferences()
        
        # Cognitive load simulation
        self.cognitive_load = 0.0  # 0.0 to 1.0
        self.retrieval_attempts = 0
        self.last_retrieval_time = None
        
        # Memory consolidation factors
        self.emotional_intensity_threshold = 0.3
        self.recency_weight = 0.4
        self.frequency_weight = 0.3
        self.importance_weight = 0.3
        
        # Fuzzy matching parameters
        self.fuzzy_match_threshold = 0.6  # Lowered threshold for better matching
        self.synonym_mappings = {
            'toy': ['plaything', 'game', 'doll', 'figure', 'chomp', 'dino', 'dinosaur', 'chomp_and_count_dino'],
            'dinosaur': ['dino', 'prehistoric', 'reptile', 'chomp_and_count_dino', 'chomp'],
            'chomp': ['bite', 'chew', 'gnaw', 'chomp_and_count_dino', 'dino', 'dinosaur', 'toy', 'plaything'],
            'cat': ['feline', 'kitty', 'pussycat'],
            'molly': ['mollie', 'molli'],
            'chomp_and_count_dino': ['chomp', 'dino', 'dinosaur', 'toy', 'plaything', 'green dinosaur', 'vtech'],
            'me': ['self', 'carl', 'robot', 'humanoid', 'reflection', 'mirror']
        }
        
    def _initialize_retrieval_preferences(self) -> Dict:
        """Initialize retrieval preferences based on personality type."""
        preferences = {
            "INTP": {
                "preferred_method": "recall",  # INTPs prefer internal recall
                "search_depth": "deep",        # Deep, thorough search
                "decision_threshold": 0.7,     # High threshold for decisions
                "openness_to_alternatives": 0.9,  # Very open to alternatives
                "cognitive_ticks_for_search": 3,  # More ticks for thorough search
                "randomness_factor": 0.3       # Some randomness in search
            },
            "ISFP": {
                "preferred_method": "recognition",
                "search_depth": "moderate",
                "decision_threshold": 0.6,
                "openness_to_alternatives": 0.7,
                "cognitive_ticks_for_search": 2,
                "randomness_factor": 0.2
            },
            "INFP": {
                "preferred_method": "recollection",
                "search_depth": "deep",
                "decision_threshold": 0.6,
                "openness_to_alternatives": 0.8,
                "cognitive_ticks_for_search": 3,
                "randomness_factor": 0.4
            },
            "default": {
                "preferred_method": "recall",
                "search_depth": "moderate",
                "decision_threshold": 0.6,
                "openness_to_alternatives": 0.7,
                "cognitive_ticks_for_search": 2,
                "randomness_factor": 0.3
            }
        }
        
        return preferences.get(self.personality_type, preferences["default"])
    
    def _calculate_levenshtein_similarity(self, str1: str, str2: str) -> float:
        """Calculate Levenshtein similarity between two strings (0.0 to 1.0)."""
        if not str1 or not str2:
            return 0.0
        
        str1, str2 = str1.lower(), str2.lower()
        if str1 == str2:
            return 1.0
        
        # Use difflib for sequence matching
        matcher = difflib.SequenceMatcher(None, str1, str2)
        return matcher.ratio()
    
    def _fuzzy_match_objects(self, query: str, concept_data: Dict) -> Tuple[bool, float]:
        """
        Perform fuzzy matching against concept template data.
        
        Args:
            query: The object name to match
            concept_data: Concept data from concept_template.json
            
        Returns:
            Tuple of (is_match, confidence_score)
        """
        try:
            query_lower = query.lower().strip()
            
            # Direct match check
            if query_lower in concept_data.get('word', '').lower():
                return True, 1.0
            
            # Check against keywords
            keywords = concept_data.get('keywords', [])
            for keyword in keywords:
                if self._calculate_levenshtein_similarity(query_lower, keyword.lower()) >= self.fuzzy_match_threshold:
                    return True, self._calculate_levenshtein_similarity(query_lower, keyword.lower())
            
            # Check Learning_Integration for additional keywords
            learning_integration = concept_data.get('Learning_Integration', {})
            if learning_integration:
                # Extract keywords from Learning_Integration
                integration_text = str(learning_integration).lower()
                if self._calculate_levenshtein_similarity(query_lower, integration_text) >= self.fuzzy_match_threshold:
                    return True, self._calculate_levenshtein_similarity(query_lower, integration_text)
            
            # Check synonym mappings
            for base_word, synonyms in self.synonym_mappings.items():
                if query_lower == base_word:
                    # Check if any synonyms match concept keywords
                    for synonym in synonyms:
                        for keyword in keywords:
                            if synonym.lower() in keyword.lower():
                                return True, 0.8
                
                # Check if query matches any synonyms
                for synonym in synonyms:
                    if self._calculate_levenshtein_similarity(query_lower, synonym) >= self.fuzzy_match_threshold:
                        # Check if base word matches concept
                        if base_word in concept_data.get('word', '').lower():
                            return True, self._calculate_levenshtein_similarity(query_lower, synonym)
                
                # Check if query matches base word and concept has synonyms
                if query_lower == base_word:
                    concept_word = concept_data.get('word', '').lower()
                    if any(synonym.lower() in concept_word for synonym in synonyms):
                        return True, 0.9
            
            # Check related concepts for better matching
            related_concepts = concept_data.get('related_concepts', [])
            for related in related_concepts:
                related_lower = related.lower()
                # Direct match with related concept
                if query_lower == related_lower:
                    return True, 0.9
                # Fuzzy match with related concept
                if self._calculate_levenshtein_similarity(query_lower, related_lower) >= self.fuzzy_match_threshold:
                    return True, self._calculate_levenshtein_similarity(query_lower, related_lower)
                # Check if query is a synonym of related concept
                for base_word, synonyms in self.synonym_mappings.items():
                    if related_lower == base_word and query_lower in [s.lower() for s in synonyms]:
                        return True, 0.8
            
            return False, 0.0
            
        except Exception as e:
            print(f"Error in fuzzy matching: {e}")
            return False, 0.0
    
    def _extract_keywords_from_learning_integration(self, learning_integration: Dict) -> List[str]:
        """Extract keywords from Learning_Integration data."""
        keywords = []
        try:
            # Convert to string and extract meaningful words
            integration_str = str(learning_integration).lower()
            
            # Common object-related keywords to look for
            object_keywords = ['toy', 'dinosaur', 'chomp', 'cat', 'molly', 'figure', 'doll', 'game', 'plaything']
            
            for keyword in object_keywords:
                if keyword in integration_str:
                    keywords.append(keyword)
            
            # Extract any quoted strings or specific terms
            import re
            quoted_terms = re.findall(r'"([^"]*)"', integration_str)
            keywords.extend(quoted_terms)
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def retrieve_memory(self, query: str = None, context: Dict = None, 
                       cognitive_ticks: int = 0) -> Dict:
        """
        Main memory retrieval method that simulates human memory search.
        
        Enhanced with fuzzy matching for object recognition queries.
        
        Args:
            query: Specific query for memory search
            context: Current context and emotional state
            cognitive_ticks: Number of cognitive processing ticks (simulates thinking time)
            
        Returns:
            Dict: Memory retrieval result with process type and memory data
        """
        try:
            # Check for object recognition queries first
            if query and self._is_object_recognition_query(query):
                return self._process_object_recognition_query(query, context)
            
            # Check for entity recall queries (people, pets, etc.)
            if query and self._is_entity_recall_query(query):
                return self._process_entity_recall_query(query, context)
            
            # Update cognitive load based on retrieval attempts
            self._update_cognitive_load()
            
            # Determine retrieval strategy based on personality and context
            retrieval_strategy = self._determine_retrieval_strategy(query, context, cognitive_ticks)
            
            # Execute the chosen retrieval process
            if retrieval_strategy["method"] == "recall":
                result = self._process_recall(query, context, cognitive_ticks)
            elif retrieval_strategy["method"] == "recognition":
                result = self._process_recognition(query, context, cognitive_ticks)
            elif retrieval_strategy["method"] == "recollection":
                result = self._process_recollection(query, context, cognitive_ticks)
            elif retrieval_strategy["method"] == "relearning":
                result = self._process_relearning(query, context, cognitive_ticks)
            else:
                result = self._process_recall(query, context, cognitive_ticks)  # Default
            
            # Add retrieval metadata
            result["retrieval_strategy"] = retrieval_strategy
            result["cognitive_load"] = self.cognitive_load
            result["personality_type"] = self.personality_type
            result["retrieval_timestamp"] = datetime.now().isoformat()
            
            # Update retrieval statistics
            self.retrieval_attempts += 1
            self.last_retrieval_time = datetime.now()
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "error",
                "memory": None,
                "confidence": 0.0
            }
    
    def _determine_retrieval_strategy(self, query: str, context: Dict, 
                                    cognitive_ticks: int) -> Dict:
        """Determine the best retrieval strategy based on context and personality."""
        
        preferences = self.retrieval_preferences
        
        # First, check for specific query patterns that strongly indicate method
        query_lower = query.lower() if query else ""
        
        # Recognition patterns (strongest indicators)
        if any(word in query_lower for word in ["recognize", "identify", "see", "when we", "do you remember when"]):
            method = "recognition"
        # Recollection patterns
        elif any(word in query_lower for word in ["reconstruct", "piece together", "think about", "reflect on"]):
            method = "recollection"
        # Relearning patterns
        elif any(word in query_lower for word in ["yesterday", "last week", "forgotten", "remind me"]):
            method = "relearning"
        # Recall patterns
        elif any(word in query_lower for word in ["share a memory", "tell me about", "what happened", "recall"]):
            method = "recall"
        else:
            # Base strategy on personality preferences
            base_method = preferences["preferred_method"]
            
            # Adjust based on cognitive ticks (more ticks = deeper search)
            if cognitive_ticks >= preferences["cognitive_ticks_for_search"]:
                if base_method == "recall":
                    method = "recollection"  # Deeper recall becomes recollection
                elif base_method == "recognition":
                    method = "recall"        # Deeper recognition becomes recall
                else:
                    method = base_method
            else:
                method = base_method
        
        # Add randomness for personality openness (but less frequently)
        if random.random() < preferences["randomness_factor"] * 0.5:  # Reduce randomness
            methods = ["recall", "recognition", "recollection", "relearning"]
            method = random.choice(methods)
        
        return {
            "method": method,
            "search_depth": preferences["search_depth"],
            "decision_threshold": preferences["decision_threshold"],
            "openness_to_alternatives": preferences["openness_to_alternatives"]
        }
    
    def _process_recall(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
        """
        Process recall - retrieving information without external cues.
        This is the most effortful retrieval process.
        """
        try:
            # Load all available memories
            memories = self._load_all_memories()
            
            if not memories:
                return {
                    "success": False,
                    "method": "recall",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No memories available for recall"
                }
            
            # Calculate recall probability based on cognitive effort
            recall_probability = min(0.3 + (cognitive_ticks * 0.15), 0.9)
            
            # Apply cognitive load penalty
            recall_probability *= (1.0 - self.cognitive_load * 0.3)
            
            # Determine search scope based on personality
            if self.personality_type == "INTP":
                # INTPs do deep, systematic search
                search_scope = min(len(memories), 50)  # Search more memories
                search_pattern = "systematic"
            else:
                search_scope = min(len(memories), 20)  # Standard search
                search_pattern = "selective"
            
            # Simulate recall process
            recalled_memories = []
            
            for i, memory in enumerate(memories[:search_scope]):
                # Calculate recall probability for this memory
                memory_recall_prob = self._calculate_memory_recall_probability(memory, context)
                
                # Apply search pattern
                if search_pattern == "systematic":
                    # Systematic search - check each memory thoroughly
                    if random.random() < memory_recall_prob * recall_probability:
                        recalled_memories.append(memory)
                else:
                    # Selective search - focus on most relevant
                    if memory_recall_prob > 0.5 and random.random() < recall_probability:
                        recalled_memories.append(memory)
                
                # Simulate thinking time
                if cognitive_ticks > 0:
                    # More ticks = more thorough search
                    pass
            
            # Select best recalled memory
            if recalled_memories:
                best_memory = max(recalled_memories, 
                                key=lambda m: self._calculate_memory_relevance(m, context))
                
                confidence = self._calculate_recall_confidence(best_memory, context, cognitive_ticks)
                
                return {
                    "success": True,
                    "method": "recall",
                    "memory": best_memory,
                    "confidence": confidence,
                    "reasoning": f"Successfully recalled memory through systematic search (found {len(recalled_memories)} candidates)",
                    "search_scope": search_scope,
                    "search_pattern": search_pattern
                }
            else:
                return {
                    "success": False,
                    "method": "recall",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": f"Recall attempt failed - no memories retrieved (probability: {recall_probability:.2f})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "recall",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Recall process error: {str(e)}"
            }
    
    def _process_recognition(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
        """
        Process recognition - identifying information when presented with cues.
        This is easier than recall but requires external cues.
        """
        try:
            memories = self._load_all_memories()
            
            if not memories:
                return {
                    "success": False,
                    "method": "recognition",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No memories available for recognition"
                }
            
            # Extract recognition cues from query and context
            recognition_cues = self._extract_recognition_cues(query, context)
            
            if not recognition_cues:
                return {
                    "success": False,
                    "method": "recognition",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No recognition cues found in query or context"
                }
            
            # Find memories that match recognition cues
            matching_memories = []
            
            for memory in memories:
                match_score = self._calculate_recognition_match(memory, recognition_cues)
                if match_score > 0.3:  # Recognition threshold
                    matching_memories.append((memory, match_score))
            
            # Sort by match score
            matching_memories.sort(key=lambda x: x[1], reverse=True)
            
            if matching_memories:
                best_memory, best_score = matching_memories[0]
                
                # Recognition is generally more confident than recall
                confidence = min(0.8 + (best_score * 0.2), 0.95)
                
                return {
                    "success": True,
                    "method": "recognition",
                    "memory": best_memory,
                    "confidence": confidence,
                    "reasoning": f"Recognized memory based on cues: {recognition_cues} (match score: {best_score:.2f})",
                    "matching_cues": recognition_cues,
                    "match_score": best_score
                }
            else:
                return {
                    "success": False,
                    "method": "recognition",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": f"No memories recognized for cues: {recognition_cues}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "recognition",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Recognition process error: {str(e)}"
            }
    
    def _process_recollection(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
        """
        Process recollection - reconstructing memories with partial information.
        This involves piecing together fragments of memories.
        """
        try:
            memories = self._load_all_memories()
            
            if not memories:
                return {
                    "success": False,
                    "method": "recollection",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No memories available for recollection"
                }
            
            # Extract memory fragments from query and context
            memory_fragments = self._extract_memory_fragments(query, context)
            
            # Find memories that contain these fragments
            fragment_matches = []
            
            for memory in memories:
                fragment_score = self._calculate_fragment_match(memory, memory_fragments)
                if fragment_score > 0.2:  # Fragment matching threshold
                    fragment_matches.append((memory, fragment_score))
            
            if fragment_matches:
                # Sort by fragment match score
                fragment_matches.sort(key=lambda x: x[1], reverse=True)
                
                # Reconstruct memory from best matches
                reconstructed_memory = self._reconstruct_memory(fragment_matches, context)
                
                # Recollection confidence is moderate (reconstruction can be imperfect)
                confidence = min(0.6 + (fragment_matches[0][1] * 0.3), 0.85)
                
                return {
                    "success": True,
                    "method": "recollection",
                    "memory": reconstructed_memory,
                    "confidence": confidence,
                    "reasoning": f"Reconstructed memory from {len(fragment_matches)} fragment matches",
                    "fragments_used": memory_fragments,
                    "fragment_score": fragment_matches[0][1]
                }
            else:
                return {
                    "success": False,
                    "method": "recollection",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": f"Could not reconstruct memory from fragments: {memory_fragments}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "recollection",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Recollection process error: {str(e)}"
            }
    
    def _process_relearning(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
        """
        Process relearning - relearning information that was previously known.
        This is the easiest retrieval process but indicates some forgetting occurred.
        """
        try:
            memories = self._load_all_memories()
            
            if not memories:
                return {
                    "success": False,
                    "method": "relearning",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No memories available for relearning"
                }
            
            # Find memories that might need relearning (older, less accessed)
            relearning_candidates = []
            
            for memory in memories:
                relearning_score = self._calculate_relearning_score(memory)
                if relearning_score > 0.4:  # Relearning threshold
                    relearning_candidates.append((memory, relearning_score))
            
            if relearning_candidates:
                # Sort by relearning score
                relearning_candidates.sort(key=lambda x: x[1], reverse=True)
                
                # Select memory for relearning
                relearned_memory = relearning_candidates[0][0]
                relearning_score = relearning_candidates[0][1]
                
                # Relearning is very confident (it's like "oh yeah, I remember now!")
                confidence = min(0.9 + (relearning_score * 0.1), 0.98)
                
                return {
                    "success": True,
                    "method": "relearning",
                    "memory": relearned_memory,
                    "confidence": confidence,
                    "reasoning": f"Relearned memory that was partially forgotten (relearning score: {relearning_score:.2f})",
                    "relearning_score": relearning_score
                }
            else:
                return {
                    "success": False,
                    "method": "relearning",
                    "memory": None,
                    "confidence": 0.0,
                    "reasoning": "No memories needed relearning"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "relearning",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Relearning process error: {str(e)}"
            }
    
    def _is_object_recognition_query(self, query: str) -> bool:
        """Check if the query is asking about object recognition."""
        try:
            query_lower = query.lower()
            object_recognition_patterns = [
                'do you remember this object',
                'do you remember this',
                'have you seen this',
                'what is this',
                'do you know what this is',
                'recognize this',
                'seen this before',
                'do you see',
                'what do you see',
                'can you see',
                'do you recognize',
                'what object',
                'remember this',
                'what is that',
                'can you identify',
                'what do you think this is'
            ]
            
            return any(pattern in query_lower for pattern in object_recognition_patterns)
            
        except Exception as e:
            print(f"Error checking object recognition query: {e}")
            return False
    
    def _is_entity_recall_query(self, query: str) -> bool:
        """Check if the query is asking about entity recall (people, pets, etc.)."""
        try:
            query_lower = query.lower()
            entity_recall_patterns = [
                'do you remember the name of',
                'what is the name of',
                'do you know the name of',
                'remember the name',
                'what\'s the name of',
                'who is',
                'what is'
            ]
            
            return any(pattern in query_lower for pattern in entity_recall_patterns)
            
        except Exception as e:
            print(f"Error checking entity recall query: {e}")
            return False
    
    def _process_object_recognition_query(self, query: str, context: Dict) -> Dict:
        """Process object recognition queries using enhanced concept matching and fuzzy search."""
        try:
            # 🔧 ENHANCEMENT: Search for vision memories with concept associations first
            vision_memories = self._search_vision_memories_with_concepts(query)
            
            # 🔧 ENHANCEMENT: Search episodic memory for object-related events
            episodic_memories = self._search_episodic_memory_for_object_recognition(query)
            
            # Search for objects in things directory using fuzzy matching
            things_dir = "things"
            concepts_dir = "concepts"
            best_match = None
            best_confidence = 0.0
            
            # 🔧 ENHANCEMENT: Check vision memories first (highest priority)
            if vision_memories:
                for memory in vision_memories:
                    confidence = memory.get('confidence', 0.0)
                    # Boost confidence if episodic memory context is available
                    if memory.get('episodic_context'):
                        confidence = min(1.0, confidence + 0.2)
                    
                    # 🔧 CRITICAL: Boost ARC detection confidence significantly
                    if memory.get('arc_trusted', False) or memory.get('source') == 'arc_detection':
                        confidence = min(1.0, confidence + 0.3)  # Major boost for ARC detection
                        self.log(f"🎯 ARC detection confidence boost applied: {confidence}")
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = memory
                        best_match['source'] = 'vision_memory'
            
            # 🔧 ENHANCEMENT: Check episodic memories (second priority)
            if episodic_memories and not best_match:
                for memory in episodic_memories:
                    confidence = memory.get('confidence', 0.0)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = memory
                        best_match['source'] = 'episodic_memory'
            
            # Search in things directory
            if os.path.exists(things_dir):
                for filename in os.listdir(things_dir):
                    if filename.endswith('.json'):
                        thing_name = filename.replace('_self_learned.json', '').replace('.json', '')
                        
                        # Try fuzzy matching against the thing name
                        confidence = self._calculate_levenshtein_similarity(query.lower(), thing_name.lower())
                        
                        # Also check against synonyms
                        for base_word, synonyms in self.synonym_mappings.items():
                            if thing_name.lower() == base_word:
                                for synonym in synonyms:
                                    synonym_confidence = self._calculate_levenshtein_similarity(query.lower(), synonym.lower())
                                    confidence = max(confidence, synonym_confidence)
                        
                        # 🔧 ENHANCEMENT: Special handling for Chomp
                        if thing_name.lower() == 'chomp':
                            # Check if query matches any Chomp-related terms
                            chomp_terms = ['chomp', 'dino', 'dinosaur', 'toy', 'green dinosaur', 'vtech']
                            for term in chomp_terms:
                                if term in query.lower():
                                    confidence = max(confidence, 0.9)  # High confidence for Chomp matches
                                    break
                        
                        if confidence > best_confidence and confidence >= self.fuzzy_match_threshold:
                            best_confidence = confidence
                            best_match = {
                                'name': thing_name,
                                'filename': filename,
                                'confidence': confidence,
                                'directory': things_dir
                            }
            
            # Search in concepts directory for more comprehensive matches
            if os.path.exists(concepts_dir):
                for filename in os.listdir(concepts_dir):
                    if filename.endswith('.json'):
                        try:
                            concept_file = os.path.join(concepts_dir, filename)
                            with open(concept_file, 'r', encoding='utf-8') as f:
                                concept_data = json.load(f)
                            
                            # Check against concept name
                            concept_name = concept_data.get('word', filename.replace('.json', ''))
                            confidence = self._calculate_levenshtein_similarity(query.lower(), concept_name.lower())
                            
                            # Check against keywords
                            keywords = concept_data.get('keywords', [])
                            for keyword in keywords:
                                keyword_confidence = self._calculate_levenshtein_similarity(query.lower(), keyword.lower())
                                confidence = max(confidence, keyword_confidence)
                            
                            # Check against related concepts
                            related_concepts = concept_data.get('related_concepts', [])
                            for related in related_concepts:
                                related_confidence = self._calculate_levenshtein_similarity(query.lower(), related.lower())
                                confidence = max(confidence, related_confidence)
                            
                            # 🔧 ENHANCEMENT: Special handling for chomp_and_count_dino concept
                            if concept_name.lower() == 'chomp_and_count_dino':
                                # Check if query matches any Chomp-related terms
                                chomp_terms = ['chomp', 'dino', 'dinosaur', 'toy', 'green dinosaur', 'vtech', 'chomp and count']
                                for term in chomp_terms:
                                    if term in query.lower():
                                        confidence = max(confidence, 0.95)  # Very high confidence for Chomp concept matches
                                        break
                                
                                # Also check keywords from the concept data
                                keywords = concept_data.get('keywords', [])
                                for keyword in keywords:
                                    if keyword.lower() in query.lower():
                                        confidence = max(confidence, 0.9)
                                        break
                            
                            if confidence > best_confidence and confidence >= self.fuzzy_match_threshold:
                                best_confidence = confidence
                                best_match = {
                                    'name': concept_name,
                                    'filename': filename,
                                    'confidence': confidence,
                                    'directory': concepts_dir,
                                    'concept_data': concept_data
                                }
                                
                        except Exception as e:
                            print(f"Error reading concept file {filename}: {e}")
                            continue
            
            if best_match:
                # Load the matched object data
                if best_match.get('concept_data'):
                    # Use concept data directly
                    thing_data = best_match['concept_data']
                    filepath = os.path.join(best_match['directory'], best_match['filename'])
                else:
                    # Load from things directory
                    thing_file = os.path.join(best_match['directory'], best_match['filename'])
                    try:
                        with open(thing_file, 'r', encoding='utf-8') as f:
                            thing_data = json.load(f)
                        filepath = thing_file
                    except Exception as e:
                        print(f"Error loading thing data: {e}")
                        return {
                            "success": False,
                            "method": "object_recognition",
                            "memory": None,
                            "confidence": 0.0,
                            "reasoning": f"Error loading object data: {str(e)}"
                        }
                
                # 🔧 ENHANCEMENT: Generate first-person response from concept data
                response = self._generate_object_recognition_response(best_match, thing_data)
                
                return {
                    "success": True,
                    "method": "object_recognition",
                    "memory": {
                        "object_name": best_match['name'],
                        "object_data": thing_data,
                        "confidence": best_confidence,
                        "filepath": filepath,
                        "keywords": thing_data.get('keywords', []),
                        "related_concepts": thing_data.get('related_concepts', []),
                        "contextual_usage": thing_data.get('contextual_usage', []),
                        "source": best_match.get('source', 'concept_file')
                    },
                    "confidence": best_confidence,
                    "reasoning": f"Fuzzy matched '{query}' to object '{best_match['name']}' with {best_confidence:.2f} confidence",
                    "response": response
                }
            
            # If no fuzzy match found, return failure with fallback response
            return {
                "success": False,
                "method": "object_recognition",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"No objects found matching '{query}' with confidence >= {self.fuzzy_match_threshold}",
                "response": "I don't recognize this object in my memory. Could you tell me more about it?"
            }
            
        except Exception as e:
            print(f"Error processing object recognition query: {e}")
            return {
                "success": False,
                "method": "object_recognition",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Error processing object recognition: {str(e)}"
            }
    
    def _search_vision_memories_with_concepts(self, query: str) -> List[Dict]:
        """Search vision memories that have concept associations."""
        try:
            import os
            import json
            from datetime import datetime, timedelta
            
            vision_memories = []
            memories_dir = "memories"
            
            if not os.path.exists(memories_dir):
                return vision_memories
            
            # Search recent vision memories (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # 🔧 ENHANCEMENT: Search both main memories directory and STM/LTM subdirectories
            search_dirs = [memories_dir]
            if os.path.exists(os.path.join(memories_dir, 'stm')):
                search_dirs.append(os.path.join(memories_dir, 'stm'))
            if os.path.exists(os.path.join(memories_dir, 'ltm')):
                search_dirs.append(os.path.join(memories_dir, 'ltm'))
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                    
                for filename in os.listdir(search_dir):
                    if not filename.endswith('.json') or not filename.startswith('vision_'):
                        continue
                    
                    try:
                        memory_file = os.path.join(search_dir, filename)
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                        
                        # Check if this is a vision memory with concept associations
                        if (memory_data.get('type') == 'vision_object_detection' and 
                            memory_data.get('concepts') and
                            memory_data.get('concept_match')):
                            
                            # Calculate relevance to query
                            relevance_score = self._calculate_vision_memory_relevance(memory_data, query)
                            
                            if relevance_score > 0.3:  # Minimum relevance threshold
                                vision_memories.append({
                                    'memory_data': memory_data,
                                    'confidence': relevance_score,
                                    'timestamp': memory_data.get('timestamp'),
                                    'object_name': memory_data.get('vision_data', {}).get('object_name', 'unknown'),
                                    'concepts': memory_data.get('concepts', []),
                                    'concept_match': memory_data.get('concept_match', {}),
                                    'source_dir': search_dir  # Track which directory this came from
                                })
                                
                    except Exception as e:
                        print(f"Error reading vision memory {filename}: {e}")
                        continue
            
            # 🔧 ENHANCEMENT: Sort by emotional experience (dopamine/serotonin levels) first, then confidence
            vision_memories = self._sort_memories_by_emotional_experience(vision_memories)
            return vision_memories[:5]  # Return top 5 matches
            
        except Exception as e:
            print(f"Error searching vision memories: {e}")
            return []
    
    def _sort_memories_by_emotional_experience(self, memories: List[Dict]) -> List[Dict]:
        """Sort memories by emotional experience (dopamine/serotonin levels) - highest first."""
        try:
            def get_emotional_score(memory):
                """Calculate emotional score based on dopamine and serotonin levels."""
                try:
                    # Get emotional state from memory
                    emotional_state = memory.get('memory_data', {}).get('neucogar_emotional_state', {})
                    if not emotional_state:
                        emotional_state = memory.get('neucogar_emotional_state', {})
                    
                    # Extract neurotransmitter levels
                    neuro_coords = emotional_state.get('neuro_coordinates', {})
                    dopamine = neuro_coords.get('dopamine', 0.0)
                    serotonin = neuro_coords.get('serotonin', 0.0)
                    
                    # Calculate emotional experience score (dopamine + serotonin)
                    emotional_score = dopamine + serotonin
                    
                    # Boost for high-intensity emotions
                    intensity = emotional_state.get('intensity', 0.0)
                    emotional_score += intensity * 0.5
                    
                    return emotional_score
                except:
                    return 0.0
            
            # Sort by emotional score (highest first), then by confidence, then by timestamp
            memories.sort(key=lambda x: (
                get_emotional_score(x),
                x.get('confidence', 0.0),
                x.get('timestamp', '')
            ), reverse=True)
            
            return memories
            
        except Exception as e:
            print(f"Error sorting memories by emotional experience: {e}")
            return memories
    
    def _calculate_vision_memory_relevance(self, memory_data: Dict, query: str) -> float:
        """Calculate relevance score for vision memory against query."""
        try:
            query_lower = query.lower()
            score = 0.0
            
            # 🔧 ENHANCEMENT: Handle generic object recognition queries
            generic_object_queries = [
                'do you remember this object',
                'do you remember this',
                'have you seen this',
                'what is this',
                'do you know what this is',
                'recognize this',
                'seen this before',
                'what do you see',
                'can you see',
                'do you recognize',
                'what object',
                'remember this',
                'what is that',
                'can you identify',
                'what do you think this is'
            ]
            
            # If this is a generic object recognition query, boost recent vision memories
            if any(pattern in query_lower for pattern in generic_object_queries):
                # Check if this is a recent vision memory (within last 5 minutes)
                memory_timestamp = memory_data.get('timestamp')
                if memory_timestamp:
                    try:
                        from datetime import datetime, timedelta
                        memory_time = datetime.fromisoformat(memory_timestamp.replace('Z', '+00:00'))
                        time_diff = datetime.now() - memory_time.replace(tzinfo=None)
                        if time_diff <= timedelta(minutes=5):
                            score += 0.9  # High relevance for recent vision memories
                        elif time_diff <= timedelta(hours=1):
                            score += 0.7  # Medium relevance for recent vision memories
                        elif time_diff <= timedelta(hours=24):
                            score += 0.5  # Lower relevance for older vision memories
                    except:
                        score += 0.6  # Default relevance if timestamp parsing fails
            
            # Check object name
            object_name = memory_data.get('vision_data', {}).get('object_name', '').lower()
            if object_name in query_lower:
                score += 0.8
            
            # Check concepts
            concepts = memory_data.get('concepts', [])
            for concept in concepts:
                if concept.lower() in query_lower:
                    score += 0.6
            
            # Check concept match keywords
            concept_match = memory_data.get('concept_match', {})
            concept_keywords = concept_match.get('concepts', [])
            for keyword in concept_keywords:
                if keyword.lower() in query_lower:
                    score += 0.4
            
            # 🔧 ENHANCEMENT: Boost score for Chomp-related memories
            chomp_keywords = ['chomp', 'dino', 'dinosaur', 'toy', 'chomp_and_count_dino']
            for keyword in chomp_keywords:
                if keyword in object_name or keyword in str(concepts).lower() or keyword in str(concept_keywords).lower():
                    score += 0.3
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            print(f"Error calculating vision memory relevance: {e}")
            return 0.0
    
    def _search_episodic_memory_for_object_recognition(self, query: str) -> List[Dict]:
        """
        Search episodic memory for object-related events to support object recognition queries.
        
        Args:
            query: The object recognition query
            
        Returns:
            List[Dict]: List of relevant episodic memories with confidence scores
        """
        try:
            import os
            import json
            from datetime import datetime, timedelta
            
            memories_dir = "memories"
            episodic_dir = os.path.join(memories_dir, "episodic")
            
            if not os.path.exists(episodic_dir):
                return []
            
            # Extract potential object names from the query
            query_lower = query.lower()
            object_keywords = []
            
            # Common object recognition patterns
            if 'this object' in query_lower or 'this' in query_lower:
                # Look for recent vision detections
                object_keywords.extend(['vision', 'object', 'detected', 'camera'])
            
            # Add common object terms
            common_objects = ['toy', 'dinosaur', 'chomp', 'cat', 'molly', 'person', 'chair', 'computer']
            for obj in common_objects:
                if obj in query_lower:
                    object_keywords.append(obj)
            
            # Look for recent episodic memories (last 7 days for object recognition)
            cutoff_date = datetime.now() - timedelta(days=7)
            relevant_memories = []
            
            for filename in os.listdir(episodic_dir):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    memory_file = os.path.join(episodic_dir, filename)
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memory_data = json.load(f)
                    
                    # Check if memory is recent enough
                    memory_timestamp = memory_data.get('timestamp', '')
                    if memory_timestamp:
                        try:
                            memory_date = datetime.fromisoformat(memory_timestamp.replace('Z', '+00:00'))
                            if memory_date < cutoff_date:
                                continue
                        except:
                            continue
                    
                    # Check if memory contains object-related information
                    memory_text = str(memory_data).lower()
                    confidence = 0.0
                    
                    for keyword in object_keywords:
                        if keyword in memory_text:
                            confidence += 0.3
                    
                    # Boost confidence for vision-related memories
                    if 'vision' in memory_text or 'object' in memory_text:
                        confidence += 0.2
                    
                    # Boost confidence for specific object mentions
                    if any(obj in memory_text for obj in ['chomp', 'dinosaur', 'toy']):
                        confidence += 0.3
                    
                    if confidence > 0.3:  # Minimum threshold
                        relevant_memories.append({
                            'memory_data': memory_data,
                            'confidence': min(1.0, confidence),
                            'timestamp': memory_timestamp,
                            'filename': filename,
                            'matched_keywords': [k for k in object_keywords if k in memory_text]
                        })
                        
                except Exception as e:
                    continue
            
            # Sort by confidence and recency
            relevant_memories.sort(key=lambda x: (x['confidence'], x['timestamp']), reverse=True)
            
            return relevant_memories[:5]  # Return top 5 matches
            
        except Exception as e:
            print(f"Error searching episodic memory for object recognition: {e}")
            return []
    
    def _generate_object_recognition_response(self, best_match: Dict, thing_data: Dict = None) -> str:
        """Generate first-person response for object recognition."""
        try:
            object_name = best_match.get('name', 'unknown')
            source = best_match.get('source', 'concept_file')
            confidence = best_match.get('confidence', 0.0)
            
            if source == 'vision_memory':
                # Response for vision memory match
                memory_data = best_match.get('memory_data', {})
                concept_match = memory_data.get('concept_match', {})
                source_concept = concept_match.get('source_concept', object_name)
                
                if confidence > 0.8:
                    return f"Yes, I remember this object! It's {source_concept}. I've seen it before and it's associated with {', '.join(concept_match.get('concepts', [])[:3])}."
                elif confidence > 0.6:
                    return f"I think I recognize this. It looks like {source_concept} based on what I've seen before."
                else:
                    return f"This looks familiar - it might be {source_concept}, but I'm not entirely sure."
            
            else:
                # Response for concept file match
                if thing_data:
                    keywords = thing_data.get('keywords', [])
                    related_concepts = thing_data.get('related_concepts', [])
                    contextual_usage = thing_data.get('contextual_usage', [])
                    
                    if confidence > 0.8:
                        if contextual_usage:
                            usage = contextual_usage[0] if contextual_usage else f"It's a {object_name}."
                            return f"Yes, I know this! It's {object_name}. {usage}"
                        else:
                            return f"Yes, I recognize this! It's {object_name}, which is related to {', '.join(related_concepts[:3])}."
                    elif confidence > 0.6:
                        return f"I think this is {object_name}. It's associated with {', '.join(keywords[:3])}."
                    else:
                        return f"This might be {object_name}, but I'm not completely certain."
                else:
                    return f"I recognize this as {object_name}."
            
        except Exception as e:
            print(f"Error generating object recognition response: {e}")
            return f"I recognize this object as {object_name}."
    
    def _process_entity_recall_query(self, query: str, context: Dict) -> Dict:
        """Process entity recall queries (people, pets, etc.) using local concept files."""
        try:
            # Search for entities in people and pets directories
            people_dir = "people"
            pets_dir = "pets"
            best_match = None
            best_confidence = 0.0
            
            # Search in people directory
            if os.path.exists(people_dir):
                for filename in os.listdir(people_dir):
                    if filename.endswith('.json'):
                        try:
                            person_file = os.path.join(people_dir, filename)
                            with open(person_file, 'r', encoding='utf-8') as f:
                                person_data = json.load(f)
                            
                            # Check against person name
                            person_name = person_data.get('name', person_data.get('word', filename.replace('.json', '')))
                            confidence = self._calculate_levenshtein_similarity(query.lower(), person_name.lower())
                            
                            # Check against aliases
                            aliases = person_data.get('aliases', [])
                            for alias in aliases:
                                alias_confidence = self._calculate_levenshtein_similarity(query.lower(), alias.lower())
                                confidence = max(confidence, alias_confidence)
                            
                            # Check against keywords
                            keywords = person_data.get('keywords', [])
                            for keyword in keywords:
                                keyword_confidence = self._calculate_levenshtein_similarity(query.lower(), keyword.lower())
                                confidence = max(confidence, keyword_confidence)
                            
                            if confidence > best_confidence and confidence >= self.fuzzy_match_threshold:
                                best_confidence = confidence
                                best_match = {
                                    'name': person_name,
                                    'filename': filename,
                                    'confidence': confidence,
                                    'directory': people_dir,
                                    'entity_data': person_data,
                                    'type': 'person'
                                }
                                
                        except Exception as e:
                            print(f"Error reading person file {filename}: {e}")
                            continue
            
            # Search in pets directory
            if os.path.exists(pets_dir):
                for filename in os.listdir(pets_dir):
                    if filename.endswith('.json'):
                        try:
                            pet_file = os.path.join(pets_dir, filename)
                            with open(pet_file, 'r', encoding='utf-8') as f:
                                pet_data = json.load(f)
                            
                            # Check against pet name
                            pet_name = pet_data.get('name', pet_data.get('word', filename.replace('.json', '')))
                            confidence = self._calculate_levenshtein_similarity(query.lower(), pet_name.lower())
                            
                            # Check against aliases
                            aliases = pet_data.get('aliases', [])
                            for alias in aliases:
                                alias_confidence = self._calculate_levenshtein_similarity(query.lower(), alias.lower())
                                confidence = max(confidence, alias_confidence)
                            
                            # Check against keywords
                            keywords = pet_data.get('keywords', [])
                            for keyword in keywords:
                                keyword_confidence = self._calculate_levenshtein_similarity(query.lower(), keyword.lower())
                                confidence = max(confidence, keyword_confidence)
                            
                            if confidence > best_confidence and confidence >= self.fuzzy_match_threshold:
                                best_confidence = confidence
                                best_match = {
                                    'name': pet_name,
                                    'filename': filename,
                                    'confidence': confidence,
                                    'directory': pets_dir,
                                    'entity_data': pet_data,
                                    'type': 'pet'
                                }
                                
                        except Exception as e:
                            print(f"Error reading pet file {filename}: {e}")
                            continue
            
            if best_match:
                return {
                    "success": True,
                    "method": "entity_recall",
                    "memory": {
                        "entity_name": best_match['name'],
                        "entity_data": best_match['entity_data'],
                        "confidence": best_confidence,
                        "filepath": os.path.join(best_match['directory'], best_match['filename']),
                        "entity_type": best_match['type'],
                        "aliases": best_match['entity_data'].get('aliases', []),
                        "keywords": best_match['entity_data'].get('keywords', [])
                    },
                    "confidence": best_confidence,
                    "reasoning": f"Fuzzy matched '{query}' to {best_match['type']} '{best_match['name']}' with {best_confidence:.2f} confidence"
                }
            
            # If no fuzzy match found, return failure
            return {
                "success": False,
                "method": "entity_recall",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"No entities found matching '{query}' with confidence >= {self.fuzzy_match_threshold}"
            }
            
        except Exception as e:
            print(f"Error processing entity recall query: {e}")
            return {
                "success": False,
                "method": "entity_recall",
                "memory": None,
                "confidence": 0.0,
                "reasoning": f"Error processing entity recall: {str(e)}"
            }
    
    def _load_all_memories(self) -> List[Dict]:
        """Load all available memories from both working memory and long-term memory."""
        memories = []
        
        # Load working memory
        if os.path.exists(self.working_memory_file):
            try:
                with open(self.working_memory_file, 'r') as f:
                    working_memory = json.load(f)
                    items = working_memory.get("items", [])
                    for item in items:
                        memories.append({
                            "type": "working",
                            "content": item.get("content", ""),
                            "context": item.get("context", ""),
                            "importance": item.get("importance", 5),
                            "created": item.get("created", ""),
                            "confidence": item.get("confidence", 1.0)
                        })
            except Exception as e:
                print(f"Error loading working memory: {e}")
        
        # Load long-term memories
        if os.path.exists(self.memories_dir):
            try:
                for filename in os.listdir(self.memories_dir):
                    if filename.endswith('_event.json'):
                        filepath = os.path.join(self.memories_dir, filename)
                        try:
                            with open(filepath, 'r') as f:
                                raw_content = f.read()
                                
                                # Log raw content for debugging
                                if not raw_content.strip():
                                    print(f"⚠️ Empty file detected: {filename}")
                                    continue
                                
                                # Try to parse JSON with error handling
                                try:
                                    memory_data = json.loads(raw_content)
                                except json.JSONDecodeError as json_error:
                                    print(f"❌ Error retrieving long term memory: {json_error}")
                                    print(f"📄 Raw content from {filename}: {repr(raw_content[:200])}")
                                    continue
                                
                                memories.append({
                                    "type": "long_term",
                                    "file": filename,
                                    "what": memory_data.get("WHAT", ""),
                                    "who": memory_data.get("WHO", ""),
                                    "when": memory_data.get("WHEN", ""),
                                    "where": memory_data.get("WHERE", ""),
                                    "why": memory_data.get("WHY", ""),
                                    "how": memory_data.get("HOW", ""),
                                    "nouns": memory_data.get("nouns", []),
                                    "verbs": memory_data.get("verbs", []),
                                    "people": memory_data.get("people", []),
                                    "subjects": memory_data.get("subjects", []),
                                    "emotions": memory_data.get("emotions", {}),
                                    "carl_thought": memory_data.get("carl_thought", {}),
                                    "timestamp": memory_data.get("timestamp", ""),
                                    "created": memory_data.get("created", "")
                                })
                        except Exception as e:
                            print(f"Error loading memory file {filename}: {e}")
            except Exception as e:
                print(f"Error loading long-term memories: {e}")
        
        return memories
    
    def _calculate_memory_recall_probability(self, memory: Dict, context: Dict) -> float:
        """Calculate the probability of recalling a specific memory."""
        probability = 0.5  # Base probability
        
        # Recency effect
        if "created" in memory:
            try:
                created_time = datetime.fromisoformat(memory["created"])
                age_hours = (datetime.now() - created_time).total_seconds() / 3600
                recency_factor = max(0.1, 1.0 - (age_hours / 168))  # Decay over a week
                probability += recency_factor * self.recency_weight
            except:
                pass
        
        # Frequency effect (access count)
        if "access_count" in memory:
            frequency_factor = min(1.0, memory["access_count"] / 10.0)
            probability += frequency_factor * self.frequency_weight
        
        # Importance effect
        if "importance" in memory:
            importance_factor = memory["importance"] / 10.0
            probability += importance_factor * self.importance_weight
        
        # Emotional intensity effect
        if "emotions" in memory and memory["emotions"]:
            max_emotion = max(memory["emotions"].values()) if memory["emotions"] else 0
            if max_emotion > self.emotional_intensity_threshold:
                probability += 0.2
        
        return min(probability, 1.0)
    
    def _calculate_memory_relevance(self, memory: Dict, context: Dict) -> float:
        """Calculate how relevant a memory is to the current context."""
        relevance = 0.0
        
        # Context matching
        if context and "current_emotion" in context:
            if "emotions" in memory and memory["emotions"]:
                # Check emotional similarity
                for emotion, intensity in memory["emotions"].items():
                    if emotion == context["current_emotion"]:
                        relevance += intensity * 0.3
        
        # Temporal relevance
        if "when" in memory and memory["when"]:
            if "recent" in memory["when"].lower() or "today" in memory["when"].lower():
                relevance += 0.4
            elif "yesterday" in memory["when"].lower():
                relevance += 0.2
        
        # Content relevance
        if "what" in memory and memory["what"]:
            relevance += 0.2
        
        # Specific item recall relevance - check for nouns in memory
        if "nouns" in memory and memory["nouns"]:
            # If this is a recall request for specific items, boost relevance
            if context and "query" in context and context["query"]:
                query_lower = context["query"].lower()
                if any(word in query_lower for word in ["remember", "recall", "what", "items", "things"]):
                    # Check if memory contains nouns (items to remember)
                    if memory["nouns"]:
                        relevance += 0.8  # High relevance for item recall requests
        
        return min(relevance, 1.0)
    
    def _calculate_recall_confidence(self, memory: Dict, context: Dict, cognitive_ticks: int) -> float:
        """Calculate confidence in recalled memory."""
        confidence = 0.5  # Base confidence
        
        # Cognitive effort increases confidence
        confidence += min(cognitive_ticks * 0.1, 0.3)
        
        # Memory strength factors
        if "confidence" in memory:
            confidence += memory["confidence"] * 0.2
        
        if "importance" in memory:
            confidence += (memory["importance"] / 10.0) * 0.1
        
        # Context consistency
        if context and "current_emotion" in context:
            if "emotions" in memory and memory["emotions"]:
                if context["current_emotion"] in memory["emotions"]:
                    confidence += 0.1
        
        return min(confidence, 0.95)
    
    def _extract_recognition_cues(self, query: str, context: Dict) -> List[str]:
        """Extract recognition cues from query and context."""
        cues = []
        
        if query:
            # Extract key words as cues
            words = query.lower().split()
            cues.extend([word for word in words if len(word) > 3])
        
        if context:
            # Extract contextual cues
            if "current_emotion" in context:
                cues.append(context["current_emotion"])
            if "current_location" in context:
                cues.append(context["current_location"])
        
        return list(set(cues))  # Remove duplicates
    
    def _calculate_recognition_match(self, memory: Dict, cues: List[str]) -> float:
        """Calculate how well a memory matches recognition cues."""
        if not cues:
            return 0.0
        
        match_score = 0.0
        total_cues = len(cues)
        
        for cue in cues:
            # Search in memory content
            memory_text = ""
            if "content" in memory:
                memory_text += memory["content"] + " "
            if "what" in memory:
                memory_text += memory["what"] + " "
            if "who" in memory:
                memory_text += memory["who"] + " "
            if "where" in memory:
                memory_text += memory["where"] + " "
            
            memory_text = memory_text.lower()
            
            if cue in memory_text:
                match_score += 1.0
            elif any(word in memory_text for word in cue.split()):
                match_score += 0.5
        
        return match_score / total_cues
    
    def _extract_memory_fragments(self, query: str, context: Dict) -> List[str]:
        """Extract memory fragments from query and context."""
        fragments = []
        
        if query:
            # Extract potential memory fragments
            words = query.lower().split()
            fragments.extend([word for word in words if len(word) > 2])
        
        if context:
            # Extract contextual fragments
            if "current_emotion" in context:
                fragments.append(context["current_emotion"])
            if "recent_events" in context:
                fragments.extend(context["recent_events"][:3])
        
        return list(set(fragments))
    
    def _calculate_fragment_match(self, memory: Dict, fragments: List[str]) -> float:
        """Calculate how well memory fragments match a memory."""
        if not fragments:
            return 0.0
        
        match_score = 0.0
        total_fragments = len(fragments)
        
        memory_text = ""
        if "content" in memory:
            memory_text += memory["content"] + " "
        if "what" in memory:
            memory_text += memory["what"] + " "
        if "who" in memory:
            memory_text += memory["who"] + " "
        if "where" in memory:
            memory_text += memory["where"] + " "
        if "why" in memory:
            memory_text += memory["why"] + " "
        
        memory_text = memory_text.lower()
        
        for fragment in fragments:
            if fragment in memory_text:
                match_score += 1.0
            elif any(word in memory_text for word in fragment.split()):
                match_score += 0.7
        
        return match_score / total_fragments
    
    def _reconstruct_memory(self, fragment_matches: List[Tuple[Dict, float]], context: Dict) -> Dict:
        """Reconstruct a memory from fragment matches."""
        if not fragment_matches:
            return {}
        
        # Use the best matching memory as base
        best_memory, best_score = fragment_matches[0]
        
        # Create reconstructed memory
        reconstructed = {
            "type": "reconstructed",
            "original_memory": best_memory,
            "reconstruction_confidence": best_score,
            "fragments_used": len(fragment_matches)
        }
        
        # Copy relevant fields
        for field in ["what", "who", "when", "where", "why", "how", "emotions"]:
            if field in best_memory:
                reconstructed[field] = best_memory[field]
        
        return reconstructed
    
    def _calculate_relearning_score(self, memory: Dict) -> float:
        """Calculate how likely a memory needs relearning."""
        score = 0.0
        
        # Age factor
        if "created" in memory:
            try:
                created_time = datetime.fromisoformat(memory["created"])
                age_hours = (datetime.now() - created_time).total_seconds() / 3600
                if age_hours > 168:  # Older than a week
                    score += 0.4
                elif age_hours > 72:  # Older than 3 days
                    score += 0.2
            except:
                pass
        
        # Access frequency factor
        if "access_count" in memory:
            if memory["access_count"] < 2:
                score += 0.3
            elif memory["access_count"] < 5:
                score += 0.1
        
        # Confidence factor
        if "confidence" in memory:
            if memory["confidence"] < 0.7:
                score += 0.3
            elif memory["confidence"] < 0.9:
                score += 0.1
        
        return min(score, 1.0)
    
    def _update_cognitive_load(self):
        """Update cognitive load based on retrieval attempts."""
        # Cognitive load increases with frequent retrieval attempts
        if self.last_retrieval_time:
            time_since_last = (datetime.now() - self.last_retrieval_time).total_seconds()
            if time_since_last < 60:  # Within a minute
                self.cognitive_load = min(1.0, self.cognitive_load + 0.1)
            else:
                self.cognitive_load = max(0.0, self.cognitive_load - 0.05)
        else:
            self.cognitive_load = max(0.0, self.cognitive_load - 0.1)
    
    def get_retrieval_statistics(self) -> Dict:
        """Get statistics about memory retrieval performance."""
        return {
            "personality_type": self.personality_type,
            "retrieval_attempts": self.retrieval_attempts,
            "cognitive_load": self.cognitive_load,
            "last_retrieval_time": self.last_retrieval_time.isoformat() if self.last_retrieval_time else None,
            "retrieval_preferences": self.retrieval_preferences
        }
