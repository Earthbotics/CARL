#!/usr/bin/env python3
"""
Create a flowchart diagram illustrating CARL's perception mechanisms.
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Graphviz not available, using matplotlib fallback")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch
import numpy as np
import os

def create_perception_flowchart_graphviz(output_path="docs/CARL_Perception_Mechanisms_Flowchart.png"):
    """Create flowchart using Graphviz."""
    dot = Digraph(comment='CARL Perception Mechanisms', format='png')
    dot.attr(rankdir='TB', size='16,12', dpi=300)
    dot.attr('node', shape='box', style='rounded,filled', fontsize='10')
    dot.attr('edge', fontsize='9')
    
    # Color scheme
    input_color = '#E3F2FD'  # Light blue for inputs
    process_color = '#FFF3E0'  # Light orange for processing
    integration_color = '#E8F5E9'  # Light green for integration
    output_color = '#F3E5F5'  # Light purple for outputs
    
    # === INPUT LAYER ===
    dot.node('speech', 'Speech Recognition\n(Flask Server)\nReal-time Audio Input', 
             fillcolor=input_color, fontcolor='black')
    dot.node('vision', 'Vision Processing\n(ARC Camera System)\nObject, Face, Color Detection', 
             fillcolor=input_color, fontcolor='black')
    dot.node('motion', 'Motion Detection\n(Exploration System)\nDynamically Enabled/Disabled', 
             fillcolor=input_color, fontcolor='black')
    dot.node('text', 'Text Input\nDirect Text Entry', 
             fillcolor=input_color, fontcolor='black')
    
    # === VISION PROCESSING PIPELINE ===
    dot.node('vision_transport', 'Vision Transport\nExponential Backoff\nCircuit Breaker', 
             fillcolor=process_color, fontcolor='black')
    dot.node('vision_dedup', 'Vision Deduplication\nTTL-based Caching\nPrevents Spam', 
             fillcolor=process_color, fontcolor='black')
    dot.node('vision_stabilization', 'Vision Stabilization\nNoise Reduction\nTemporal Smoothing', 
             fillcolor=process_color, fontcolor='black')
    dot.node('vision_analysis', 'Vision Analysis\n(OpenAI Vision API)\nObject Recognition\nDanger/Pleasure Detection', 
             fillcolor=process_color, fontcolor='black')
    
    # === PERCEPTION PROCESSING ===
    dot.node('intent_class', 'Intent Classification\n(OpenAI Analysis)\nSpeech Act Detection\nUser Intent Identification', 
             fillcolor=process_color, fontcolor='black')
    dot.node('context_aware', 'Context Awareness\nConversation History\nEmotional State\nVisual Information', 
             fillcolor=process_color, fontcolor='black')
    dot.node('personality', 'Personality Functions\n(40% Processing Time)\nExtroversion/Introversion\nSensation/Intuition', 
             fillcolor=process_color, fontcolor='black')
    dot.node('aiml_reflex', 'AIML Reflex Layer\nPattern Matching\nFast Response System', 
             fillcolor=process_color, fontcolor='black')
    
    # === CROSS-REFERENCING ===
    dot.node('cross_ref', 'Cross-Referencing\nNeeds, Goals, Skills\nConcepts Integration', 
             fillcolor=integration_color, fontcolor='black')
    dot.node('memory_integration', 'Memory Integration\nSTM/LTM Object Tracking\nVision→Memory Binding', 
             fillcolor=integration_color, fontcolor='black')
    dot.node('concept_matching', 'Concept Matching\nSemantic Relationships\nKnowledge Base Lookup', 
             fillcolor=integration_color, fontcolor='black')
    
    # === OUTPUT LAYER ===
    dot.node('cognitive_rep', 'Cognitive Representation\nUnified Perceptual Model\nStructured Data', 
             fillcolor=output_color, fontcolor='black')
    dot.node('judgment_input', 'Judgment System Input\nReady for Evaluation\nDecision Making', 
             fillcolor=output_color, fontcolor='black')
    
    # === EDGES: INPUT TO VISION PIPELINE ===
    dot.edge('vision', 'vision_transport', label='Vision Events', color='blue')
    dot.edge('vision_transport', 'vision_dedup', label='Filtered Events', color='blue')
    dot.edge('vision_dedup', 'vision_stabilization', label='Unique Events', color='blue')
    dot.edge('vision_stabilization', 'vision_analysis', label='Stabilized Data', color='blue')
    
    # === EDGES: INPUT TO PROCESSING ===
    dot.edge('speech', 'intent_class', label='Audio Signal', color='green')
    dot.edge('text', 'intent_class', label='Text Input', color='green')
    dot.edge('motion', 'context_aware', label='Motion Data', color='orange')
    
    # === EDGES: VISION TO PROCESSING ===
    dot.edge('vision_analysis', 'context_aware', label='Visual Context', color='purple')
    dot.edge('vision_analysis', 'personality', label='Visual Input', color='purple')
    
    # === EDGES: PROCESSING TO INTEGRATION ===
    dot.edge('intent_class', 'cross_ref', label='Identified Intent', color='red')
    dot.edge('context_aware', 'cross_ref', label='Contextual Data', color='red')
    dot.edge('personality', 'cross_ref', label='Personality Impact', color='red')
    dot.edge('aiml_reflex', 'cross_ref', label='Reflex Response', color='red', style='dashed')
    
    # === EDGES: INTEGRATION LAYER ===
    dot.edge('cross_ref', 'memory_integration', label='Cross-Referenced Data', color='darkgreen')
    dot.edge('memory_integration', 'concept_matching', label='Memory Context', color='darkgreen')
    dot.edge('vision_analysis', 'memory_integration', label='Vision Detections', color='darkgreen')
    
    # === EDGES: INTEGRATION TO OUTPUT ===
    dot.edge('concept_matching', 'cognitive_rep', label='Integrated Knowledge', color='darkblue')
    dot.edge('cross_ref', 'cognitive_rep', label='Structured Data', color='darkblue')
    dot.edge('cognitive_rep', 'judgment_input', label='Perception Complete', color='darkblue', style='bold')
    
    # === SUBGRAPHS FOR GROUPING ===
    with dot.subgraph(name='cluster_inputs') as inputs:
        inputs.attr(label='Multi-Modal Input Sources', style='dashed', color='gray')
        inputs.node('speech')
        inputs.node('vision')
        inputs.node('motion')
        inputs.node('text')
    
    with dot.subgraph(name='cluster_vision') as vision:
        vision.attr(label='Vision Processing Pipeline', style='dashed', color='blue')
        vision.node('vision_transport')
        vision.node('vision_dedup')
        vision.node('vision_stabilization')
        vision.node('vision_analysis')
    
    with dot.subgraph(name='cluster_processing') as processing:
        processing.attr(label='Perception Processing', style='dashed', color='orange')
        processing.node('intent_class')
        processing.node('context_aware')
        processing.node('personality')
        processing.node('aiml_reflex')
    
    with dot.subgraph(name='cluster_integration') as integration:
        integration.attr(label='Knowledge Integration', style='dashed', color='green')
        integration.node('cross_ref')
        integration.node('memory_integration')
        integration.node('concept_matching')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Render
    dot.render(output_path.replace('.png', ''), cleanup=True)
    print(f"Flowchart saved to: {output_path}")
    return output_path

def create_perception_flowchart_matplotlib(output_path="docs/CARL_Perception_Mechanisms_Flowchart.png"):
    """Create comprehensive flowchart using matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(24, 18))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Color scheme
    input_color = '#E3F2FD'  # Light blue
    vision_color = '#BBDEFB'  # Medium blue for vision pipeline
    process_color = '#FFF3E0'  # Light orange
    personality_color = '#FFE0B2'  # Light amber for personality
    integration_color = '#E8F5E9'  # Light green
    output_color = '#F3E5F5'  # Light purple
    
    # Define positions (x, y, width, height)
    boxes = {
        # === INPUT LAYER (y=20) ===
        'speech': (2, 20, 3.5, 1.2),
        'vision': (6.5, 20, 3.5, 1.2),
        'motion': (11, 20, 3.5, 1.2),
        'text': (15.5, 20, 3.5, 1.2),
        
        # === VISION PIPELINE (y=17) ===
        'vision_transport': (2, 17, 3, 1),
        'vision_dedup': (6, 17, 3, 1),
        'vision_stabilization': (10, 17, 3, 1),
        'vision_analysis': (14, 17, 3, 1),
        
        # === PERCEPTION PROCESSING (y=14) ===
        'intent_class': (2, 14, 3.5, 1),
        'context_aware': (6.5, 14, 3.5, 1),
        'personality': (11, 14, 3.5, 1),
        'aiml_reflex': (15.5, 14, 3.5, 1),
        
        # === PERSONALITY FUNCTIONS DETAIL (y=11) ===
        'extroversion': (9, 11, 2.5, 0.8),
        'introversion': (12, 11, 2.5, 0.8),
        'sensation': (9, 10, 2.5, 0.8),
        'intuition': (12, 10, 2.5, 0.8),
        
        # === INTEGRATION LAYER (y=7) ===
        'cross_ref': (3, 7, 4, 1.2),
        'memory_integration': (9, 7, 4, 1.2),
        'concept_matching': (15, 7, 4, 1.2),
        
        # === MEMORY DETAILS (y=4.5) ===
        'stm': (7, 4.5, 2.5, 0.8),
        'ltm': (11, 4.5, 2.5, 0.8),
        
        # === OUTPUT LAYER (y=2) ===
        'cognitive_rep': (6, 2, 5, 1),
        'judgment_input': (14, 2, 5, 1),
    }
    
    # Draw boxes with appropriate colors
    for name, (x, y, w, h) in boxes.items():
        # Determine color
        if name in ['speech', 'text']:
            color = input_color
        elif name in ['vision', 'motion']:
            color = input_color
        elif name in ['vision_transport', 'vision_dedup', 'vision_stabilization', 'vision_analysis']:
            color = vision_color
        elif name in ['intent_class', 'context_aware', 'aiml_reflex']:
            color = process_color
        elif name in ['personality', 'extroversion', 'introversion', 'sensation', 'intuition']:
            color = personality_color
        elif name in ['cross_ref', 'memory_integration', 'concept_matching', 'stm', 'ltm']:
            color = integration_color
        else:
            color = output_color
        
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                             boxstyle="round,pad=0.1", 
                             facecolor=color, 
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        
        # Add text with detailed labels
        labels = {
            'speech': 'Speech Recognition\n(Flask Server)\nReal-time Audio',
            'vision': 'Vision Processing\n(ARC Camera)\nObject/Face/Color',
            'motion': 'Motion Detection\n(Exploration System)\nDynamic Enable/Disable',
            'text': 'Text Input\nDirect Entry',
            'vision_transport': 'Vision Transport\nExponential Backoff\nCircuit Breaker',
            'vision_dedup': 'Deduplication\nTTL-based Cache\nPrevents Spam',
            'vision_stabilization': 'Stabilization\nNoise Reduction\nTemporal Smoothing',
            'vision_analysis': 'Vision Analysis\n(OpenAI Vision API)\nObject/Danger/Pleasure',
            'intent_class': 'Intent Classification\n(OpenAI)\nSpeech Act Detection',
            'context_aware': 'Context Awareness\nConversation History\nEmotional State',
            'personality': 'Personality Functions\n(40% Processing)\nMBTI Cognitive Stack',
            'aiml_reflex': 'AIML Reflex Layer\nPattern Matching\nFast Response',
            'extroversion': 'Extroversion\nEnergy for Interaction',
            'introversion': 'Introversion\nEnergy for Personal Goals',
            'sensation': 'Sensation\nConcrete Details',
            'intuition': 'Intuition\nBig Picture Patterns',
            'cross_ref': 'Cross-Referencing\nNeeds, Goals, Skills\nConcepts Integration',
            'memory_integration': 'Memory Integration\nVision→Memory Binding\nObject Tracking',
            'concept_matching': 'Concept Matching\nSemantic Relationships\nKnowledge Base',
            'stm': 'Short-Term Memory\nRecent Objects',
            'ltm': 'Long-Term Memory\nPersistent Knowledge',
            'cognitive_rep': 'Cognitive Representation\nUnified Perceptual Model\nStructured Data',
            'judgment_input': 'Judgment System Input\nReady for Evaluation\nDecision Making',
        }
        
        ax.text(x, y, labels.get(name, name), 
               ha='center', va='center', 
               fontsize=7.5, weight='bold',
               wrap=True)
    
    # Draw arrows with labels
    arrows = [
        # Vision pipeline (sequential)
        ('vision', 'vision_transport', 'Vision Events', 'blue'),
        ('vision_transport', 'vision_dedup', 'Filtered', 'blue'),
        ('vision_dedup', 'vision_stabilization', 'Unique', 'blue'),
        ('vision_stabilization', 'vision_analysis', 'Stabilized', 'blue'),
        
        # Input to processing
        ('speech', 'intent_class', 'Audio Signal', 'green'),
        ('text', 'intent_class', 'Text', 'green'),
        ('motion', 'context_aware', 'Motion Data', 'orange'),
        ('vision_analysis', 'context_aware', 'Visual Context', 'purple'),
        ('vision_analysis', 'personality', 'Visual Input', 'purple'),
        
        # Personality functions detail
        ('personality', 'extroversion', '', 'darkorange'),
        ('personality', 'introversion', '', 'darkorange'),
        ('personality', 'sensation', '', 'darkorange'),
        ('personality', 'intuition', '', 'darkorange'),
        
        # Processing to integration
        ('intent_class', 'cross_ref', 'Intent', 'red'),
        ('context_aware', 'cross_ref', 'Context', 'red'),
        ('extroversion', 'cross_ref', 'Personality', 'darkorange'),
        ('introversion', 'cross_ref', '', 'darkorange'),
        ('sensation', 'cross_ref', '', 'darkorange'),
        ('intuition', 'cross_ref', '', 'darkorange'),
        ('aiml_reflex', 'cross_ref', 'Reflex', 'red'),
        
        # Integration flow
        ('cross_ref', 'memory_integration', 'Cross-Ref Data', 'darkgreen'),
        ('vision_analysis', 'memory_integration', 'Vision Detections', 'darkgreen'),
        ('memory_integration', 'stm', 'STM', 'darkgreen'),
        ('memory_integration', 'ltm', 'LTM', 'darkgreen'),
        ('memory_integration', 'concept_matching', 'Memory Context', 'darkgreen'),
        
        # To output
        ('concept_matching', 'cognitive_rep', 'Knowledge', 'darkblue'),
        ('cross_ref', 'cognitive_rep', 'Structured', 'darkblue'),
        ('cognitive_rep', 'judgment_input', 'Perception Complete', 'darkblue'),
    ]
    
    for start, end, label, color in arrows:
        x1, y1 = boxes[start][0], boxes[start][1] - boxes[start][3]/2
        x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        # Adjust arrow positions for better flow
        if start == 'personality' and end in ['extroversion', 'introversion', 'sensation', 'intuition']:
            # Horizontal arrows from personality
            if end == 'extroversion':
                x1, y1 = boxes[start][0] - boxes[start][2]/2, boxes[start][1] - 0.2
                x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
            elif end == 'introversion':
                x1, y1 = boxes[start][0] + boxes[start][2]/2, boxes[start][1] - 0.2
                x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
            elif end == 'sensation':
                x1, y1 = boxes[start][0] - boxes[start][2]/2, boxes[start][1] - 0.2
                x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
            elif end == 'intuition':
                x1, y1 = boxes[start][0] + boxes[start][2]/2, boxes[start][1] - 0.2
                x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', 
                               mutation_scale=25,
                               color=color,
                               linewidth=2,
                               alpha=0.8,
                               connectionstyle="arc3,rad=0.1" if abs(x2-x1) > 1 else None)
        ax.add_patch(arrow)
        
        # Add label for important arrows
        if label and label not in ['', 'Personality']:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y - 0.3, label, 
                   ha='center', va='top',
                   fontsize=6, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add title
    ax.text(12, 21.5, "CARL's Perception Mechanisms - Cognitive Architecture", 
           ha='center', va='center',
           fontsize=18, weight='bold')
    
    # Add subtitle
    ax.text(12, 21, "Multi-Modal Input → Processing → Integration → Cognitive Representation", 
           ha='center', va='center',
           fontsize=11, style='italic', color='gray')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=input_color, label='Input Sources', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=vision_color, label='Vision Pipeline', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=process_color, label='Processing', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=personality_color, label='Personality Functions', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=integration_color, label='Integration', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=output_color, label='Output', edgecolor='black', linewidth=1.5),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Flowchart saved to: {output_path}")
    plt.close()
    return output_path

if __name__ == "__main__":
    output_path = "docs/CARL_Perception_Mechanisms_Flowchart.png"
    
    if GRAPHVIZ_AVAILABLE:
        try:
            create_perception_flowchart_graphviz(output_path)
        except Exception as e:
            print(f"Graphviz failed: {e}")
            print("Falling back to matplotlib...")
            create_perception_flowchart_matplotlib(output_path)
    else:
        print("Using matplotlib (graphviz not available)...")
        create_perception_flowchart_matplotlib(output_path)

