## ROCCO Baseline From CARL: What to Reuse and Provide to the Bootstrap LLM

This guide lists the CARL files and key sections you should include in your prompt to quickly bootstrap ROCCO (a quadruped robot dog) using CARL’s core cognitive architecture, while swapping in ROCCO’s hardware stack (LIDAR, IMU, map/pose services, locomotion). It also highlights where EZ-Robot specifics must be replaced.

### Primary Orchestrator (Core Loop and Events)
- `main.py`
  - Include: the main app class, event processing, cognitive loop orchestration, threading/async loops, initialization sequencing, and event/memory writing logic.
  - Rationale: Contains the coordinator for perception → judgment → action, and ties together memory, vision, and skill dispatch.
  - Adapt: Ensure hardware callbacks and sensor event creation flow through ROCCO’s perception events instead of ARC/EZ-Robot hooks.

### Cognitive Pipeline Systems (Plug-and-Play)
- `perception_system.py`
  - Include: personality-function-driven perception phases (Sensation/Intuition paths), event shaping, and perception scoring utilities.
  - Adapt: Add ROCCO sensor adapters (LIDAR scan handler, IMU/gyro, map service client, robot pose provider) to populate `event_data` consistently.
- `judgment_system.py` (if present)
  - Include: judgment phases and evaluation logic leveraged by the loop.
  - Adapt: Keep logic; no hardware coupling expected.
- `action_system.py`
  - Include: action selection, skill execution coordination, learning-aware skill file creation template logic.
  - Replace: EZ-Robot command emitters with ROCCO’s locomotion/gait controller, high-level navigation, and pose actions.
- `working_memory.py`, `memory_system.py`
  - Include: working/episodic/semantic/procedural memory coordination, add_vision_memory, consolidation thresholds, caches.
  - Adapt: Keep as-is; extend with sensor-image associations (e.g., LIDAR map snapshots) if desired.

### Agent/Skills Subsystems
- `agent_systems.py`
  - Include: directory scaffolding for `goals/`, `needs/`, `senses/`, `skills/`, `concepts/`, `memories/`, `beliefs/` and initialization helpers.
  - Adapt: Replace default `skills` with ROCCO equivalents (e.g., stand, sit, trot, turn-in-place, navigate-to, scan, head-aim).
- `position_aware_skill_system.py`
  - Include: position-aware gating and prerequisite poses for skill eligibility.
  - Adapt: Wire to ROCCO’s pose/stance states (e.g., prone, stand, crouch) and locomotion state machine.
- `skill_classification.py`
  - Include: skill taxonomy and dependency modeling.
  - Adapt: Seed with quadruped movement primitives and navigation/action families.

### Vision and Perception Enhancers (Optional but Valuable)
- `vision_system.py`
  - Include: the OpenAI Vision integration, capture/analysis cadence, and memory hooks.
  - Adapt: Replace capture with ROCCO’s camera or omit if headless; ensure rate limiting stays coherent with sensor loop timing.
- `vision_events.py`, `vision_stabilization.py`, `vision_transport.py`, `vision_deduplication.py`
  - Include selectively if you want CARL’s richer visual pipeline behaviors (stabilization, deduplication) for ROCCO.

### Concept/Dialogue/Values/Inner World (Keep for Cognitive Coherence)
- `concept_system.py`, `concept_graph_system.py`, `concept_linking_system.py`
  - Include: concept representation and linking/association utilities.
- `dialogue_state_machine.py`, `dialogue/`
  - Include: dialogue management if ROCCO will converse; otherwise keep minimal for text outputs/logging.
- `values_system.py`, `needs/`, `goals/`
  - Include: values/needs/goals; hardware-agnostic and useful for behavioral prioritization.
- `inner_world_system.py`, `inner_attention.py`, `inner_self.py`
  - Include as needed for inner-dialogue/attention modeling.
- `neucogar_emotional_engine.py`
  - Include: neurotransmitter simulation that regulates timing/variability; helps realism of loop pacing.

### Core Docs To Provide the LLM (High-Value Blueprints)
- `docs/ENHANCED_COGNITIVE_LOOP_IMPLEMENTATION.md`
- `docs/COGNITIVE_PROCESSING_IMPROVEMENTS.md`
- `docs/ABSTRACT.md` (and/or `docs/Abstract_v5.13.2.txt`)
- `docs/VISION_SYSTEM_IMPLEMENTATION.md`
- `docs/MEMORY_SYSTEM_ARCHITECTURE_DOCUMENTATION.md`
- Optionally: `AIML_REFLEX_INTEGRATION_SUMMARY.md` if you want reflex → fallback → full processing behavior

These documents concisely explain the intended loop cadence, phases, and integration points—perfect for guiding the bootstrap LLM’s scaffolding.

### Files To Avoid Copying Over (EZ-Robot Specific)
- `ezrobot.py`
- ARC-specific scripts: `ARC_HTTP_POST_SCRIPT.js`, `ARC_VISION_POST_SCRIPT.js`, `ARC_VISION_SCRIPT_MODIFIED.js`
- Any `skills/*.json` referencing `EZRobot-...` techniques (use as shape examples only)

Use them only as references for data shapes and command dispatch patterns; replace the emitters with ROCCO’s control stack.

### ROCCO Hardware Integration: Adapters to Stub
Create thin adapters that translate ROCCO’s hardware/services into CARL’s perception/event model and action calls.

- Sensors (Perception Inputs)
  - LIDAR Adapter
    - Provides: latest scan, obstacle summary, free-space vectors, hazard flags
    - Injects into: `PerceptionSystem` → `event_data['environment']` and `nouns`/context cues (e.g., “corridor”, “open area”)
  - IMU/Gyro Adapter
    - Provides: orientation, angular rates, stability flags, foot contact if available
    - Injects into: `event_data['robot_state']` (balance, pitch/roll thresholds)
  - Map Service Client
    - Provides: occupancy/grid/topo map query, path cost summaries
    - Injects into: `event_data['map']` and navigation context
  - Robot Position Node
    - Provides: pose (x,y,theta), frame, covariance if available
    - Injects into: `event_data['pose']`

- Actions (Behavior Outputs)
  - Locomotion/Gait Controller
    - Replaces EZ-Robot techniques with: stand, sit, trot, step, rotate-in-place, navigate-to(x,y), path-follow(list), stop
    - Integrate into `action_system.py` skill dispatch; map skill names → ROCCO commands
  - Head/Body Aiming
    - For sensor scanning and attention expressions (tie into needs/curiosity)

Keep adapters small and stateless; centralize state in CARL systems (memory/working memory/agent systems).

### Minimal File Set To Hand the LLM (Start Here)
Provide these files/verbatim sections to the bootstrap LLM to save the most time:
1) Orchestrator and Loop
- `main.py`: app class/init; event creation and memory write; cognitive loop cadence; process_input path

2) Cognitive Systems
- `perception_system.py`
- `judgment_system.py` (or the relevant judgment logic in `main.py`/docs if embedded)
- `action_system.py`

3) Memory
- `memory_system.py`
- `working_memory.py`
- `docs/MEMORY_SYSTEM_ARCHITECTURE_DOCUMENTATION.md`

4) Agent/Skills
- `agent_systems.py`
- `position_aware_skill_system.py`
- `skill_classification.py`

5) Vision (optional but ready-to-plug)
- `vision_system.py`
- `docs/VISION_SYSTEM_IMPLEMENTATION.md`

6) Cognitive Loop Design (docs)
- `docs/ENHANCED_COGNITIVE_LOOP_IMPLEMENTATION.md`
- `docs/COGNITIVE_PROCESSING_IMPROVEMENTS.md`
- `docs/ABSTRACT.md`

### Replacement Plan (High-Level)
- Replace EZ-Robot emitters:
  - In `action_system.py`, switch technique dispatch from `EZRobot-*` to ROCCO control client.
- Add ROCCO sensor adapters:
  - New modules: `rocco_lidar_adapter.py`, `rocco_imu_adapter.py`, `rocco_map_client.py`, `rocco_pose_client.py`.
  - Wire their updates into `PerceptionSystem` event assembly.
- Seed ROCCO skills:
  - Populate `skills/` with JSONs for locomotion, postures, scan behaviors; migrate keywords/motivators to match.
- Keep cognitive timing/regulation:
  - Preserve NEUCOGAR timing modulation and phase pacing from docs and loop implementation.

### Checklist for Your Prompt to the Bootstrap LLM
- Include the listed files and doc excerpts above (verbatim where possible)
- Ask to:
  - Preserve CARL’s cognitive loop phases and NEUCOGAR timing
  - Implement ROCCO sensor adapters and inject into perception events
  - Replace action emitters with ROCCO locomotion/navigation/head control
  - Initialize directories and memory system as-is
  - Provide a small demo skill set (stand, sit, trot, rotate, navigate-to)
  - Keep reflex → fallback → full processing behavior optional (include doc if desired)

This bundle gives the LLM a complete cognitive substrate with minimal hardware coupling and clear seams for ROCCO’s quadruped stack.
