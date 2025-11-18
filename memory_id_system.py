#!/usr/bin/env python3
"""
CARL Memory ID (MID) System

This module implements a unique Memory ID system that:
1. Generates unique IDs at the point of ARC vision capture
2. Propagates MID through all related event files (vision, episodic, self_recognition_event)
3. Ensures CME search results contain correct MID and image file paths
4. Prevents CME display errors by validating memory file existence

The MID system provides traceability and consistency across all memory-related operations.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

class MemoryIDSystem:
    """
    CARL's Memory ID system for unique identification and traceability.
    """
    
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # MID registry for tracking all generated IDs
        self.mid_registry = {}
        
        # Image path registry for tracking image-MID associations
        self.image_mid_registry = {}
        
        # Event file registry for tracking MID-event associations
        self.event_mid_registry = {}
        
        # Load existing registry data
        self._load_registry_data()
    
    def _load_registry_data(self):
        """Load existing registry data from disk."""
        try:
            registry_file = "memory_id_registry.json"
            if os.path.exists(registry_file):
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mid_registry = data.get('mid_registry', {})
                    self.image_mid_registry = data.get('image_mid_registry', {})
                    self.event_mid_registry = data.get('event_mid_registry', {})
                self.logger.info(f"📋 Loaded MID registry with {len(self.mid_registry)} entries")
        except Exception as e:
            self.logger.error(f"Error loading MID registry: {e}")
    
    def _save_registry_data(self):
        """Save registry data to disk."""
        try:
            registry_file = "memory_id_registry.json"
            data = {
                'mid_registry': self.mid_registry,
                'image_mid_registry': self.image_mid_registry,
                'event_mid_registry': self.event_mid_registry,
                'last_updated': datetime.now().isoformat()
            }
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving MID registry: {e}")
    
    def generate_mid(self, source: str = "vision_capture") -> str:
        """
        Generate a unique Memory ID (MID).
        
        Args:
            source: Source of the MID generation (e.g., "vision_capture", "episodic_event")
            
        Returns:
            Unique Memory ID string
        """
        try:
            # Generate timestamp-based ID with UUID component for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uuid_component = str(uuid.uuid4())[:8]
            mid = f"MID_{timestamp}_{uuid_component}"
            
            # Register the MID
            self.mid_registry[mid] = {
                'generated_at': datetime.now().isoformat(),
                'source': source,
                'status': 'active',
                'related_files': [],
                'image_path': None,
                'event_files': []
            }
            
            self.logger.info(f"🆔 Generated MID: {mid} (source: {source})")
            return mid
            
        except Exception as e:
            self.logger.error(f"Error generating MID: {e}")
            return f"MID_ERROR_{int(time.time())}"
    
    def associate_image_with_mid(self, mid: str, image_path: str) -> bool:
        """
        Associate an image file with a MID.
        
        Args:
            mid: Memory ID
            image_path: Path to the image file
            
        Returns:
            True if association was successful
        """
        try:
            if mid not in self.mid_registry:
                self.logger.warning(f"MID {mid} not found in registry")
                return False
            
            # Update MID registry with image path
            self.mid_registry[mid]['image_path'] = image_path
            self.mid_registry[mid]['related_files'].append(image_path)
            
            # Update image-MID registry
            self.image_mid_registry[image_path] = mid
            
            self.logger.info(f"📸 Associated image {os.path.basename(image_path)} with MID {mid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error associating image with MID: {e}")
            return False
    
    def associate_event_with_mid(self, mid: str, event_file_path: str, event_type: str = "episodic") -> bool:
        """
        Associate an event file with a MID.
        
        Args:
            mid: Memory ID
            event_file_path: Path to the event file
            event_type: Type of event (episodic, vision, self_recognition, etc.)
            
        Returns:
            True if association was successful
        """
        try:
            if mid not in self.mid_registry:
                self.logger.warning(f"MID {mid} not found in registry")
                return False
            
            # Update MID registry with event file
            self.mid_registry[mid]['event_files'].append({
                'path': event_file_path,
                'type': event_type,
                'created_at': datetime.now().isoformat()
            })
            self.mid_registry[mid]['related_files'].append(event_file_path)
            
            # Update event-MID registry
            self.event_mid_registry[event_file_path] = {
                'mid': mid,
                'type': event_type,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"📄 Associated {event_type} event {os.path.basename(event_file_path)} with MID {mid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error associating event with MID: {e}")
            return False
    
    def get_mid_for_image(self, image_path: str) -> Optional[str]:
        """
        Get the MID associated with an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            MID if found, None otherwise
        """
        return self.image_mid_registry.get(image_path)
    
    def get_mid_for_event(self, event_file_path: str) -> Optional[str]:
        """
        Get the MID associated with an event file.
        
        Args:
            event_file_path: Path to the event file
            
        Returns:
            MID if found, None otherwise
        """
        event_data = self.event_mid_registry.get(event_file_path)
        return event_data['mid'] if event_data else None
    
    def get_mid_info(self, mid: str) -> Optional[Dict]:
        """
        Get complete information about a MID.
        
        Args:
            mid: Memory ID
            
        Returns:
            Dictionary with MID information or None if not found
        """
        return self.mid_registry.get(mid)
    
    def validate_memory_file_exists(self, file_path: str) -> bool:
        """
        Validate that a memory file exists and is accessible.
        
        Args:
            file_path: Path to the memory file
            
        Returns:
            True if file exists and is accessible
        """
        try:
            if not file_path:
                return False
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.logger.warning(f"Memory file not found: {file_path}")
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                self.logger.warning(f"Memory file not readable: {file_path}")
                return False
            
            # Check if file has content
            if os.path.getsize(file_path) == 0:
                self.logger.warning(f"Memory file is empty: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating memory file {file_path}: {e}")
            return False
    
    def get_cme_search_results_with_mid(self, search_query: str) -> List[Dict]:
        """
        Get CME search results with MID and validated file paths.
        
        Args:
            search_query: Search query string
            
        Returns:
            List of search results with MID and validated file paths
        """
        try:
            results = []
            
            # Search through event files
            for event_file, event_data in self.event_mid_registry.items():
                mid = event_data['mid']
                event_type = event_data['type']
                
                # Validate file exists
                if not self.validate_memory_file_exists(event_file):
                    continue
                
                # Get MID info
                mid_info = self.get_mid_info(mid)
                if not mid_info:
                    continue
                
                # Create search result
                result = {
                    'mid': mid,
                    'event_file': event_file,
                    'event_type': event_type,
                    'image_path': mid_info.get('image_path'),
                    'created_at': event_data['created_at'],
                    'validated': True
                }
                
                # Validate image path if it exists
                if result['image_path']:
                    result['image_validated'] = self.validate_memory_file_exists(result['image_path'])
                else:
                    result['image_validated'] = False
                
                results.append(result)
            
            self.logger.info(f"🔍 CME search returned {len(results)} results with MID validation")
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting CME search results: {e}")
            return []
    
    def create_vision_memory_with_mid(self, vision_data: Dict, image_path: str) -> Tuple[str, str]:
        """
        Create vision memory with MID association.
        
        Args:
            vision_data: Vision analysis data
            image_path: Path to the captured image
            
        Returns:
            Tuple of (MID, memory_file_path)
        """
        try:
            # Generate MID for this vision capture
            mid = self.generate_mid("vision_capture")
            
            # Associate image with MID
            self.associate_image_with_mid(mid, image_path)
            
            # Create vision memory file
            memory_data = {
                "mid": mid,
                "type": "vision_memory",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "image_filename": os.path.basename(image_path),
                "vision_data": vision_data,
                "related_events": [],
                "validation": {
                    "image_exists": self.validate_memory_file_exists(image_path),
                    "mid_registered": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Save vision memory file
            memory_filename = f"vision_memory_{mid}.json"
            memory_file_path = os.path.join("memories", memory_filename)
            
            # Ensure memories directory exists
            os.makedirs("memories", exist_ok=True)
            
            with open(memory_file_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
            
            # Associate event file with MID
            self.associate_event_with_mid(mid, memory_file_path, "vision_memory")
            
            # Save registry data
            self._save_registry_data()
            
            self.logger.info(f"📸 Created vision memory with MID {mid}: {memory_filename}")
            return mid, memory_file_path
            
        except Exception as e:
            self.logger.error(f"Error creating vision memory with MID: {e}")
            return "", ""
    
    def create_episodic_memory_with_mid(self, episodic_data: Dict, related_mid: str = None) -> Tuple[str, str]:
        """
        Create episodic memory with MID association.
        
        Args:
            episodic_data: Episodic memory data
            related_mid: Related MID if this is linked to a vision event
            
        Returns:
            Tuple of (MID, memory_file_path)
        """
        try:
            # Generate MID for this episodic event
            mid = self.generate_mid("episodic_event")
            
            # Create episodic memory file
            memory_data = {
                "mid": mid,
                "type": "episodic_memory",
                "timestamp": datetime.now().isoformat(),
                "episodic_data": episodic_data,
                "related_mid": related_mid,
                "related_events": [],
                "validation": {
                    "mid_registered": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Save episodic memory file
            memory_filename = f"episodic_memory_{mid}.json"
            memory_file_path = os.path.join("memories", memory_filename)
            
            # Ensure memories directory exists
            os.makedirs("memories", exist_ok=True)
            
            with open(memory_file_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2)
            
            # Associate event file with MID
            self.associate_event_with_mid(mid, memory_file_path, "episodic_memory")
            
            # Link with related MID if provided
            if related_mid and related_mid in self.mid_registry:
                self.mid_registry[mid]['related_mid'] = related_mid
                self.mid_registry[related_mid]['related_events'].append(mid)
            
            # Save registry data
            self._save_registry_data()
            
            self.logger.info(f"📝 Created episodic memory with MID {mid}: {memory_filename}")
            return mid, memory_file_path
            
        except Exception as e:
            self.logger.error(f"Error creating episodic memory with MID: {e}")
            return "", ""
    
    def create_self_recognition_event_with_mid(self, self_recognition_data: Dict, image_path: str) -> Tuple[str, str]:
        """
        Create self-recognition event with MID association.
        
        Args:
            self_recognition_data: Self-recognition event data
            image_path: Path to the image where self was recognized
            
        Returns:
            Tuple of (MID, event_file_path)
        """
        try:
            # Generate MID for this self-recognition event
            mid = self.generate_mid("self_recognition")
            
            # Associate image with MID
            self.associate_image_with_mid(mid, image_path)
            
            # Create self-recognition event file
            event_data = {
                "mid": mid,
                "type": "self_recognition_event",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "image_filename": os.path.basename(image_path),
                "self_recognition_data": self_recognition_data,
                "validation": {
                    "image_exists": self.validate_memory_file_exists(image_path),
                    "mid_registered": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Save self-recognition event file
            event_filename = f"self_recognition_event_{mid}.json"
            event_file_path = os.path.join("memories", event_filename)
            
            # Ensure memories directory exists
            os.makedirs("memories", exist_ok=True)
            
            with open(event_file_path, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, indent=2)
            
            # Associate event file with MID
            self.associate_event_with_mid(mid, event_file_path, "self_recognition_event")
            
            # Save registry data
            self._save_registry_data()
            
            self.logger.info(f"🪞 Created self-recognition event with MID {mid}: {event_filename}")
            return mid, event_file_path
            
        except Exception as e:
            self.logger.error(f"Error creating self-recognition event with MID: {e}")
            return "", ""
    
    def get_mid_summary(self) -> Dict:
        """
        Get a summary of the MID system status.
        
        Returns:
            Dictionary with MID system information
        """
        return {
            'total_mids': len(self.mid_registry),
            'total_images': len(self.image_mid_registry),
            'total_events': len(self.event_mid_registry),
            'active_mids': len([mid for mid, data in self.mid_registry.items() if data.get('status') == 'active']),
            'last_updated': datetime.now().isoformat()
        }
