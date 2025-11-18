#!/usr/bin/env python3
"""
Create a flowchart diagram illustrating CARL's Startup Process.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_startup_flowchart_matplotlib(output_path="docs/CARL_Startup_Process_Flowchart.png"):
    """Create comprehensive startup process flowchart using matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(24, 22))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 26)
    ax.axis('off')
    
    # Color scheme
    config_color = '#E3F2FD'  # Light blue - configuration
    core_color = '#FFF3E0'  # Light orange - core systems
    cognitive_color = '#E8F5E9'  # Light green - cognitive systems
    hardware_color = '#F3E5F5'  # Light purple - hardware/connections
    integration_color = '#FCE4EC'  # Light pink - integration
    ready_color = '#C8E6C9'  # Light green - ready state
    
    # Define positions (x, y, width, height)
    boxes = {
        # === START (y=25) ===
        'start': (12, 25, 4, 0.8),
        
        # === CONFIGURATION PHASE (y=23) ===
        'config_check': (12, 23, 5, 1),
        
        # === CORE INITIALIZATION (y=21) ===
        'action_system': (3, 21, 3.5, 1),
        'position_system': (8, 21, 3.5, 1),
        'curiosity': (13, 21, 3.5, 1),
        'memory_id': (18, 21, 3.5, 1),
        
        # === COGNITIVE SYSTEMS (y=19) ===
        'perception_system': (4, 19, 3.5, 1),
        'judgment_system': (9, 19, 3.5, 1),
        'memory_system': (14, 19, 3.5, 1),
        'concept_system': (19, 19, 3.5, 1),
        
        # === ADVANCED SYSTEMS (y=17) ===
        'neucogar': (4, 17, 3.5, 1),
        'inner_self': (9, 17, 3.5, 1),
        'attention': (14, 17, 3.5, 1),
        'concept_graph': (19, 17, 3.5, 1),
        
        # === GAME & LOGIC SYSTEMS (y=15) ===
        'game_theory': (6, 15, 3.5, 1),
        'logic_system': (12, 15, 3.5, 1),
        'earthly_game': (18, 15, 3.5, 1),
        
        # === API & CLIENT (y=13) ===
        'api_client': (6, 13, 3.5, 1),
        'working_memory': (12, 13, 3.5, 1),
        'memory_retrieval': (18, 13, 3.5, 1),
        
        # === HARDWARE CONNECTION (y=11) ===
        'ez_robot_init': (6, 11, 4, 1),
        'flask_server': (12, 11, 4, 1),
        'vision_system': (18, 11, 4, 1),
        
        # === ENHANCED SYSTEMS (y=9) ===
        'enhanced_eye': (4, 9, 3.5, 1),
        'enhanced_skill': (9, 9, 3.5, 1),
        'imagination': (14, 9, 3.5, 1),
        'startup_seq': (19, 9, 3.5, 1),
        
        # === STARTUP SEQUENCING (y=7) ===
        'connection_test': (4, 7, 3.5, 1),
        'eye_setup': (9, 7, 3.5, 1),
        'speech_test': (14, 7, 3.5, 1),
        'body_test': (19, 7, 3.5, 1),
        
        # === GUI INITIALIZATION (y=5) ===
        'gui_create': (8, 5, 4, 1),
        'gui_widgets': (16, 5, 4, 1),
        
        # === KNOWLEDGE LOADING (y=3) ===
        'load_memories': (4, 3, 3.5, 1),
        'load_concepts': (9, 3, 3.5, 1),
        'load_people': (14, 3, 3.5, 1),
        'load_skills': (19, 3, 3.5, 1),
        
        # === READY STATE (y=1) ===
        'ready': (12, 1, 6, 1),
    }
    
    # Draw boxes with appropriate colors
    for name, (x, y, w, h) in boxes.items():
        # Determine color
        if name == 'start':
            color = '#BBDEFB'  # Medium blue
        elif name in ['config_check']:
            color = config_color
        elif name in ['action_system', 'position_system', 'curiosity', 'memory_id']:
            color = core_color
        elif name in ['perception_system', 'judgment_system', 'memory_system', 'concept_system',
                      'neucogar', 'inner_self', 'attention', 'concept_graph', 'game_theory',
                      'logic_system', 'earthly_game', 'api_client', 'working_memory', 'memory_retrieval']:
            color = cognitive_color
        elif name in ['ez_robot_init', 'flask_server', 'vision_system', 'enhanced_eye',
                      'enhanced_skill', 'imagination', 'startup_seq', 'connection_test',
                      'eye_setup', 'speech_test', 'body_test']:
            color = hardware_color
        elif name in ['gui_create', 'gui_widgets', 'load_memories', 'load_concepts',
                      'load_people', 'load_skills']:
            color = integration_color
        else:
            color = ready_color
        
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                             boxstyle="round,pad=0.1", 
                             facecolor=color, 
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        
        # Add text with detailed labels
        labels = {
            'start': 'CARL Startup',
            'config_check': 'Configuration Check\nsettings_current.ini\nsettings_default.ini',
            'action_system': 'Action System\nPhysical Behaviors',
            'position_system': 'Position System\nSpatial Awareness',
            'curiosity': 'Curiosity Module\nExploration Drive',
            'memory_id': 'Memory ID System\nUnique Identifiers',
            'perception_system': 'Perception System\nMulti-Modal Input',
            'judgment_system': 'Judgment System\nDecision Making',
            'memory_system': 'Memory System\nSTM/LTM Storage',
            'concept_system': 'Concept System\nKnowledge Base',
            'neucogar': 'NEUCOGAR Engine\nNeurotransmitters',
            'inner_self': 'Inner Self\nInternal Thoughts',
            'attention': 'Attention Manager\nFocus Control',
            'concept_graph': 'Concept Graph\nAssociations',
            'game_theory': 'Game Theory\nStrategic Planning',
            'logic_system': 'Logic System\nReasoning',
            'earthly_game': 'Earthly Game\nLife Simulation',
            'api_client': 'API Client\nOpenAI Integration',
            'working_memory': 'Working Memory\nActive Context',
            'memory_retrieval': 'Memory Retrieval\nRecall System',
            'ez_robot_init': 'EZ-Robot Init\nHardware Connection',
            'flask_server': 'Flask Server\nSpeech HTTP (Port 5000)',
            'vision_system': 'Vision System\nARC Camera',
            'enhanced_eye': 'Enhanced Eye\nExpression System',
            'enhanced_skill': 'Enhanced Skill\nExecution System',
            'imagination': 'Imagination System\nDALL·E Integration',
            'startup_seq': 'Startup Sequencing\nControlled Init',
            'connection_test': 'Connection Test\nHTTP Server Check',
            'eye_setup': 'Eye Expression\nInitial Setup',
            'speech_test': 'Speech Test\nAudio System',
            'body_test': 'Body Function Test\nMovement Check',
            'gui_create': 'GUI Creation\nTkinter Window',
            'gui_widgets': 'GUI Widgets\nControls & Display',
            'load_memories': 'Load Memories\nExisting Knowledge',
            'load_concepts': 'Load Concepts\nKnowledge Base',
            'load_people': 'Load People\nSocial Memory',
            'load_skills': 'Load Skills\nBehavior Library',
            'ready': 'CARL Ready\nOperational State',
        }
        
        ax.text(x, y, labels.get(name, name), 
               ha='center', va='center', 
               fontsize=7.5, weight='bold',
               wrap=True)
    
    # Draw arrows with labels
    arrows = [
        # Main flow
        ('start', 'config_check', 'Begin', 'blue'),
        ('config_check', 'action_system', 'Config Loaded', 'blue'),
        
        # Core initialization
        ('action_system', 'position_system', '', 'orange'),
        ('position_system', 'curiosity', '', 'orange'),
        ('curiosity', 'memory_id', '', 'orange'),
        
        # Cognitive systems
        ('memory_id', 'perception_system', 'Core Ready', 'green'),
        ('perception_system', 'judgment_system', '', 'green'),
        ('judgment_system', 'memory_system', '', 'green'),
        ('memory_system', 'concept_system', '', 'green'),
        
        # Advanced systems
        ('concept_system', 'neucogar', 'Cognitive Ready', 'green'),
        ('neucogar', 'inner_self', '', 'green'),
        ('inner_self', 'attention', '', 'green'),
        ('attention', 'concept_graph', '', 'green'),
        
        # Game & logic
        ('concept_graph', 'game_theory', 'Advanced Ready', 'green'),
        ('game_theory', 'logic_system', '', 'green'),
        ('logic_system', 'earthly_game', '', 'green'),
        
        # API & client
        ('earthly_game', 'api_client', 'Systems Ready', 'green'),
        ('api_client', 'working_memory', '', 'green'),
        ('working_memory', 'memory_retrieval', '', 'green'),
        
        # Hardware connection
        ('memory_retrieval', 'ez_robot_init', 'Init Hardware', 'purple'),
        ('ez_robot_init', 'flask_server', 'EZ-Robot Ready', 'purple'),
        ('flask_server', 'vision_system', 'Flask Running', 'purple'),
        
        # Enhanced systems
        ('vision_system', 'enhanced_eye', 'Hardware Ready', 'purple'),
        ('enhanced_eye', 'enhanced_skill', '', 'purple'),
        ('enhanced_skill', 'imagination', '', 'purple'),
        ('imagination', 'startup_seq', '', 'purple'),
        
        # Startup sequencing
        ('startup_seq', 'connection_test', 'Start Sequence', 'purple'),
        ('connection_test', 'eye_setup', 'Connection OK', 'purple'),
        ('eye_setup', 'speech_test', 'Eyes Ready', 'purple'),
        ('speech_test', 'body_test', 'Speech OK', 'purple'),
        
        # GUI initialization
        ('body_test', 'gui_create', 'Hardware Tested', 'pink'),
        ('gui_create', 'gui_widgets', 'GUI Created', 'pink'),
        
        # Knowledge loading
        ('gui_widgets', 'load_memories', 'GUI Ready', 'pink'),
        ('load_memories', 'load_concepts', 'Memories Loaded', 'pink'),
        ('load_concepts', 'load_people', 'Concepts Loaded', 'pink'),
        ('load_people', 'load_skills', 'People Loaded', 'pink'),
        
        # Ready state
        ('load_skills', 'ready', 'Knowledge Loaded', 'darkgreen'),
    ]
    
    for start, end, label, color in arrows:
        x1, y1 = boxes[start][0], boxes[start][1] - boxes[start][3]/2
        x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        # Adjust for horizontal connections
        if abs(x2 - x1) > 2:
            connectionstyle = "arc3,rad=0.2"
        else:
            connectionstyle = "arc3,rad=0.1"
        
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', 
                               mutation_scale=25,
                               color=color,
                               linewidth=2,
                               alpha=0.8,
                               connectionstyle=connectionstyle)
        ax.add_patch(arrow)
        
        # Add label for important arrows
        if label and label not in ['']:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            # Adjust label position to avoid overlap
            if abs(y2 - y1) < 1:
                mid_y += 0.4
            ax.text(mid_x, mid_y, label, 
                   ha='center', va='center',
                   fontsize=6, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Add title
    ax.text(12, 25.8, "CARL Startup Process - Initialization Sequence", 
           ha='center', va='center',
           fontsize=18, weight='bold')
    
    # Add subtitle
    ax.text(12, 25.4, "Configuration → Core Systems → Cognitive Systems → Hardware → GUI → Knowledge → Ready", 
           ha='center', va='center',
           fontsize=11, style='italic', color='gray')
    
    # Add phase labels
    phase_y_positions = [23, 19, 15, 11, 7, 5, 3, 1]
    phase_labels = [
        'Configuration',
        'Cognitive Systems',
        'Game & Logic',
        'Hardware Connection',
        'Startup Sequencing',
        'GUI Initialization',
        'Knowledge Loading',
        'Ready State'
    ]
    
    for i, (y_pos, label) in enumerate(zip(phase_y_positions, phase_labels)):
        ax.text(0.5, y_pos, label, 
               ha='left', va='center',
               fontsize=9, weight='bold', style='italic',
               color='gray',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray'))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=config_color, label='Configuration', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=core_color, label='Core Systems', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=cognitive_color, label='Cognitive Systems', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=hardware_color, label='Hardware/Connections', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=integration_color, label='Integration', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=ready_color, label='Ready State', edgecolor='black', linewidth=1.5),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Flowchart saved to: {output_path}")
    plt.close()
    return output_path

if __name__ == "__main__":
    output_path = "docs/CARL_Startup_Process_Flowchart.png"
    create_startup_flowchart_matplotlib(output_path)

