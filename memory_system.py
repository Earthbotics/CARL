#!/usr/bin/env python3
"""
Comprehensive Memory System for CARL
This system coordinates all memory-related functionality including working memory,
long-term memory, episodic memory, and semantic memory.
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

@dataclass
class MemoryItem:
    """Represents a single memory item with metadata."""
    id: str
    content: str
    memory_type: str  # 'episodic', 'semantic', 'working', 'procedural'
    timestamp: str
    emotional_context: Dict[str, float]
    importance: float  # 0.0 to 1.0
    access_count: int
    last_accessed: str
    associations: List[str]  # Related memory IDs
    source: str  # 'conversation', 'experience', 'learning', 'imagination'
    confidence: float  # 0.0 to 1.0
    decay_rate: float  # How quickly this memory fades
    # 🔧 FIX: Add image fields for vision memories
    image_path: str = ""  # Path to associated image file
    image_filename: str = ""  # Filename of associated image

@dataclass
class MemoryContext:
    """Context for memory operations."""
    current_emotion: str
    emotional_intensity: float
    cognitive_load: float
    attention_focus: str
    environmental_context: Dict[str, Any]
    personality_state: Dict[str, Any]

class MemorySystem:
    """
    Comprehensive memory system that coordinates all memory-related functionality.
    """
    
    def __init__(self, personality_type: str = "INTP"):
        self.personality_type = personality_type
        self.logger = logging.getLogger(__name__)
        
        # Memory storage directories with standardized organization
        self.memory_dirs = {
            'episodic': 'memories/episodic',
            'semantic': 'memories/semantic',
            'working': 'memories/working',
            'procedural': 'memories/procedural',
            'imagined': 'memories/imagined',
            'vision': 'memories/vision',
            'self_recognition': 'memories/self_recognition',
            'relationships': 'memories/relationships',
            'first_interaction': 'memories/first_interaction'
        }
        
        # Ensure memory directories exist
        self._ensure_memory_directories()
        
        # Memory system parameters
        self.working_memory_capacity = 7  # Miller's Law: 7±2 items
        self.episodic_memory_capacity = 1000  # Maximum episodic memories
        self.semantic_memory_capacity = 5000  # Maximum semantic memories
        self.memory_consolidation_threshold = 0.3  # Minimum importance for long-term storage
        
        # Memory consolidation parameters
        self.consolidation_factors = {
            'emotional_intensity': 0.4,
            'repetition': 0.3,
            'novelty': 0.2,
            'relevance': 0.1
        }
        
        # Memory retrieval parameters
        self.retrieval_thresholds = {
            'recall': 0.7,
            'recognition': 0.5,
            'recollection': 0.6,
            'relearning': 0.3
        }
        
        # Initialize memory caches
        self.working_memory_cache = []
        self.episodic_memory_cache = {}
        self.semantic_memory_cache = {}
        self.procedural_memory_cache = {}
        
        # Memory statistics
        self.memory_stats = {
            'total_memories': 0,
            'working_memories': 0,
            'episodic_memories': 0,
            'semantic_memories': 0,
            'procedural_memories': 0,
            'retrieval_attempts': 0,
            'successful_retrievals': 0,
            'consolidation_events': 0
        }
        
        # 🔧 FIX: Add memory consistency tracking for STM/LTM updates and concept associations
        self.memory_consistency_enabled = True
        self.concept_associations = {}
        self.last_consistency_check = None
        
        # Load existing memories
        self._load_all_memories()
        
        # 🔧 FIX: Initialize memory consistency system
        self._ensure_memory_consistency()
    
    def _ensure_memory_directories(self):
        """Ensure all memory directories exist."""
        for dir_path in self.memory_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_all_memories(self):
        """Load all memories from storage."""
        try:
            # Load working memory
            working_memory_file = os.path.join(self.memory_dirs['working'], 'working_memory.json')
            if os.path.exists(working_memory_file):
                with open(working_memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.working_memory_cache = data.get('items', [])
                    self.memory_stats['working_memories'] = len(self.working_memory_cache)
            
            # Load episodic memories
            episodic_dir = self.memory_dirs['episodic']
            for filename in os.listdir(episodic_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(episodic_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                            memory_id = memory_data.get('id', filename[:-5])
                            self.episodic_memory_cache[memory_id] = memory_data
                    except Exception as e:
                        self.logger.warning(f"Error loading episodic memory {filename}: {e}")
            
            # Load semantic memories
            semantic_dir = self.memory_dirs['semantic']
            for filename in os.listdir(semantic_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(semantic_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                            memory_id = memory_data.get('id', filename[:-5])
                            self.semantic_memory_cache[memory_id] = memory_data
                    except Exception as e:
                        self.logger.warning(f"Error loading semantic memory {filename}: {e}")
            
            # Update statistics
            self.memory_stats['episodic_memories'] = len(self.episodic_memory_cache)
            self.memory_stats['semantic_memories'] = len(self.semantic_memory_cache)
            self.memory_stats['total_memories'] = (
                self.memory_stats['working_memories'] +
                self.memory_stats['episodic_memories'] +
                self.memory_stats['semantic_memories'] +
                self.memory_stats['procedural_memories']
            )
            
        except Exception as e:
            self.logger.error(f"Error loading memories: {e}")
    
    def store_memory(self, content: str, memory_type: str, context: MemoryContext,
                    importance: float = 0.5, source: str = "experience") -> str:
        """
        Store a new memory item.
        
        Args:
            content: The memory content
            memory_type: Type of memory ('episodic', 'semantic', 'working', 'procedural')
            context: Current memory context
            importance: Importance of the memory (0.0 to 1.0)
            source: Source of the memory
            
        Returns:
            Memory ID
        """
        try:
            # Generate memory ID using memory_id_system if available
            memory_id = self._generate_unique_memory_id(memory_type)
            
            # Create memory item
            # 🔧 FIX: Handle None context gracefully
            if context is None:
                context = MemoryContext(
                    current_emotion="neutral",
                    emotional_intensity=0.5,
                    cognitive_load=0.3,
                    attention_focus="general",
                    environmental_context={},
                    personality_state={}
                )
            
            memory_item = MemoryItem(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                timestamp=datetime.now().isoformat(),
                emotional_context={
                    context.current_emotion: context.emotional_intensity
                },
                importance=importance,
                access_count=0,
                last_accessed=datetime.now().isoformat(),
                associations=[],
                source=source,
                confidence=0.8,  # Initial confidence
                decay_rate=0.1  # Default decay rate
            )
            
            # Store based on memory type
            if memory_type == 'working':
                self._store_working_memory(memory_item)
            elif memory_type == 'episodic':
                self._store_episodic_memory(memory_item)
            elif memory_type == 'semantic':
                self._store_semantic_memory(memory_item)
            elif memory_type == 'procedural':
                self._store_procedural_memory(memory_item)
            
            # Update statistics
            self.memory_stats['total_memories'] += 1
            # Safely update memory type statistics
            memory_type_key = f'{memory_type}_memories'
            if memory_type_key in self.memory_stats:
                self.memory_stats[memory_type_key] += 1
            else:
                # Initialize the key if it doesn't exist
                self.memory_stats[memory_type_key] = 1
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            # Generate fallback ID instead of returning None
            return self._generate_fallback_memory_id(memory_type)
    
    def _generate_unique_memory_id(self, memory_type: str) -> str:
        """Generate a unique memory ID using memory_id_system if available."""
        try:
            # Try to use memory_id_system if available
            if hasattr(self, 'memory_id_system') and self.memory_id_system:
                return self.memory_id_system.generate_mid(memory_type)
            
            # Fallback to UUID-based ID instead of timestamp
            import uuid
            unique_id = str(uuid.uuid4())
            return f"{memory_type}_{unique_id}"
            
        except Exception as e:
            self.logger.error(f"Error generating unique memory ID: {e}")
            return self._generate_fallback_memory_id(memory_type)
    
    def _generate_fallback_memory_id(self, memory_type: str) -> str:
        """Generate a fallback memory ID when other methods fail."""
        try:
            import uuid
            # Generate a proper UUID instead of timestamp-based ID
            unique_id = str(uuid.uuid4())
            return f"{memory_type}_{unique_id}"
        except Exception as e:
            self.logger.error(f"Error generating fallback memory ID: {e}")
            # Last resort - use current time in seconds with UUID
            try:
                import uuid
                return f"{memory_type}_{uuid.uuid4()}"
            except:
                return f"{memory_type}_{int(datetime.now().timestamp())}_{random.randint(100, 999)}"
    
    def add_vision_memory(self, vision_data: Dict[str, Any]) -> str:
        """
        Add vision memory with image data and analysis.
        
        Args:
            vision_data: Dictionary containing vision information including:
                - filename: Image filename
                - filepath: Full path to image file
                - image_hash: Hash of image data
                - context: Additional context information
                - camera_active: Whether camera was active
                - timestamp: When the vision was captured
                - objects_detected: List of detected objects (REQUIRED for meaningful memory)
                
        Returns:
            Memory ID or None if memory should not be created (no actual data)
        """
        try:
            # 🔧 CRITICAL FIX: Only create memory if we have actual vision analysis data
            # Don't create empty memories before API returns
            objects_detected = vision_data.get('objects_detected', [])
            filepath = vision_data.get('filepath', '')
            image_path = vision_data.get('image_path', '')
            
            # Check if we have meaningful data to store
            has_objects = objects_detected and len(objects_detected) > 0
            has_image = bool(filepath or image_path)
            
            # If we have neither objects nor image path, this is likely a premature memory creation
            # Wait for the actual API response before creating memory
            if not has_objects and not has_image:
                self.logger.warning(f"⚠️ Skipping vision memory creation - no objects detected and no image path. This is likely a premature call before API returns.")
                return None
            
            # Generate memory ID
            memory_id = f"vision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Create vision memory content
            filename = vision_data.get('filename', '')
            if not filename:
                # Try to extract filename from filepath or image_path
                actual_path = filepath or image_path
                if actual_path:
                    filename = os.path.basename(actual_path)
                else:
                    # Use objects detected if available
                    if objects_detected:
                        filename = f"objects_{', '.join(objects_detected[:3])}"  # First 3 objects
                    else:
                        # If we have an image path but no objects, use a generic name
                        filename = "vision_capture"
            
            # 🔧 FIX #2: Create detailed descriptive content for CME entries
            objects_str = ', '.join(objects_detected[:3]) if objects_detected else 'No objects detected'
            
            # Use actual image path (check both filepath and image_path)
            actual_image_path = filepath or image_path or vision_data.get('filepath', '') or vision_data.get('image_path', '')
            
            content = f"""Vision capture: {filename}

PURPOSE: This entry represents CARL's vision system capturing and analyzing a visual scene from the camera. The system processes the image to detect objects, assess danger/pleasure, and extract semantic information (Who, What, When, Where, Why, How, Expectation).

ARCHITECTURE CONNECTION: This vision capture is part of CARL's Perception → Judgment → Needs → Goals → Actions → PDB → Memory cognitive pipeline:
- PERCEPTION: Visual scene captured and analyzed
- JUDGMENT: Objects detected and contextualized
- MEMORY: Stored as episodic memory for future recall and context building
- COGNITIVE PROCESSING: Visual information influences CARL's understanding of the environment

DETECTION DETAILS:
- Objects Detected: {objects_str}
- Camera Active: {vision_data.get('camera_active', False)}
- Image Path: {actual_image_path if actual_image_path else 'N/A'}
- Timestamp: {vision_data.get('timestamp', datetime.now().isoformat())}"""
            
            if vision_data.get('context', {}).get('source'):
                content += f"\n- Source: {vision_data['context']['source']}"
            
            content += "\n\nThis memory entry enables CARL to recall visual scenes and build contextual understanding of the environment over time."
            
            # Create memory context
            context = MemoryContext(
                current_emotion="neutral",
                emotional_intensity=0.5,
                cognitive_load=0.3,
                attention_focus="visual",
                environmental_context={
                    "camera_active": vision_data.get('camera_active', False),
                    "image_hash": vision_data.get('image_hash', ''),
                    "filepath": vision_data.get('filepath', '')
                },
                personality_state={}
            )
            
            # Store as episodic memory with vision type
            memory_item = MemoryItem(
                id=memory_id,
                content=content,
                memory_type='episodic',
                timestamp=vision_data.get('timestamp', datetime.now().isoformat()),
                emotional_context={'neutral': 0.5},
                importance=0.6,  # Vision memories are moderately important
                access_count=0,
                last_accessed=datetime.now().isoformat(),
                associations=[],
                source='vision',
                confidence=0.9,  # High confidence for visual memories
                decay_rate=0.05,  # Slower decay for visual memories
                # 🔧 FIX: Add image path directly to memory item for CME display
                image_path=actual_image_path,
                image_filename=filename
            )
            
            # Store in episodic memory
            self._store_episodic_memory(memory_item)
            
            # Save vision metadata
            vision_file = os.path.join(self.memory_dirs['vision'], f"{memory_id}_vision.json")
            with open(vision_file, 'w', encoding='utf-8') as f:
                json.dump(vision_data, f, indent=2, ensure_ascii=False)
            
            # Update statistics
            self.memory_stats['total_memories'] += 1
            self.memory_stats['episodic_memories'] += 1
            
            self.logger.info(f"Vision memory stored: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing vision memory: {e}")
            return None
    
    def _store_working_memory(self, memory_item: MemoryItem):
        """Store memory in working memory."""
        # Add to cache
        self.working_memory_cache.append(asdict(memory_item))
        
        # Maintain capacity limit
        if len(self.working_memory_cache) > self.working_memory_capacity:
            # Remove least important memory
            self.working_memory_cache.sort(key=lambda x: x['importance'], reverse=True)
            self.working_memory_cache = self.working_memory_cache[:self.working_memory_capacity]
        
        # Save to file
        self._save_working_memory()
    
    def _store_episodic_memory(self, memory_item: MemoryItem):
        """Store memory in episodic memory."""
        # Add to cache
        self.episodic_memory_cache[memory_item.id] = asdict(memory_item)
        
        # Save to file
        file_path = os.path.join(self.memory_dirs['episodic'], f"{memory_item.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(memory_item), f, indent=2, ensure_ascii=False)
    
    def _store_semantic_memory(self, memory_item: MemoryItem):
        """Store memory in semantic memory."""
        # Add to cache
        self.semantic_memory_cache[memory_item.id] = asdict(memory_item)
        
        # Save to file
        file_path = os.path.join(self.memory_dirs['semantic'], f"{memory_item.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(memory_item), f, indent=2, ensure_ascii=False)
    
    def _store_procedural_memory(self, memory_item: MemoryItem):
        """Store memory in procedural memory."""
        # Add to cache
        self.procedural_memory_cache[memory_item.id] = asdict(memory_item)
        
        # Save to file
        file_path = os.path.join(self.memory_dirs['procedural'], f"{memory_item.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(memory_item), f, indent=2, ensure_ascii=False)
    
    def retrieve_memory(self, query: str, context: MemoryContext, 
                       memory_types: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        Retrieve memories based on query and context.
        
        Args:
            query: Search query
            context: Current memory context
            memory_types: Types of memory to search (None for all)
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            self.memory_stats['retrieval_attempts'] += 1
            
            if memory_types is None:
                memory_types = ['working', 'episodic', 'semantic', 'procedural']
            
            results = []
            
            # Search working memory
            if 'working' in memory_types:
                working_results = self._search_working_memory(query, context)
                results.extend(working_results)
            
            # Search episodic memory
            if 'episodic' in memory_types:
                episodic_results = self._search_episodic_memory(query, context)
                results.extend(episodic_results)
            
            # Search semantic memory
            if 'semantic' in memory_types:
                semantic_results = self._search_semantic_memory(query, context)
                results.extend(semantic_results)
            
            # Search procedural memory
            if 'procedural' in memory_types:
                procedural_results = self._search_procedural_memory(query, context)
                results.extend(procedural_results)
            
            # Sort by relevance and recency
            results.sort(key=lambda x: self._calculate_relevance_score(x, context), reverse=True)
            
            # Limit results
            results = results[:limit]
            
            # Update access statistics
            for result in results:
                self._update_memory_access(result['id'], result['memory_type'])
            
            self.memory_stats['successful_retrievals'] += len(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving memory: {e}")
            return []
    
    def _search_working_memory(self, query: str, context: MemoryContext) -> List[Dict]:
        """Search working memory."""
        results = []
        query_lower = query.lower()
        
        for memory in self.working_memory_cache:
            if query_lower in memory['content'].lower():
                memory['memory_type'] = 'working'
                results.append(memory)
        
        return results
    
    def _search_episodic_memory(self, query: str, context: MemoryContext) -> List[Dict]:
        """Search episodic memory."""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory in self.episodic_memory_cache.items():
            if query_lower in memory['content'].lower():
                memory['memory_type'] = 'episodic'
                results.append(memory)
        
        return results
    
    def _search_semantic_memory(self, query: str, context: MemoryContext) -> List[Dict]:
        """Search semantic memory."""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory in self.semantic_memory_cache.items():
            if query_lower in memory['content'].lower():
                memory['memory_type'] = 'semantic'
                results.append(memory)
        
        return results
    
    def _search_procedural_memory(self, query: str, context: MemoryContext) -> List[Dict]:
        """Search procedural memory."""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory in self.procedural_memory_cache.items():
            if query_lower in memory['content'].lower():
                memory['memory_type'] = 'procedural'
                results.append(memory)
        
        return results

    def recall_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        Recall memories based on entity/place/time queries.
        
        Args:
            query: Search query (entity/place/time)
            
        Returns:
            List of memory hits with timestamp and summary
        """
        try:
            # Check for first meeting recall queries
            if self._is_first_meeting_query(query):
                return self._recall_first_meeting_memories(query)
            
            # First, check if this is a named entity query (concept, need, goal, skill, value)
            named_entity_result = self._search_named_entities(query)
            if named_entity_result:
                return [named_entity_result]
            
            # Create a basic context for retrieval
            context = MemoryContext(
                current_emotion="neutral",
                emotional_intensity=0.5,
                cognitive_load=0.3,
                attention_focus="memory_recall",
                environmental_context={},
                personality_state={}
            )
            
            # Retrieve memories using existing method
            memories = self.retrieve_memory(query, context, limit=20)
            
            # Format results with timestamp and summary
            formatted_results = []
            for memory in memories:
                # Generate summary
                summary = self._generate_memory_summary(memory)
                
                # Format timestamp
                timestamp = memory.get('timestamp', '')
                if timestamp:
                    try:
                        # Parse and format timestamp
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_timestamp = timestamp
                else:
                    formatted_timestamp = "Unknown"
                
                # Create formatted result
                formatted_result = {
                    'id': memory.get('id', ''),
                    'timestamp': formatted_timestamp,
                    'summary': summary,
                    'content': memory.get('content', ''),
                    'memory_type': memory.get('memory_type', ''),
                    'relevance_score': memory.get('relevance_score', 0.0),
                    'image_file': memory.get('image_file', None),
                    'concepts': memory.get('concepts', []),
                    'emotion': memory.get('emotional_context', {})
                }
                
                formatted_results.append(formatted_result)
            
            # Sort by relevance score (descending)
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            self.logger.info(f"Memory recall for '{query}': {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in memory recall: {e}")
            return []

    def _search_named_entities(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for named entities in concept files, needs, goals, skills, and values.
        This provides fallback recall when direct memory search fails.
        
        Args:
            query: The named entity to search for
            
        Returns:
            Dict containing named entity information and fallback context, or None if not found
        """
        try:
            query_lower = query.lower().strip()
            
            # Search in concepts directory
            concepts_dir = "concepts"
            if os.path.exists(concepts_dir):
                for filename in os.listdir(concepts_dir):
                    if filename.endswith('.json'):
                        concept_name = filename.replace('.json', '')
                        if query_lower in concept_name.lower():
                            concept_file = os.path.join(concepts_dir, filename)
                            try:
                                with open(concept_file, 'r', encoding='utf-8') as f:
                                    concept_data = json.load(f)
                                return self._create_named_entity_result(query, "concept", concept_data, concept_file)
                            except Exception as e:
                                self.logger.warning(f"Error reading concept file {filename}: {e}")
            
            # Search in things directory (for self-learned concepts like Chomp)
            things_dir = "things"
            if os.path.exists(things_dir):
                for filename in os.listdir(things_dir):
                    if filename.endswith('.json'):
                        thing_name = filename.replace('.json', '')
                        if query_lower in thing_name.lower():
                            thing_file = os.path.join(things_dir, filename)
                            try:
                                with open(thing_file, 'r', encoding='utf-8') as f:
                                    thing_data = json.load(f)
                                return self._create_named_entity_result(query, "thing", thing_data, thing_file)
                            except Exception as e:
                                self.logger.warning(f"Error reading thing file {filename}: {e}")
            
            # Search in needs directory
            needs_dir = "needs"
            if os.path.exists(needs_dir):
                for filename in os.listdir(needs_dir):
                    if filename.endswith('.json'):
                        need_name = filename.replace('.json', '')
                        if query_lower in need_name.lower():
                            need_file = os.path.join(needs_dir, filename)
                            try:
                                with open(need_file, 'r', encoding='utf-8') as f:
                                    need_data = json.load(f)
                                return self._create_named_entity_result(query, "need", need_data, need_file)
                            except Exception as e:
                                self.logger.warning(f"Error reading need file {filename}: {e}")
            
            # Search in goals directory
            goals_dir = "goals"
            if os.path.exists(goals_dir):
                for filename in os.listdir(goals_dir):
                    if filename.endswith('.json'):
                        goal_name = filename.replace('.json', '')
                        if query_lower in goal_name.lower():
                            goal_file = os.path.join(goals_dir, filename)
                            try:
                                with open(goal_file, 'r', encoding='utf-8') as f:
                                    goal_data = json.load(f)
                                return self._create_named_entity_result(query, "goal", goal_data, goal_file)
                            except Exception as e:
                                self.logger.warning(f"Error reading goal file {filename}: {e}")
            
            # Search in skills directory
            skills_dir = "skills"
            if os.path.exists(skills_dir):
                for filename in os.listdir(skills_dir):
                    if filename.endswith('.json'):
                        skill_name = filename.replace('.json', '')
                        if query_lower in skill_name.lower():
                            skill_file = os.path.join(skills_dir, filename)
                            try:
                                with open(skill_file, 'r', encoding='utf-8') as f:
                                    skill_data = json.load(f)
                                return self._create_named_entity_result(query, "skill", skill_data, skill_file)
                            except Exception as e:
                                self.logger.warning(f"Error reading skill file {filename}: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching named entities: {e}")
            return None

    def _create_named_entity_result(self, query: str, entity_type: str, entity_data: Dict, filepath: str) -> Dict[str, Any]:
        """
        Create a named entity recall result with fallback context information.
        
        Args:
            query: The original query
            entity_type: Type of entity (concept, need, goal, skill, thing)
            entity_data: The entity data from the file
            filepath: Path to the entity file
            
        Returns:
            Dict containing the named entity recall result
        """
        try:
            # Get the entity name
            entity_name = entity_data.get('name', entity_data.get('word', query))
            
            # Create basic result
            result = {
                'id': f"{entity_type}_{entity_name.lower().replace(' ', '_')}",
                'timestamp': entity_data.get('created_at', entity_data.get('last_updated', 'Unknown')),
                'summary': f"Named entity: {entity_name} ({entity_type})",
                'content': f"Found {entity_name} in {entity_type} system",
                'memory_type': 'named_entity',
                'relevance_score': 1.0,  # High relevance for direct matches
                'entity_type': entity_type,
                'entity_name': entity_name,
                'entity_data': entity_data,
                'filepath': filepath
            }
            
            # Add fallback context information
            fallback_context = self._get_fallback_context(query, entity_name)
            if fallback_context:
                result['fallback_context'] = fallback_context
                result['content'] += f" - {fallback_context['summary']}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating named entity result: {e}")
            return {
                'id': f"{entity_type}_{query.lower()}",
                'timestamp': 'Unknown',
                'summary': f"Named entity: {query} ({entity_type})",
                'content': f"Found {query} in {entity_type} system",
                'memory_type': 'named_entity',
                'relevance_score': 1.0,
                'entity_type': entity_type,
                'entity_name': query,
                'entity_data': entity_data,
                'filepath': filepath
            }

    def _get_fallback_context(self, query: str, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Get fallback context information for a named entity, including visual and spatial context.
        
        Args:
            query: The original query
            entity_name: The name of the entity
            
        Returns:
            Dict containing fallback context information, or None if not available
        """
        try:
            # Search for vision memories related to this entity
            vision_memories = self._search_vision_memories_for_entity(entity_name)
            
            if vision_memories:
                # Get the most recent vision memory
                latest_vision = max(vision_memories, key=lambda x: x.get('timestamp', ''))
                
                # Extract visual and spatial context
                visual_context = self._extract_visual_context(latest_vision)
                spatial_context = self._extract_spatial_context(latest_vision)
                
                return {
                    'summary': f"Last seen: {visual_context}",
                    'visual_context': visual_context,
                    'spatial_context': spatial_context,
                    'last_sighting': latest_vision.get('timestamp', 'Unknown'),
                    'vision_memories_count': len(vision_memories)
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting fallback context: {e}")
            return None

    def _search_vision_memories_for_entity(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Search for vision memories related to a specific entity.
        
        Args:
            entity_name: Name of the entity to search for
            
        Returns:
            List of vision memories related to the entity
        """
        try:
            vision_memories = []
            memories_dir = "memories"
            
            if os.path.exists(memories_dir):
                # Search through all memory files
                for filename in os.listdir(memories_dir):
                    if filename.endswith('.json'):
                        memory_file = os.path.join(memories_dir, filename)
                        try:
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            # Check if this memory contains vision data related to the entity
                            if self._memory_contains_entity_vision(memory_data, entity_name):
                                vision_memories.append(memory_data)
                                
                        except Exception as e:
                            continue  # Skip files that can't be read
            
            return vision_memories
            
        except Exception as e:
            self.logger.error(f"Error searching vision memories: {e}")
            return []

    def _memory_contains_entity_vision(self, memory_data: Dict[str, Any], entity_name: str) -> bool:
        """
        Check if a memory contains vision data related to a specific entity.
        
        Args:
            memory_data: The memory data to check
            entity_name: Name of the entity to look for
            
        Returns:
            True if the memory contains vision data related to the entity
        """
        try:
            entity_name_lower = entity_name.lower()
            
            # Check vision_memory section
            vision_memory = memory_data.get('vision_memory', {})
            if vision_memory:
                detected_objects = vision_memory.get('detected_objects', [])
                if any(entity_name_lower in obj.lower() for obj in detected_objects):
                    return True
            
            # Check vision_analysis section
            vision_analysis = memory_data.get('vision_analysis', {})
            if vision_analysis:
                objects_detected = vision_analysis.get('objects_detected', [])
                if any(entity_name_lower in obj.lower() for obj in objects_detected):
                    return True
            
            # Check WHAT field for vision references
            what_field = memory_data.get('WHAT', '')
            if 'vision' in what_field.lower() and entity_name_lower in what_field.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking memory for entity vision: {e}")
            return False

    def _extract_visual_context(self, vision_memory: Dict[str, Any]) -> str:
        """
        Extract visual context from a vision memory.
        
        Args:
            vision_memory: The vision memory data
            
        Returns:
            String describing the visual context
        """
        try:
            # Check vision_memory section
            vision_data = vision_memory.get('vision_memory', {})
            if vision_data:
                detected_objects = vision_data.get('detected_objects', [])
                if detected_objects:
                    return f"Detected objects: {', '.join(detected_objects)}"
            
            # Check vision_analysis section
            vision_analysis = vision_memory.get('vision_analysis', {})
            if vision_analysis:
                objects_detected = vision_analysis.get('objects_detected', [])
                if objects_detected:
                    return f"Objects detected: {', '.join(objects_detected)}"
            
            return "Visual context not available"
            
        except Exception as e:
            self.logger.error(f"Error extracting visual context: {e}")
            return "Visual context not available"

    def _extract_spatial_context(self, vision_memory: Dict[str, Any]) -> str:
        """
        Extract spatial context from a vision memory.
        
        Args:
            vision_memory: The vision memory data
            
        Returns:
            String describing the spatial context
        """
        try:
            # Check WHERE field
            where_field = vision_memory.get('WHERE', '')
            if where_field:
                return f"Location: {where_field}"
            
            # Check vision_analysis analysis section
            vision_analysis = vision_memory.get('vision_analysis', {})
            if vision_analysis:
                analysis = vision_analysis.get('analysis', {})
                where_context = analysis.get('where', '')
                if where_context:
                    return f"Context: {where_context}"
            
            return "Spatial context not available"
            
        except Exception as e:
            self.logger.error(f"Error extracting spatial context: {e}")
            return "Spatial context not available"

    def _generate_memory_summary(self, memory: Dict[str, Any]) -> str:
        """Generate a short summary of a memory."""
        content = memory.get('content', '')
        memory_type = memory.get('memory_type', '')
        
        # Generate summary based on memory type
        if memory_type == 'vision':
            # Extract object/concept from vision memory
            if 'saw' in content.lower() or 'detected' in content.lower():
                # Extract the object name
                words = content.split()
                for i, word in enumerate(words):
                    if word.lower() in ['saw', 'detected', 'spotted']:
                        if i + 1 < len(words):
                            object_name = words[i + 1]
                            return f"Saw {object_name}"
                return f"Vision event: {content[:50]}"
            else:
                return f"Vision: {content[:50]}"
        
        elif memory_type == 'episodic':
            # Extract key information from episodic memory
            if len(content) > 50:
                return f"{content[:47]}..."
            else:
                return content
        
        elif memory_type == 'conversation':
            # Extract key information from conversation
            if 'said' in content.lower() or 'asked' in content.lower():
                return f"Conversation: {content[:50]}"
            else:
                return f"Talk: {content[:50]}"
        
        else:
            # Generic summary
            if len(content) > 50:
                return f"{content[:47]}..."
            else:
                return content

    def _calculate_relevance_score(self, memory: Dict, context: MemoryContext) -> float:
        """Calculate relevance score for memory retrieval."""
        score = 0.0
        
        # Base importance
        score += memory.get('importance', 0.5) * 0.3
        
        # Recency factor
        last_accessed = datetime.fromisoformat(memory.get('last_accessed', datetime.now().isoformat()))
        days_ago = (datetime.now() - last_accessed).days
        recency_factor = max(0.1, 1.0 - (days_ago / 365.0))  # Decay over a year
        score += recency_factor * 0.2
        
        # Access frequency
        access_count = memory.get('access_count', 0)
        frequency_factor = min(1.0, access_count / 10.0)  # Normalize to 0-1
        score += frequency_factor * 0.2
        
        # Emotional relevance
        memory_emotion = list(memory.get('emotional_context', {}).keys())[0] if memory.get('emotional_context') else None
        if memory_emotion == context.current_emotion:
            score += 0.3
        
        return score
    
    def _update_memory_access(self, memory_id: str, memory_type: str):
        """Update memory access statistics."""
        try:
            if memory_type == 'working':
                for memory in self.working_memory_cache:
                    if memory['id'] == memory_id:
                        memory['access_count'] += 1
                        memory['last_accessed'] = datetime.now().isoformat()
                        break
            elif memory_type == 'episodic':
                if memory_id in self.episodic_memory_cache:
                    self.episodic_memory_cache[memory_id]['access_count'] += 1
                    self.episodic_memory_cache[memory_id]['last_accessed'] = datetime.now().isoformat()
            elif memory_type == 'semantic':
                if memory_id in self.semantic_memory_cache:
                    self.semantic_memory_cache[memory_id]['access_count'] += 1
                    self.semantic_memory_cache[memory_id]['last_accessed'] = datetime.now().isoformat()
            elif memory_type == 'procedural':
                if memory_id in self.procedural_memory_cache:
                    self.procedural_memory_cache[memory_id]['access_count'] += 1
                    self.procedural_memory_cache[memory_id]['last_accessed'] = datetime.now().isoformat()
        except Exception as e:
            self.logger.warning(f"Error updating memory access: {e}")
    
    def consolidate_memories(self, context: MemoryContext):
        """Consolidate working memories to long-term storage."""
        try:
            memories_to_consolidate = []
            
            for memory in self.working_memory_cache:
                consolidation_score = self._calculate_consolidation_score(memory, context)
                if consolidation_score >= self.memory_consolidation_threshold:
                    memories_to_consolidate.append((memory, consolidation_score))
            
            # Sort by consolidation score
            memories_to_consolidate.sort(key=lambda x: x[1], reverse=True)
            
            for memory, score in memories_to_consolidate:
                # Determine target memory type based on content
                if self._is_episodic_memory(memory):
                    target_type = 'episodic'
                elif self._is_semantic_memory(memory):
                    target_type = 'semantic'
                else:
                    target_type = 'episodic'  # Default
                
                # Create new memory item for long-term storage
                memory_item = MemoryItem(
                    id=memory['id'],
                    content=memory['content'],
                    memory_type=target_type,
                    timestamp=memory['timestamp'],
                    emotional_context=memory['emotional_context'],
                    importance=memory['importance'],
                    access_count=memory['access_count'],
                    last_accessed=memory['last_accessed'],
                    associations=memory['associations'],
                    source=memory['source'],
                    confidence=memory['confidence'],
                    decay_rate=memory['decay_rate']
                )
                
                # Store in long-term memory
                if target_type == 'episodic':
                    self._store_episodic_memory(memory_item)
                elif target_type == 'semantic':
                    self._store_semantic_memory(memory_item)
                
                # Remove from working memory
                self.working_memory_cache = [m for m in self.working_memory_cache if m['id'] != memory['id']]
                
                self.memory_stats['consolidation_events'] += 1
            
            # Update statistics
            self.memory_stats['working_memories'] = len(self.working_memory_cache)
            self.memory_stats['total_memories'] = (
                self.memory_stats['working_memories'] +
                self.memory_stats['episodic_memories'] +
                self.memory_stats['semantic_memories'] +
                self.memory_stats['procedural_memories']
            )
            
        except Exception as e:
            self.logger.error(f"Error consolidating memories: {e}")
    
    def _calculate_consolidation_score(self, memory: Dict, context: MemoryContext) -> float:
        """Calculate consolidation score for a memory."""
        score = 0.0
        
        # Emotional intensity
        emotional_intensity = max(memory.get('emotional_context', {}).values(), default=0.0)
        score += emotional_intensity * self.consolidation_factors['emotional_intensity']
        
        # Repetition (access count)
        access_count = memory.get('access_count', 0)
        repetition_factor = min(1.0, access_count / 5.0)  # Normalize to 0-1
        score += repetition_factor * self.consolidation_factors['repetition']
        
        # Novelty (inverse of access count for new memories)
        if access_count <= 1:
            score += self.consolidation_factors['novelty']
        
        # Relevance (importance)
        importance = memory.get('importance', 0.5)
        score += importance * self.consolidation_factors['relevance']
        
        return score
    
    def _is_episodic_memory(self, memory: Dict) -> bool:
        """Determine if memory is episodic (event-based)."""
        content = memory.get('content', '').lower()
        episodic_indicators = ['when', 'where', 'who', 'what happened', 'event', 'experience']
        return any(indicator in content for indicator in episodic_indicators)
    
    def _is_semantic_memory(self, memory: Dict) -> bool:
        """Determine if memory is semantic (fact-based)."""
        content = memory.get('content', '').lower()
        semantic_indicators = ['is', 'are', 'means', 'definition', 'fact', 'knowledge', 'concept']
        return any(indicator in content for indicator in semantic_indicators)
    
    def _save_working_memory(self):
        """Save working memory to file."""
        try:
            working_memory_file = os.path.join(self.memory_dirs['working'], 'working_memory.json')
            data = {
                'items': self.working_memory_cache,
                'last_updated': datetime.now().isoformat(),
                'total_items': len(self.working_memory_cache)
            }
            with open(working_memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving working memory: {e}")
    
    def get_memory_statistics(self) -> Dict:
        """Get memory system statistics."""
        return self.memory_stats.copy()
    
    def cleanup_old_memories(self, days_threshold: int = 365):
        """Clean up old memories that are no longer relevant."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            # Clean working memory
            self.working_memory_cache = [
                memory for memory in self.working_memory_cache
                if datetime.fromisoformat(memory['last_accessed']) > cutoff_date
            ]
            
            # Clean episodic memory
            memories_to_remove = []
            for memory_id, memory in self.episodic_memory_cache.items():
                if datetime.fromisoformat(memory['last_accessed']) <= cutoff_date:
                    memories_to_remove.append(memory_id)
            
            for memory_id in memories_to_remove:
                del self.episodic_memory_cache[memory_id]
                # Remove file
                file_path = os.path.join(self.memory_dirs['episodic'], f"{memory_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Update statistics
            self.memory_stats['working_memories'] = len(self.working_memory_cache)
            self.memory_stats['episodic_memories'] = len(self.episodic_memory_cache)
            self.memory_stats['total_memories'] = (
                self.memory_stats['working_memories'] +
                self.memory_stats['episodic_memories'] +
                self.memory_stats['semantic_memories'] +
                self.memory_stats['procedural_memories']
            )
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old memories: {e}")

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID."""
        try:
            # Search in all memory types
            memory_types = ['working', 'episodic', 'semantic', 'procedural']
            
            for memory_type in memory_types:
                if memory_type == 'working':
                    for memory in self.working_memory_cache:
                        if memory.get('id') == memory_id:
                            return memory
                else:
                    cache_name = f"{memory_type}_memory_cache"
                    if hasattr(self, cache_name):
                        cache = getattr(self, cache_name)
                        if memory_id in cache:
                            return cache[memory_id]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting memory by ID: {e}")
            return None

    def store_short_term_memory(self, event_data: Dict[str, Any]) -> str:
        """
        Store an event in short-term memory (working memory).
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            Memory ID
        """
        try:
            # Create memory context for short-term memory
            context = MemoryContext(
                current_emotion="neutral",
                emotional_intensity=0.5,
                attention_level=0.7,
                cognitive_load=0.5
            )
            
            # Extract content from event data
            content = event_data.get('content', '')
            if not content and 'type' in event_data:
                content = f"{event_data['type']} event"
            elif not content and 'WHAT' in event_data:
                content = event_data['WHAT']
            elif not content:
                content = str(event_data)
            
            # Store as working memory (short-term)
            return self.store_memory(
                content=content,
                memory_type="working",
                context=context,
                importance=0.6,  # Short-term memories are moderately important
                source="short_term_storage"
            )
            
        except Exception as e:
            self.logger.error(f"Error storing short-term memory: {e}")
            return ""

    def store_event(self, event_data: Dict[str, Any], memory_type: str = "working") -> str:
        """
        Store an event as a memory item.
        
        Args:
            event_data: Dictionary containing event information
            memory_type: Type of memory to store in ('working', 'episodic', 'semantic', 'procedural')
            
        Returns:
            Memory ID
        """
        try:
            # Extract content from event data
            content = event_data.get('content', '')
            if not content and 'type' in event_data:
                content = f"{event_data['type']} event"
            
            # Create memory context
            context = MemoryContext(
                current_emotion=event_data.get('emotional_context', {}).get('primary', 'neutral'),
                emotional_intensity=event_data.get('emotional_context', {}).get('intensity', 0.5),
                cognitive_load=0.3,
                attention_focus="internal" if event_data.get('type') == 'internal_thought' else "external",
                environmental_context=event_data.get('cognitive_state', {}),
                personality_state=event_data.get('cognitive_state', {}).get('personality_type', self.personality_type)
            )
            
            # Calculate importance based on priority and emotional intensity
            importance = event_data.get('priority', 0.5)
            emotional_intensity = event_data.get('emotional_context', {}).get('intensity', 0.5)
            importance = max(importance, emotional_intensity * 0.7)
            
            # Store using existing store_memory method
            memory_id = self.store_memory(
                content=content,
                memory_type=memory_type,
                context=context,
                importance=importance,
                source=event_data.get('type', 'event')
            )

            # Ensure memory_id is never 'unknown' - CRITICAL FIX
            if not memory_id or memory_id == 'unknown' or memory_id == 'None':
                memory_id = self._generate_guaranteed_memory_id(event_data)
                self.logger.info(f"🔧 Generated guaranteed memory ID: {memory_id}")
                
                # Check for first interaction events and add special tagging
                if self._is_first_interaction_event(event_data):
                    self._tag_first_interaction_event(event_data, memory_id)
                
                # Add additional event-specific data to the memory item
                if memory_id:
                    memory_item = self.get_memory_by_id(memory_id)
                    if memory_item:
                        # Add event-specific fields
                        memory_item.update({
                            'event_type': event_data.get('type', 'unknown'),
                            'thread_id': event_data.get('thread_id', ''),
                            'tags': event_data.get('tags', []),
                            'associations': event_data.get('associations', {}),
                            'original_event_data': event_data
                        })
                        
                        # Save updated memory item
                        if memory_type == 'working':
                            self._save_working_memory()
                        else:
                            # Save to file for other memory types
                            file_path = os.path.join(self.memory_dirs[memory_type], f"{memory_id}.json")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(memory_item, f, indent=2, ensure_ascii=False)
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing event: {e}")
            return None
    
    def _is_first_interaction_event(self, event_data: Dict[str, Any]) -> bool:
        """Check if this is a first interaction event with a new person."""
        try:
            # Check for introduction patterns in the WHAT field
            what_field = event_data.get('WHAT', '').lower()
            introduction_patterns = [
                'my name is', 'i am', 'i\'m', 'call me', 'hi i\'m', 'hello i\'m',
                'this is', 'meet', 'introduce', 'first time', 'new here'
            ]
            
            # Check if any introduction pattern is present
            for pattern in introduction_patterns:
                if pattern in what_field:
                    return True
            
            # Check for first meeting indicators in cognitive state
            cognitive_state = event_data.get('cognitive_state', {})
            if cognitive_state.get('first_meeting', False):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking first interaction event: {e}")
            return False
    
    def _tag_first_interaction_event(self, event_data: Dict[str, Any], memory_id: str):
        """Tag a first interaction event with timestamp and speaker identity."""
        try:
            # Extract speaker identity
            speaker_identity = self._extract_speaker_identity(event_data)
            
            # Create first interaction event data
            first_interaction_data = {
                'event_type': 'first_interaction_event',
                'memory_id': memory_id,
                'uuid': self._generate_uuid(),
                'timestamp': event_data.get('timestamp', datetime.now().isoformat()),
                'speaker_identity': speaker_identity,
                'introduction_context': event_data.get('WHAT', ''),
                'relationship_type': 'new_acquaintance',
                'scene_image_path': event_data.get('image_path', ''),
                'concept_references': self._extract_concept_references(event_data),
                'skill_references': self._extract_skill_references(event_data),
                'follow_up_questions': [
                    "What should I call you?",
                    "Have we met before?",
                    "What brings you here today?"
                ],
                'memory_tags': ['first_interaction', 'introduction', 'relationship_start'],
                'summary_format': self._generate_summary_format(event_data, speaker_identity)
            }
            
            # Store first interaction event in a dedicated file
            first_interaction_filename = f"first_interaction_{speaker_identity}_{int(time.time())}.json"
            first_interaction_path = os.path.join(self.memory_dirs['episodic'], first_interaction_filename)
            
            # Ensure episodic directory exists
            os.makedirs(self.memory_dirs['episodic'], exist_ok=True)
            
            with open(first_interaction_path, 'w', encoding='utf-8') as f:
                json.dump(first_interaction_data, f, indent=2)
            
            self.logger.info(f"🏷️ Tagged first interaction event: {speaker_identity} (Memory ID: {memory_id})")
            
        except Exception as e:
            self.logger.error(f"Error tagging first interaction event: {e}")
    
    def _extract_speaker_identity(self, event_data: Dict[str, Any]) -> str:
        """Extract speaker identity from event data."""
        try:
            # Try to extract name from WHAT field
            what_field = event_data.get('WHAT', '')
            
            # Look for name patterns
            import re
            name_patterns = [
                r"my name is (\w+)",
                r"i am (\w+)",
                r"i'm (\w+)",
                r"call me (\w+)",
                r"hi i'm (\w+)",
                r"hello i'm (\w+)"
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, what_field.lower())
                if match:
                    return match.group(1).capitalize()
            
            # Fallback to generic identifier
            return "Unknown_Person"
            
        except Exception as e:
            self.logger.error(f"Error extracting speaker identity: {e}")
            return "Unknown_Person"
    
    def _generate_uuid(self) -> str:
        """Generate a unique UUID for memory entries."""
        try:
            import uuid
            return str(uuid.uuid4())
        except Exception as e:
            self.logger.error(f"Error generating UUID: {e}")
            return f"uuid_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _extract_concept_references(self, event_data: Dict[str, Any]) -> List[str]:
        """Extract concept references from event data."""
        try:
            concepts = []
            
            # Extract from WHAT field
            what_field = event_data.get('WHAT', '')
            if what_field:
                # Look for concept patterns
                import re
                concept_patterns = [
                    r'\b(?:cat|dog|toy|book|car|house|tree|person|friend|family)\b',
                    r'\b(?:happy|sad|angry|excited|tired|hungry|thirsty)\b',
                    r'\b(?:walk|run|jump|sit|stand|eat|drink|sleep)\b'
                ]
                
                for pattern in concept_patterns:
                    matches = re.findall(pattern, what_field.lower())
                    concepts.extend(matches)
            
            # Extract from cognitive state
            cognitive_state = event_data.get('cognitive_state', {})
            if cognitive_state:
                # Look for concept mentions in cognitive processing
                concepts.extend(cognitive_state.get('concepts_mentioned', []))
            
            return list(set(concepts))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error extracting concept references: {e}")
            return []
    
    def _extract_skill_references(self, event_data: Dict[str, Any]) -> List[str]:
        """Extract skill references from event data."""
        try:
            skills = []
            
            # Extract from WHAT field
            what_field = event_data.get('WHAT', '')
            if what_field:
                # Look for skill patterns
                import re
                skill_patterns = [
                    r'\b(?:dance|wave|bow|sit|stand|walk|run|jump|turn|look)\b',
                    r'\b(?:reaction_\w+)\b'
                ]
                
                for pattern in skill_patterns:
                    matches = re.findall(pattern, what_field.lower())
                    skills.extend(matches)
            
            # Extract from cognitive state
            cognitive_state = event_data.get('cognitive_state', {})
            if cognitive_state:
                # Look for skill mentions in cognitive processing
                skills.extend(cognitive_state.get('skills_mentioned', []))
            
            return list(set(skills))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error extracting skill references: {e}")
            return []
    
    def _generate_summary_format(self, event_data: Dict[str, Any], speaker_identity: str) -> str:
        """Generate summary format: [Time, Location, People, Object, Event]."""
        try:
            timestamp = event_data.get('timestamp', datetime.now().isoformat())
            location = event_data.get('location', 'Unknown')
            people = [speaker_identity] if speaker_identity != "Unknown_Person" else []
            objects = self._extract_concept_references(event_data)
            event_desc = event_data.get('WHAT', 'First interaction')
            
            # Format: [Time, Location, People, Object, Event]
            summary = f"[{timestamp}, {location}, {', '.join(people)}, {', '.join(objects[:3])}, {event_desc}]"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary format: {e}")
            return f"[{datetime.now().isoformat()}, Unknown, {speaker_identity}, , First interaction]"
    
    def _generate_guaranteed_memory_id(self, event_data: Dict[str, Any]) -> str:
        """Generate a guaranteed unique memory ID that is never 'unknown'."""
        try:
            import time
            import random
            import uuid
            
            # Get event type and timestamp
            event_type = event_data.get('type', 'event')
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            uuid_component = str(uuid.uuid4())[:8]
            
            # Extract content for ID generation
            content = event_data.get('content', event_data.get('WHAT', ''))
            content_hash = hash(content) % 10000 if content else random_suffix
            
            # 🔧 ENHANCEMENT: Generate guaranteed unique ID with multiple uniqueness factors
            memory_id = f"mem_{event_type}_{timestamp}_{content_hash}_{uuid_component}_{random_suffix}"
            
            # 🔧 ENHANCEMENT: Ensure ID is never "unknown" or "unknown_id"
            if memory_id.lower() in ['unknown', 'unknown_id', 'unknown_memory']:
                memory_id = f"mem_{event_type}_{timestamp}_{uuid_component}_{random_suffix}_safe"
            
            self.logger.info(f"🆔 Generated guaranteed memory ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error generating guaranteed memory ID: {e}")
            # 🔧 ENHANCEMENT: Fallback with multiple uniqueness factors
            import uuid
            fallback_id = f"mem_guaranteed_{int(time.time())}_{str(uuid.uuid4())[:8]}_{random.randint(10000, 99999)}"
            self.logger.info(f"🆔 Generated fallback memory ID: {fallback_id}")
            return fallback_id
    
    def _is_first_meeting_query(self, query: str) -> bool:
        """Check if the query is asking about first meeting memories."""
        try:
            query_lower = query.lower()
            first_meeting_patterns = [
                'when did we first meet',
                'when did you and i first meet',
                'when was our first meeting',
                'do you recall what time and day you and i first met',
                'first time we met',
                'when we first met',
                'our first meeting',
                'first meeting',
                'when did we meet',
                'when did you meet me',
                'when did i meet you',
                'first time we talked',
                'when did we start talking',
                'when did we begin',
                'our first conversation'
            ]
            
            return any(pattern in query_lower for pattern in first_meeting_patterns)
            
        except Exception as e:
            self.logger.error(f"Error checking first meeting query: {e}")
            return False
    
    def _recall_first_meeting_memories(self, query: str) -> List[Dict[str, Any]]:
        """Recall first meeting memories for the user."""
        try:
            # Search for first meeting events in memories
            first_meeting_memories = []
            
            # Search in memories directory for first meeting events
            memories_dir = "memories"
            if os.path.exists(memories_dir):
                for filename in os.listdir(memories_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(memories_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            # Check if this is a first meeting event
                            if self._is_first_meeting_memory(memory_data):
                                first_meeting_memories.append({
                                    'memory_id': memory_data.get('id', filename),
                                    'timestamp': memory_data.get('timestamp', 'Unknown'),
                                    'summary': memory_data.get('WHAT', memory_data.get('summary', 'First meeting event')),
                                    'type': 'first_meeting',
                                    'filepath': filepath,
                                    'speaker_identity': memory_data.get('speaker_identity', 'Unknown'),
                                    'introduction_context': memory_data.get('introduction_context', ''),
                                    'relationship_type': memory_data.get('relationship_type', 'new_acquaintance')
                                })
                        except Exception as e:
                            self.logger.error(f"Error reading memory file {filename}: {e}")
                            continue
            
            # Also search for first interaction events
            first_interaction_memories = self._search_first_interaction_events()
            first_meeting_memories.extend(first_interaction_memories)
            
            # Search for early conversation events (introduction patterns)
            early_conversation_memories = self._search_early_conversation_events()
            first_meeting_memories.extend(early_conversation_memories)
            
            # Sort by timestamp (oldest first)
            first_meeting_memories.sort(key=lambda x: x.get('timestamp', ''))
            
            if first_meeting_memories:
                self.logger.info(f"Found {len(first_meeting_memories)} first meeting memories")
                return first_meeting_memories
            else:
                # Return a helpful message if no first meeting memories found
                return [{
                    'memory_id': 'no_first_meeting_found',
                    'timestamp': 'Unknown',
                    'summary': 'No first meeting memories found. This might be our first interaction!',
                    'type': 'no_memory',
                    'filepath': '',
                    'speaker_identity': 'Unknown',
                    'introduction_context': '',
                    'relationship_type': 'unknown'
                }]
                
        except Exception as e:
            self.logger.error(f"Error recalling first meeting memories: {e}")
            return [{
                'memory_id': 'error',
                'timestamp': 'Unknown',
                'summary': f'Error recalling first meeting memories: {str(e)}',
                'type': 'error',
                'filepath': '',
                'speaker_identity': 'Unknown',
                'introduction_context': '',
                'relationship_type': 'unknown'
            }]
    
    def _is_first_meeting_memory(self, memory_data: Dict) -> bool:
        """Check if a memory is a first meeting event."""
        try:
            # Check for first meeting indicators
            memory_type = memory_data.get('type', '').lower()
            what_field = memory_data.get('WHAT', '').lower()
            summary = memory_data.get('summary', '').lower()
            
            first_meeting_indicators = [
                'first_meeting',
                'first_interaction',
                'first time',
                'introduction',
                'meeting for the first time',
                'new acquaintance'
            ]
            
            # Check type field
            if any(indicator in memory_type for indicator in first_meeting_indicators):
                return True
            
            # Check WHAT field
            if any(indicator in what_field for indicator in first_meeting_indicators):
                return True
            
            # Check summary field
            if any(indicator in summary for indicator in first_meeting_indicators):
                return True
            
            # Check for introduction patterns
            introduction_patterns = [
                'my name is',
                'i am',
                'i\'m',
                'call me',
                'hi i\'m',
                'hello i\'m'
            ]
            
            if any(pattern in what_field for pattern in introduction_patterns):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking first meeting memory: {e}")
            return False
    
    def _search_first_interaction_events(self) -> List[Dict[str, Any]]:
        """Search for first interaction events in the system."""
        try:
            first_interaction_memories = []
            
            # Search in memories directory for first interaction events
            memories_dir = "memories"
            if os.path.exists(memories_dir):
                for filename in os.listdir(memories_dir):
                    if 'first_interaction' in filename.lower():
                        filepath = os.path.join(memories_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            first_interaction_memories.append({
                                'memory_id': memory_data.get('id', filename),
                                'timestamp': memory_data.get('timestamp', 'Unknown'),
                                'summary': memory_data.get('WHAT', memory_data.get('summary', 'First interaction event')),
                                'type': 'first_interaction',
                                'filepath': filepath,
                                'speaker_identity': memory_data.get('speaker_identity', 'Unknown'),
                                'introduction_context': memory_data.get('introduction_context', ''),
                                'relationship_type': memory_data.get('relationship_type', 'new_acquaintance')
                            })
                        except Exception as e:
                            self.logger.error(f"Error reading first interaction file {filename}: {e}")
                            continue
            
            return first_interaction_memories
            
        except Exception as e:
            self.logger.error(f"Error searching first interaction events: {e}")
            return []
    
    def _search_early_conversation_events(self) -> List[Dict[str, Any]]:
        """Search for early conversation events that might indicate first meetings."""
        try:
            early_conversation_memories = []
            
            # Search in memories directory for early conversation events
            memories_dir = "memories"
            if os.path.exists(memories_dir):
                for filename in os.listdir(memories_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(memories_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            # Check if this is an early conversation event
                            if self._is_early_conversation_memory(memory_data):
                                early_conversation_memories.append({
                                    'memory_id': memory_data.get('id', filename),
                                    'timestamp': memory_data.get('timestamp', 'Unknown'),
                                    'summary': memory_data.get('WHAT', memory_data.get('summary', 'Early conversation event')),
                                    'type': 'early_conversation',
                                    'filepath': filepath,
                                    'speaker_identity': memory_data.get('speaker_identity', 'Unknown'),
                                    'introduction_context': memory_data.get('introduction_context', ''),
                                    'relationship_type': memory_data.get('relationship_type', 'new_acquaintance')
                                })
                        except Exception as e:
                            self.logger.error(f"Error reading early conversation file {filename}: {e}")
                            continue
            
            return early_conversation_memories
            
        except Exception as e:
            self.logger.error(f"Error searching early conversation events: {e}")
            return []
    
    def _is_early_conversation_memory(self, memory_data: Dict) -> bool:
        """Check if a memory is an early conversation event."""
        try:
            # Check for early conversation indicators
            memory_type = memory_data.get('type', '').lower()
            what_field = memory_data.get('WHAT', '').lower()
            summary = memory_data.get('summary', '').lower()
            
            early_conversation_indicators = [
                'hi carl',
                'hello carl',
                'hi i am',
                'hello i am',
                'my name is',
                'i am joe',
                'i\'m joe',
                'call me',
                'nice to meet you',
                'pleased to meet you',
                'good to meet you',
                'introducing myself',
                'first time',
                'new here',
                'just started'
            ]
            
            # Check WHAT field for early conversation patterns
            if any(indicator in what_field for indicator in early_conversation_indicators):
                return True
            
            # Check summary field for early conversation patterns
            if any(indicator in summary for indicator in early_conversation_indicators):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking early conversation memory: {e}")
            return False

    def get_recent_memories(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get memories from the last N hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            all_memories = []
            
            # Collect memories from all types
            memory_types = ['working', 'episodic', 'semantic', 'procedural']
            
            for memory_type in memory_types:
                if memory_type == 'working':
                    all_memories.extend(self.working_memory_cache)
                else:
                    cache_name = f"{memory_type}_memory_cache"
                    if hasattr(self, cache_name):
                        cache = getattr(self, cache_name)
                        all_memories.extend(cache.values())
            
            # Filter by timestamp
            recent_memories = []
            for memory in all_memories:
                timestamp = memory.get('timestamp', '')
                if timestamp:
                    try:
                        memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if memory_time >= cutoff_time:
                            recent_memories.append(memory)
                    except:
                        continue
            
            # Sort by timestamp (newest first)
            recent_memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return recent_memories
            
        except Exception as e:
            self.logger.error(f"Error getting recent memories: {e}")
            return []
    
    def standardize_memory_file_organization(self):
        """Standardize memory file naming and folder placement."""
        try:
            self.logger.info("🔧 Standardizing memory file organization...")
            
            # Process all memory files in the root memories directory
            memories_root = "memories"
            if not os.path.exists(memories_root):
                return
            
            moved_count = 0
            renamed_count = 0
            
            for filename in os.listdir(memories_root):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(memories_root, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        memory_data = json.load(f)
                    
                    # Determine the correct directory and filename based on memory type
                    memory_type = memory_data.get('type', 'event')
                    target_dir, new_filename = self._determine_memory_organization(memory_type, filename, memory_data)
                    
                    if target_dir and new_filename:
                        # Create target directory if it doesn't exist
                        os.makedirs(target_dir, exist_ok=True)
                        
                        target_path = os.path.join(target_dir, new_filename)
                        
                        # Move and rename the file if needed
                        if filepath != target_path:
                            shutil.move(filepath, target_path)
                            moved_count += 1
                            self.logger.info(f"📁 Moved {filename} to {target_path}")
                        
                        # Update the memory data with correct ID and references
                        self._update_memory_metadata(target_path, memory_data)
                        
                except Exception as e:
                    self.logger.error(f"❌ Error processing memory file {filename}: {e}")
                    continue
            
            self.logger.info(f"✅ Memory organization complete: {moved_count} files moved, {renamed_count} files renamed")
            
        except Exception as e:
            self.logger.error(f"❌ Error standardizing memory file organization: {e}")
    
    def _determine_memory_organization(self, memory_type: str, current_filename: str, memory_data: Dict) -> Tuple[str, str]:
        """Determine the correct directory and filename for a memory file."""
        try:
            timestamp = memory_data.get('timestamp', '')
            memory_id = memory_data.get('id', '')
            
            # Generate standardized filename
            if timestamp:
                # Extract date and time from timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y%m%d_%H%M%S')
                except:
                    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            else:
                date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Determine target directory and filename based on memory type
            if memory_type == 'self_recognition_event':
                target_dir = self.memory_dirs['self_recognition']
                new_filename = f"{date_str}_self_recognition_event.json"
            elif memory_type == 'first_interaction_event':
                target_dir = self.memory_dirs['first_interaction']
                new_filename = f"{date_str}_first_interaction_event.json"
            elif memory_type == 'episodic':
                target_dir = self.memory_dirs['episodic']
                new_filename = f"episodic_{date_str}_{memory_id[-6:] if memory_id else 'unknown'}.json"
            elif memory_type == 'vision_event' or 'vision' in current_filename.lower():
                target_dir = self.memory_dirs['vision']
                new_filename = f"vision_{date_str}_{memory_id[-6:] if memory_id else 'unknown'}.json"
            elif memory_type == 'imagined':
                target_dir = self.memory_dirs['imagined']
                new_filename = f"imagined_{date_str}_{memory_id[-6:] if memory_id else 'unknown'}.json"
            else:
                # Default to episodic for general events
                target_dir = self.memory_dirs['episodic']
                new_filename = f"episodic_{date_str}_{memory_id[-6:] if memory_id else 'unknown'}.json"
            
            return target_dir, new_filename
            
        except Exception as e:
            self.logger.error(f"❌ Error determining memory organization: {e}")
            return None, None
    
    def _update_memory_metadata(self, filepath: str, memory_data: Dict):
        """Update memory metadata with correct ID and references."""
        try:
            # Ensure memory ID is never 'unknown'
            if not memory_data.get('id') or memory_data.get('id') == 'unknown':
                memory_data['id'] = self._generate_guaranteed_memory_id(memory_data)
            
            # Add scene_image_path if not present
            if 'scene_image_path' not in memory_data:
                memory_data['scene_image_path'] = self._find_associated_image_path(memory_data)
            
            # Add UUID if not present
            if 'uuid' not in memory_data:
                memory_data['uuid'] = self._generate_uuid()
            
            # Add concept references if not present
            if 'concept_references' not in memory_data:
                memory_data['concept_references'] = self._extract_concept_references(memory_data)
            
            # Add skill references if not present
            if 'skill_references' not in memory_data:
                memory_data['skill_references'] = self._extract_skill_references(memory_data)
            
            # Update the file with enhanced metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error updating memory metadata: {e}")
    
    def _find_associated_image_path(self, memory_data: Dict) -> str:
        """Find associated image path for a memory."""
        try:
            timestamp = memory_data.get('timestamp', '')
            memory_id = memory_data.get('id', '')
            
            # Search for associated images
            image_dirs = ['memories/vision', 'memories/episodic', 'memories']
            
            for image_dir in image_dirs:
                if os.path.exists(image_dir):
                    for file in os.listdir(image_dir):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                            # Check if image is associated with this memory
                            if (memory_id in file or 
                                (timestamp and any(part in file for part in timestamp.split('T')[0].split('-')))):
                                return os.path.join(image_dir, file)
            
            return ""
            
        except Exception as e:
            self.logger.error(f"❌ Error finding associated image path: {e}")
            return ""
    
    def _extract_skill_references(self, memory_data: Dict) -> List[str]:
        """Extract skill references from memory data."""
        try:
            skills = []
            
            # Extract from WHAT field
            what_field = memory_data.get('WHAT', '')
            if what_field:
                # Look for skill patterns
                skill_patterns = ['reaction_', 'turn_', 'walk_', 'sit_', 'stand_', 'wave_', 'nod_', 'shake_']
                for pattern in skill_patterns:
                    if pattern in what_field.lower():
                        skills.append(pattern.rstrip('_'))
            
            # Extract from action fields
            actions = memory_data.get('actions', [])
            if isinstance(actions, list):
                skills.extend([action for action in actions if isinstance(action, str)])
            
            return list(set(skills))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting skill references: {e}")
            return []
    
    def search_memories(self, query: str, memory_types: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories across all memory types for a specific query.
        
        Args:
            query: Search query string
            memory_types: Types of memory to search (None for all)
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            if memory_types is None:
                memory_types = ['working', 'episodic', 'semantic', 'procedural']
            
            search_results = []
            query_lower = query.lower()
            
            # Search working memory
            if 'working' in memory_types:
                for memory in self.working_memory_cache:
                    if self._memory_matches_query(memory, query_lower):
                        search_results.append(memory)
            
            # Search episodic memory
            if 'episodic' in memory_types:
                for memory in self.episodic_memory_cache.values():
                    if self._memory_matches_query(memory, query_lower):
                        search_results.append(memory)
            
            # Search semantic memory
            if 'semantic' in memory_types:
                for memory in self.semantic_memory_cache.values():
                    if self._memory_matches_query(memory, query_lower):
                        search_results.append(memory)
            
            # Search procedural memory
            if 'procedural' in memory_types:
                for memory in self.procedural_memory_cache.values():
                    if self._memory_matches_query(memory, query_lower):
                        search_results.append(memory)
            
            # Sort by relevance and recency
            search_results.sort(key=lambda x: self._calculate_search_relevance(x, query_lower), reverse=True)
            
            # Limit results
            search_results = search_results[:limit]
            
            self.logger.info(f"Memory search for '{query}': {len(search_results)} results")
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            return []
    
    def log_reflex_hit(self, user_input: str, response: str, pattern: str = None) -> str:
        """
        Log a reflex hit to memory system.
        
        Args:
            user_input: The user's input
            response: The reflex response
            pattern: The matched pattern (optional)
            
        Returns:
            Memory ID
        """
        try:
            # Create memory context for reflex
            context = MemoryContext(
                current_emotion="neutral",
                emotional_intensity=0.3,  # Low intensity for reflexes
                cognitive_load=0.1,  # Very low cognitive load
                attention_focus="reflex",
                environmental_context={
                    "reflex_type": "aiml_pattern",
                    "pattern_matched": pattern
                },
                personality_state={}
            )
            
            # Create content
            content = f"Reflex hit: '{user_input}' -> '{response}'"
            if pattern:
                content += f" (pattern: {pattern})"
            
            # Store as working memory
            memory_id = self.store_memory(
                content=content,
                memory_type="working",
                context=context,
                importance=0.4,  # Moderate importance for reflexes
                source="reflex_system"
            )
            
            self.logger.info(f"Logged reflex hit: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error logging reflex hit: {e}")
            return ""
    
    def log_openai_fallback(self, user_input: str, response: str, confidence: float = 0.6) -> str:
        """
        Log an OpenAI fallback response to memory system.
        
        Args:
            user_input: The user's input
            response: The OpenAI response
            confidence: Confidence level of the response
            
        Returns:
            Memory ID
        """
        try:
            # Create memory context for OpenAI fallback
            context = MemoryContext(
                current_emotion="curious",
                emotional_intensity=0.5,  # Moderate intensity for creative responses
                cognitive_load=0.7,  # Higher cognitive load for AI generation
                attention_focus="creative",
                environmental_context={
                    "ai_generated": True,
                    "confidence": confidence,
                    "response_type": "random"
                },
                personality_state={}
            )
            
            # Create content
            content = f"OpenAI fallback: '{user_input}' -> '{response}' (confidence: {confidence:.2f})"
            
            # Store as episodic memory (more important than reflexes)
            memory_id = self.store_memory(
                content=content,
                memory_type="episodic",
                context=context,
                importance=0.6,  # Higher importance for AI responses
                source="openai_fallback"
            )
            
            self.logger.info(f"Logged OpenAI fallback: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error logging OpenAI fallback: {e}")
            return ""
    
    def get_common_unlearned_phrases(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """
        Get phrases that appear frequently but haven't been learned as reflexes.
        
        Args:
            threshold: Minimum frequency to consider
            
        Returns:
            List of unlearned phrases with frequency data
        """
        try:
            # Analyze memory content for common phrases
            phrase_frequency = {}
            
            # Search through all memories
            all_memories = []
            all_memories.extend(self.working_memory_cache)
            all_memories.extend(self.episodic_memory_cache.values())
            all_memories.extend(self.semantic_memory_cache.values())
            
            # Extract phrases from memory content
            for memory in all_memories:
                content = memory.get('content', '')
                if 'user said:' in content.lower() or 'user input:' in content.lower():
                    # Extract user input from memory content
                    import re
                    user_inputs = re.findall(r'user (?:said|input):\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
                    for user_input in user_inputs:
                        if user_input in phrase_frequency:
                            phrase_frequency[user_input] += 1
                        else:
                            phrase_frequency[user_input] = 1
            
            # Filter phrases that appear frequently but aren't learned
            unlearned_phrases = []
            for phrase, frequency in phrase_frequency.items():
                if frequency >= threshold:
                    # Check if this phrase has been learned as a reflex
                    # This would require checking against reflex patterns
                    unlearned_phrases.append({
                        'phrase': phrase,
                        'frequency': frequency,
                        'last_seen': 'unknown',  # Could be enhanced to track timestamps
                        'learning_priority': min(1.0, frequency / 10.0)  # Normalize to 0-1
                    })
            
            # Sort by learning priority
            unlearned_phrases.sort(key=lambda x: x['learning_priority'], reverse=True)
            
            self.logger.info(f"Found {len(unlearned_phrases)} unlearned phrases above threshold {threshold}")
            return unlearned_phrases
            
        except Exception as e:
            self.logger.error(f"Error getting common unlearned phrases: {e}")
            return []
    
    def _memory_matches_query(self, memory: Dict[str, Any], query_lower: str) -> bool:
        """Check if a memory matches the search query."""
        try:
            # Search in multiple fields
            searchable_fields = [
                memory.get('content', ''),
                memory.get('summary', ''),
                memory.get('tags', []),
                memory.get('associations', [])
            ]
            
            # Convert lists to strings for searching
            searchable_text = []
            for field in searchable_fields:
                if isinstance(field, list):
                    searchable_text.extend(field)
                else:
                    searchable_text.append(str(field))
            
            # Check if query appears in any field
            full_text = ' '.join(searchable_text).lower()
            return query_lower in full_text
            
        except Exception as e:
            self.logger.error(f"Error checking memory match: {e}")
            return False
    
    def _calculate_search_relevance(self, memory: Dict[str, Any], query_lower: str) -> float:
        """Calculate relevance score for search results."""
        try:
            relevance_score = 0.0
            
            # Content relevance
            content = memory.get('content', '').lower()
            if query_lower in content:
                relevance_score += 0.5
            
            # Tag relevance
            tags = memory.get('tags', [])
            for tag in tags:
                if query_lower in tag.lower():
                    relevance_score += 0.3
            
            # Association relevance
            associations = memory.get('associations', [])
            for assoc in associations:
                if query_lower in str(assoc).lower():
                    relevance_score += 0.2
            
            # Recency bonus
            timestamp = memory.get('timestamp', '')
            if timestamp:
                try:
                    memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_diff = datetime.now() - memory_time
                    if time_diff.days < 1:
                        relevance_score += 0.1
                    elif time_diff.days < 7:
                        relevance_score += 0.05
                except:
                    pass
            
            # Importance bonus
            importance = memory.get('importance', 0.5)
            relevance_score += importance * 0.2
            
            return relevance_score
            
        except Exception as e:
            self.logger.error(f"Error calculating search relevance: {e}")
            return 0.0
    
    def _ensure_memory_consistency(self):
        """
        Ensure STM/LTM updates and concept associations are consistent across startup and runtime.
        This implements the memory consistency requirement from the user's request.
        """
        try:
            if not self.memory_consistency_enabled:
                return
            
            self.logger.info("🔧 Ensuring memory consistency across startup and runtime...")
            
            # 1. Check STM/LTM consistency
            self._check_stm_ltm_consistency()
            
            # 2. Update concept associations
            self._update_concept_associations()
            
            # 3. Ensure autonomous need/goal execution consistency
            self._ensure_autonomous_consistency()
            
            # 4. Update last consistency check
            self.last_consistency_check = datetime.now().isoformat()
            
            self.logger.info("✅ Memory consistency check completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error ensuring memory consistency: {e}")
    
    def _check_stm_ltm_consistency(self):
        """Check and maintain consistency between short-term and long-term memory."""
        try:
            # Check if working memory needs consolidation
            if len(self.working_memory_cache) > self.working_memory_capacity * 0.8:
                self.logger.info("🧠 Working memory near capacity, triggering consolidation")
                self._consolidate_working_memory()
            
            # Check if episodic memories need semantic consolidation
            if len(self.episodic_memory_cache) > self.episodic_memory_capacity * 0.9:
                self.logger.info("🧠 Episodic memory near capacity, triggering semantic consolidation")
                self._consolidate_episodic_to_semantic()
                
        except Exception as e:
            self.logger.error(f"❌ Error checking STM/LTM consistency: {e}")
    
    def _update_concept_associations(self):
        """Update concept associations to maintain consistency."""
        try:
            # Load concept associations from concept system if available
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'concept_system'):
                concept_system = self.main_app.concept_system
                if hasattr(concept_system, 'get_concept_associations'):
                    self.concept_associations = concept_system.get_concept_associations()
                    self.logger.info(f"🔗 Updated {len(self.concept_associations)} concept associations")
            
            # Update memory associations based on concept associations
            for memory_id, memory_data in self.episodic_memory_cache.items():
                if 'associations' not in memory_data:
                    memory_data['associations'] = []
                
                # Add concept-based associations
                content = memory_data.get('content', '').lower()
                for concept, associations in self.concept_associations.items():
                    if concept.lower() in content:
                        memory_data['associations'].extend(associations)
                        # Remove duplicates
                        memory_data['associations'] = list(set(memory_data['associations']))
                
        except Exception as e:
            self.logger.error(f"❌ Error updating concept associations: {e}")
    
    def _ensure_autonomous_consistency(self):
        """Ensure autonomous need/goal execution is consistent."""
        try:
            # Check if inner_self system is available for autonomous actions
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'inner_self'):
                inner_self = self.main_app.inner_self
                
                # Ensure PDB counters are consistent
                if hasattr(inner_self, 'pdb_counters'):
                    pdb_counters = inner_self.pdb_counters
                    self.logger.info(f"🎯 PDB Counters: {pdb_counters}")
                
                # Ensure needs/goals evaluation is consistent
                if hasattr(inner_self, 'evaluate_needs_and_goals'):
                    needs_goals = inner_self.evaluate_needs_and_goals()
                    self.logger.info(f"🎯 Needs/Goals: {needs_goals.get('active_needs', [])}")
                
        except Exception as e:
            self.logger.error(f"❌ Error ensuring autonomous consistency: {e}")
    
    def _consolidate_working_memory(self):
        """Consolidate working memory to long-term memory."""
        try:
            # Move important working memories to episodic memory
            important_memories = [m for m in self.working_memory_cache if m.get('importance', 0) > self.memory_consolidation_threshold]
            
            for memory in important_memories:
                # Create episodic memory item
                episodic_item = MemoryItem(
                    id=f"episodic_{memory['id']}",
                    content=memory['content'],
                    memory_type='episodic',
                    timestamp=memory['timestamp'],
                    emotional_context=memory.get('emotional_context', {}),
                    importance=memory['importance'],
                    access_count=memory.get('access_count', 0),
                    last_accessed=memory.get('last_accessed', memory['timestamp']),
                    associations=memory.get('associations', []),
                    source=memory.get('source', 'working_memory_consolidation'),
                    confidence=memory.get('confidence', 0.8),
                    decay_rate=memory.get('decay_rate', 0.1)
                )
                
                # Store in episodic memory
                self._store_episodic_memory(episodic_item)
                
                # Remove from working memory
                self.working_memory_cache.remove(memory)
            
            self.logger.info(f"🧠 Consolidated {len(important_memories)} working memories to episodic memory")
            
        except Exception as e:
            self.logger.error(f"❌ Error consolidating working memory: {e}")
    
    def _consolidate_episodic_to_semantic(self):
        """Consolidate episodic memories to semantic memory."""
        try:
            # Find episodic memories that should become semantic
            semantic_candidates = []
            for memory_id, memory_data in self.episodic_memory_cache.items():
                # Check if memory has been accessed multiple times and is important
                if (memory_data.get('access_count', 0) > 3 and 
                    memory_data.get('importance', 0) > 0.7):
                    semantic_candidates.append(memory_data)
            
            # Convert to semantic memories
            for memory in semantic_candidates:
                semantic_item = MemoryItem(
                    id=f"semantic_{memory['id']}",
                    content=memory['content'],
                    memory_type='semantic',
                    timestamp=memory['timestamp'],
                    emotional_context=memory.get('emotional_context', {}),
                    importance=memory['importance'],
                    access_count=memory.get('access_count', 0),
                    last_accessed=memory.get('last_accessed', memory['timestamp']),
                    associations=memory.get('associations', []),
                    source=memory.get('source', 'episodic_consolidation'),
                    confidence=memory.get('confidence', 0.9),
                    decay_rate=0.05  # Semantic memories decay slowly
                )
                
                # Store in semantic memory
                self._store_semantic_memory(semantic_item)
            
            self.logger.info(f"🧠 Consolidated {len(semantic_candidates)} episodic memories to semantic memory")
            
        except Exception as e:
            self.logger.error(f"❌ Error consolidating episodic to semantic memory: {e}")
