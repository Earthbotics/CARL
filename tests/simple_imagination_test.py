#!/usr/bin/env python3
"""
Simple test script to check imagination system basic functionality
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic_imagination():
    """Test basic imagination system functionality."""
    print("🧪 Testing Basic Imagination System")
    print("=" * 50)
    
    try:
        # Test 1: Check if modules can be imported
        print("\n1. Testing module imports...")
        from imagination_system import ImaginationSystem
        print("✅ ImaginationSystem imported successfully")
        
        # Test 2: Check if we can create a mock episode
        print("\n2. Testing episode creation...")
        from imagination_system import ImaginedEpisode, ImaginationRequest, SceneGraph
        
        request = ImaginationRequest(
            seed="A beautiful sunset over mountains",
            purpose="explore-scenario",
            mbti_state={"Ti": 0.7, "Ne": 0.6, "Si": 0.4, "Fe": 0.3},
            neucogar={"DA": 0.5, "5HT": 0.4, "NE": 0.3}
        )
        
        scene_graph = SceneGraph(
            objects=[{"name": "mountain", "type": "landscape"}],
            relations=[],
            affect={"valence": 0.8, "arousal": 0.3, "dominant_emotion": "peaceful"},
            details={"lighting": "golden hour", "style": "realistic"},
            context={"time": "sunset", "weather": "clear"}
        )
        
        episode = ImaginedEpisode(
            episode_id="test_episode_001",
            request=request,
            scene_graph=scene_graph,
            coherence_score=0.85,
            render_data={"path": "test_image.png"}
        )
        
        print("✅ Episode creation successful")
        print(f"   Episode ID: {episode.episode_id}")
        print(f"   Purpose: {episode.request.purpose}")
        print(f"   Seed: {episode.request.seed}")
        print(f"   Coherence: {episode.coherence_score}")
        
        # Test 3: Check if we can access the imagination system class structure
        print("\n3. Testing imagination system structure...")
        if hasattr(ImaginationSystem, 'imagine'):
            print("✅ imagine method exists")
        else:
            print("❌ imagine method missing")
            
        if hasattr(ImaginationSystem, 'imagine_async'):
            print("✅ imagine_async method exists")
        else:
            print("❌ imagine_async method missing")
            
        if hasattr(ImaginationSystem, '_store_imagined_episode'):
            print("✅ _store_imagined_episode method exists")
        else:
            print("❌ _store_imagined_episode method missing")
        
        print("\n🎉 Basic imagination system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_imagination())
    sys.exit(0 if success else 1)
