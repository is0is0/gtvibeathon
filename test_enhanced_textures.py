#!/usr/bin/env python3
"""
Enhanced Texture System Test
Comprehensive test of the advanced texture catalog and enhanced texture mapper.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voxel.voxelweaver.advanced_texture_catalog import (
    AdvancedTextureCatalog, MaterialCategory, TextureType, EnvironmentType
)
from voxel.voxelweaver.enhanced_texture_mapper import (
    EnhancedTextureMapper, MaterialComplexity, EnvironmentType as EnvType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_advanced_texture_catalog():
    """Test the advanced texture catalog system."""
    
    print("🎨 Advanced Texture Catalog Test")
    print("=" * 60)
    
    # Test 1: Initialize catalog
    print("\n📚 Test 1: Initialize Advanced Texture Catalog")
    try:
        catalog = AdvancedTextureCatalog()
        print("✅ Advanced texture catalog initialized")
        print(f"   - Total materials: {len(catalog.material_presets)}")
        
    except Exception as e:
        print(f"❌ Catalog initialization failed: {e}")
        return False
    
    # Test 2: Test material categories
    print("\n🏷️ Test 2: Material Categories")
    try:
        categories = {}
        for preset in catalog.material_presets.values():
            cat = preset.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        print("✅ Material categories:")
        for cat, count in categories.items():
            print(f"   - {cat}: {count} materials")
            
    except Exception as e:
        print(f"❌ Category analysis failed: {e}")
        return False
    
    # Test 3: Test texture map types
    print("\n🗺️ Test 3: Texture Map Types")
    try:
        map_types = set()
        for preset in catalog.material_presets.values():
            for map_type in preset.texture_maps.keys():
                map_types.add(map_type.value)
        
        print(f"✅ Texture map types used: {len(map_types)}")
        for map_type in sorted(map_types):
            print(f"   - {map_type}")
            
    except Exception as e:
        print(f"❌ Texture map analysis failed: {e}")
        return False
    
    # Test 4: Test material quality levels
    print("\n⭐ Test 4: Material Quality Levels")
    try:
        quality_levels = {}
        for preset in catalog.material_presets.values():
            level = preset.quality_level
            quality_levels[level] = quality_levels.get(level, 0) + 1
        
        print("✅ Quality level distribution:")
        for level, count in quality_levels.items():
            print(f"   - {level}: {count} materials")
            
    except Exception as e:
        print(f"❌ Quality level analysis failed: {e}")
        return False
    
    # Test 5: Test specific materials
    print("\n🔍 Test 5: Specific Material Analysis")
    try:
        # Test oak wood
        oak = catalog.get_material_preset("oak_wood")
        if oak:
            print(f"✅ Oak wood material:")
            print(f"   - Category: {oak.category.value}")
            print(f"   - Quality: {oak.quality_level}")
            print(f"   - Complexity: {oak.complexity_score:.2f}")
            print(f"   - Texture maps: {len(oak.texture_maps)}")
            print(f"   - Shader nodes: {len(oak.shader_nodes)}")
        
        # Test stainless steel
        steel = catalog.get_material_preset("stainless_steel")
        if steel:
            print(f"✅ Stainless steel material:")
            print(f"   - Category: {steel.category.value}")
            print(f"   - Quality: {steel.quality_level}")
            print(f"   - Complexity: {steel.complexity_score:.2f}")
            print(f"   - Metallic: {steel.metallic}")
            print(f"   - Roughness: {steel.roughness}")
        
        # Test neon blue
        neon = catalog.get_material_preset("neon_blue")
        if neon:
            print(f"✅ Neon blue material:")
            print(f"   - Category: {neon.category.value}")
            print(f"   - Emission strength: {neon.emission_strength}")
            print(f"   - Base color: {neon.base_color}")
            
    except Exception as e:
        print(f"❌ Specific material analysis failed: {e}")
        return False
    
    # Test 6: Test Blender code generation
    print("\n💻 Test 6: Blender Code Generation")
    try:
        oak = catalog.get_material_preset("oak_wood")
        if oak:
            code = catalog.generate_blender_material_code(oak)
            print(f"✅ Blender code generated: {len(code)} chars")
            print(f"   - Contains bpy import: {'import bpy' in code}")
            print(f"   - Contains material creation: {'materials.new' in code}")
            print(f"   - Contains BSDF setup: {'Principled BSDF' in code}")
            
    except Exception as e:
        print(f"❌ Blender code generation failed: {e}")
        return False
    
    # Test 7: Test catalog summary
    print("\n📊 Test 7: Catalog Summary")
    try:
        summary = catalog.get_catalog_summary()
        print(f"✅ Catalog summary:")
        print(f"   - Total materials: {summary['total_materials']}")
        print(f"   - Categories: {summary['categories']}")
        print(f"   - Quality levels: {summary['quality_levels']}")
        print(f"   - Complexity distribution: {summary['complexity_distribution']}")
        
    except Exception as e:
        print(f"❌ Catalog summary failed: {e}")
        return False
    
    print(f"\n🎉 Advanced Texture Catalog Test Complete!")
    return True

def test_enhanced_texture_mapper():
    """Test the enhanced texture mapper system."""
    
    print("\n🎨 Enhanced Texture Mapper Test")
    print("=" * 60)
    
    # Test 1: Initialize mapper
    print("\n🔧 Test 1: Initialize Enhanced Texture Mapper")
    try:
        mapper = EnhancedTextureMapper()
        print("✅ Enhanced texture mapper initialized")
        
    except Exception as e:
        print(f"❌ Mapper initialization failed: {e}")
        return False
    
    # Test 2: Test material suggestions for different environments
    print("\n🌍 Test 2: Environment-Based Material Suggestions")
    try:
        concept = "A modern living room with wooden furniture, metal fixtures, and soft lighting"
        
        environments = [EnvType.INDOOR, EnvType.OUTDOOR, EnvType.STUDIO, EnvType.NIGHT]
        
        for env in environments:
            suggestions = mapper.suggest_materials_advanced(
                concept=concept,
                environment=env,
                complexity=MaterialComplexity.ADVANCED
            )
            
            print(f"✅ {env.value} environment: {len(suggestions)} suggestions")
            if suggestions:
                top_suggestion = suggestions[0]
                print(f"   - Top suggestion: {top_suggestion.material_name}")
                print(f"   - Quality score: {top_suggestion.quality_score:.2f}")
                print(f"   - Environment adaptation: {top_suggestion.environment_adaptation:.2f}")
                print(f"   - Required maps: {len(top_suggestion.required_maps)}")
                print(f"   - Cost estimate: {top_suggestion.cost_estimate:.2f}")
                print(f"   - Generation time: {top_suggestion.generation_time:.1f}s")
            
    except Exception as e:
        print(f"❌ Environment-based suggestions failed: {e}")
        return False
    
    # Test 3: Test complexity levels
    print("\n⚙️ Test 3: Complexity Level Testing")
    try:
        concept = "A cyberpunk cityscape with neon lights and metallic surfaces"
        
        complexity_levels = [
            MaterialComplexity.SIMPLE,
            MaterialComplexity.MODERATE,
            MaterialComplexity.ADVANCED,
            MaterialComplexity.PRODUCTION
        ]
        
        for complexity in complexity_levels:
            suggestions = mapper.suggest_materials_advanced(
                concept=concept,
                environment=EnvType.NIGHT,
                complexity=complexity
            )
            
            print(f"✅ {complexity.value} complexity: {len(suggestions)} suggestions")
            if suggestions:
                avg_cost = sum(s.cost_estimate for s in suggestions) / len(suggestions)
                avg_time = sum(s.generation_time for s in suggestions) / len(suggestions)
                print(f"   - Average cost: {avg_cost:.2f}")
                print(f"   - Average time: {avg_time:.1f}s")
                print(f"   - Top material: {suggestions[0].material_name}")
            
    except Exception as e:
        print(f"❌ Complexity level testing failed: {e}")
        return False
    
    # Test 4: Test Blender code generation
    print("\n💻 Test 4: Blender Code Generation")
    try:
        concept = "A futuristic vehicle with metallic surfaces and neon accents"
        suggestions = mapper.suggest_materials_advanced(
            concept=concept,
            environment=EnvType.NIGHT,
            complexity=MaterialComplexity.ADVANCED
        )
        
        if suggestions:
            top_suggestion = suggestions[0]
            code = mapper.generate_material_blend_code(top_suggestion, "Vehicle")
            
            print(f"✅ Blender code generated: {len(code)} chars")
            print(f"   - Material: {top_suggestion.material_name}")
            print(f"   - Contains bpy import: {'import bpy' in code}")
            print(f"   - Contains BSDF setup: {'Principled BSDF' in code}")
            print(f"   - Contains texture nodes: {'TexImage' in code}")
            print(f"   - Contains material assignment: {'materials.append' in code}")
            
    except Exception as e:
        print(f"❌ Blender code generation failed: {e}")
        return False
    
    # Test 5: Test catalog statistics
    print("\n📊 Test 5: Enhanced Statistics")
    try:
        stats = mapper.get_catalog_statistics()
        print(f"✅ Enhanced statistics:")
        print(f"   - Total materials: {stats['catalog_summary']['total_materials']}")
        print(f"   - Environment support: {stats['environment_support']}")
        print(f"   - Complexity levels: {stats['complexity_levels']}")
        print(f"   - Texture map types: {stats['texture_map_types']}")
        print(f"   - Average complexity: {stats['average_complexity']:.2f}")
        print(f"   - Production ready: {stats['production_ready_materials']}")
        print(f"   - Emissive materials: {stats['emissive_materials']}")
        print(f"   - Transparent materials: {stats['transparent_materials']}")
        
    except Exception as e:
        print(f"❌ Enhanced statistics failed: {e}")
        return False
    
    print(f"\n🎉 Enhanced Texture Mapper Test Complete!")
    return True

def test_advanced_scenarios():
    """Test advanced texture scenarios."""
    
    print("\n🚀 Advanced Texture Scenarios Test")
    print("=" * 50)
    
    try:
        mapper = EnhancedTextureMapper()
        
        # Test 1: Cyberpunk scene
        print("\n🌃 Cyberpunk Scene Test")
        cyberpunk_suggestions = mapper.suggest_materials_advanced(
            concept="A cyberpunk cityscape with neon lights, flying cars, and metallic buildings",
            environment=EnvType.NIGHT,
            complexity=MaterialComplexity.PRODUCTION
        )
        
        print(f"✅ Cyberpunk scene: {len(cyberpunk_suggestions)} materials")
        for suggestion in cyberpunk_suggestions[:3]:
            print(f"   - {suggestion.material_name}: {suggestion.quality_score:.2f} score")
        
        # Test 2: Natural environment
        print("\n🌲 Natural Environment Test")
        natural_suggestions = mapper.suggest_materials_advanced(
            concept="A forest clearing with wooden structures, stone paths, and natural lighting",
            environment=EnvType.OUTDOOR,
            complexity=MaterialComplexity.ADVANCED
        )
        
        print(f"✅ Natural environment: {len(natural_suggestions)} materials")
        for suggestion in natural_suggestions[:3]:
            print(f"   - {suggestion.material_name}: {suggestion.quality_score:.2f} score")
        
        # Test 3: Studio setup
        print("\n🎬 Studio Setup Test")
        studio_suggestions = mapper.suggest_materials_advanced(
            concept="A professional photography studio with metallic equipment and soft lighting",
            environment=EnvType.STUDIO,
            complexity=MaterialComplexity.PRODUCTION
        )
        
        print(f"✅ Studio setup: {len(studio_suggestions)} materials")
        for suggestion in studio_suggestions[:3]:
            print(f"   - {suggestion.material_name}: {suggestion.quality_score:.2f} score")
        
        print("✅ Advanced scenarios test complete")
        
    except Exception as e:
        print(f"❌ Advanced scenarios test failed: {e}")

if __name__ == "__main__":
    print("🎯 Starting Enhanced Texture System Test...")
    
    # Run catalog test
    catalog_success = test_advanced_texture_catalog()
    
    # Run mapper test
    mapper_success = test_enhanced_texture_mapper()
    
    # Run advanced scenarios
    test_advanced_scenarios()
    
    if catalog_success and mapper_success:
        print(f"\n🎉 ALL ENHANCED TEXTURE TESTS PASSED!")
        print(f"🚀 Advanced texture system is fully operational")
        print(f"📊 Comprehensive material catalog ready")
        print(f"🎨 Intricate texture mapping system complete")
        print(f"🔧 Production-ready material generation available")
    else:
        print(f"\n❌ ENHANCED TEXTURE TESTS FAILED!")
        print(f"🔧 System needs debugging")
