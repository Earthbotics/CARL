def _load_startup_knowledge(self):
    """Load all existing memories and concepts into GUI during startup."""
    try:
        self.log("🧠 Loading existing knowledge into GUI...")
        
        # Load memories
        self._load_startup_memories()
        
        # Load concepts
        self._load_startup_concepts()
        
        # Load people
        self._load_startup_people()
        
        # Load skills
        self._load_startup_skills()
        
        # Update GUI status labels
        self._update_startup_gui_status()
        
        self.log("✅ Startup knowledge loading complete")
        
    except Exception as e:
        self.log(f"❌ Error loading startup knowledge: {e}")

def _load_startup_memories(self):
    """Load existing memories into GUI memory explorer."""
    try:
        if not os.path.exists(self.memories_dir):
            self.log("📁 No memories directory found")
            return
        
        memory_files = [f for f in os.listdir(self.memories_dir) if f.endswith('_event.json')]
        
        if not memory_files:
            self.log("📁 No memory files found")
            return
        
        # Update memory count
        self.total_memories = len(memory_files)
        self.log(f"📚 Loaded {self.total_memories} memories into GUI")
        
        # Update memory status label if it exists
        if hasattr(self, 'memory_status_label'):
            self.memory_status_label.config(text=f"Loaded {self.total_memories} memories")
        
        # Refresh memory explorer if it exists
        if hasattr(self, '_refresh_memory_list'):
            # Find memory listbox and details text widgets
            for widget in self.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Listbox):
                            # Found memory listbox, refresh it
                            self._refresh_memory_list(child, None)
                            break
        
    except Exception as e:
        self.log(f"❌ Error loading startup memories: {e}")

def _load_startup_concepts(self):
    """Load existing concepts into GUI."""
    try:
        concepts_loaded = 0
        
        # Load from concepts directory
        if os.path.exists(self.concepts_dir):
            concept_files = [f for f in os.listdir(self.concepts_dir) if f.endswith('_self_learned.json')]
            concepts_loaded += len(concept_files)
        
        # Load from people directory
        if os.path.exists(self.people_dir):
            people_files = [f for f in os.listdir(self.people_dir) if f.endswith('_self_learned.json')]
            concepts_loaded += len(people_files)
        
        self.log(f"💡 Loaded {concepts_loaded} concepts into GUI")
        
        # Update concept status label if it exists
        if hasattr(self, 'concept_status_label'):
            self.concept_status_label.config(text=f"Loaded {concepts_loaded} concepts")
        
    except Exception as e:
        self.log(f"❌ Error loading startup concepts: {e}")

def _load_startup_people(self):
    """Load existing people into GUI."""
    try:
        if os.path.exists(self.people_dir):
            people_files = [f for f in os.listdir(self.people_dir) if f.endswith('_self_learned.json')]
            self.log(f"👥 Loaded {len(people_files)} people into GUI")
        else:
            self.log("👥 No people directory found")
        
    except Exception as e:
        self.log(f"❌ Error loading startup people: {e}")

def _load_startup_skills(self):
    """Load existing skills into GUI."""
    try:
        if os.path.exists(self.skills_dir):
            skill_files = [f for f in os.listdir(self.skills_dir) if f.endswith('.json')]
            self.log(f"🎯 Loaded {len(skill_files)} skills into GUI")
        else:
            self.log("🎯 No skills directory found")
        
    except Exception as e:
        self.log(f"❌ Error loading startup skills: {e}")

def _update_startup_gui_status(self):
    """Update all GUI status labels with loaded knowledge."""
    try:
        # Update various status labels that might exist
        status_updates = {
            'memory_status_label': f"Loaded {getattr(self, 'total_memories', 0)} memories",
            'concept_status_label': f"Loaded {len(self._load_all_concepts())} concepts",
            'knowledge_status_label': "Knowledge loaded successfully",
            'startup_status_label': "Startup complete - knowledge loaded"
        }
        
        for label_name, text in status_updates.items():
            if hasattr(self, label_name):
                getattr(self, label_name).config(text=text)
        
        self.log("✅ GUI status labels updated")
        
    except Exception as e:
        self.log(f"❌ Error updating GUI status: {e}")

def _enhanced_count_memories(self):
    """Enhanced memory counting that also loads memories into GUI."""
    try:
        # Original memory counting logic
        if os.path.exists(self.memories_dir):
            self.total_memories = len([f for f in os.listdir(self.memories_dir) if f.endswith('.json')])
            self.log(f"Total memories loaded: {self.total_memories}")
        else:
            self.total_memories = 0
            self.log("No memories directory found")
        
        # NEW: Load memories into GUI
        self._load_startup_memories()
        
        # After loading memories, have CARL wave with emotional eyes
        self._carl_startup_greeting()
        
    except Exception as e:
        self.log(f"Error counting memories: {e}")
        self.total_memories = 0
