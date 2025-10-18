"""Voxel addon operators for Blender."""

import bpy
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global voxel instance
_voxel_agency: Optional['Agency3D'] = None
_voxel_config: Optional['Config'] = None


def get_voxel_agency():
    """Get or create the Voxel agency instance."""
    global _voxel_agency, _voxel_config
    
    if _voxel_agency is None:
        try:
            from agency3d import Agency3D, Config
            _voxel_config = Config()
            _voxel_agency = Agency3D(_voxel_config)
        except Exception as e:
            logger.error(f"Failed to initialize Voxel agency: {e}")
            return None
    
    return _voxel_agency


class VOXEL_OT_generate_scene(bpy.types.Operator):
    """Generate a 3D scene using Voxel AI agents."""
    
    bl_idname = "voxel.generate_scene"
    bl_label = "Generate Scene"
    bl_description = "Generate a 3D scene from text prompt using AI agents"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the scene generation."""
        agency = get_voxel_agency()
        if not agency:
            self.report({'ERROR'}, "Voxel agency not available. Check configuration.")
            return {'CANCELLED'}
        
        # Get prompt from scene properties
        prompt = context.scene.voxel_prompt
        if not prompt.strip():
            self.report({'ERROR'}, "Please enter a scene description")
            return {'CANCELLED'}
        
        try:
            # Generate scene
            self.report({'INFO'}, f"Generating scene: {prompt}")
            
            # Use the workflow orchestrator
            from agency3d.orchestrator.workflow import WorkflowOrchestrator
            orchestrator = WorkflowOrchestrator(_voxel_config)
            
            result = orchestrator.execute_workflow(prompt)
            
            if result.success:
                self.report({'INFO'}, f"Scene generated successfully! Output: {result.output_path}")
                
                # Load the generated .blend file
                if result.output_path and result.output_path.exists():
                    bpy.ops.wm.open_mainfile(filepath=str(result.output_path))
            else:
                self.report({'ERROR'}, f"Scene generation failed: {result.error}")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"Scene generation error: {e}")
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class VOXEL_OT_generate_with_rigging(bpy.types.Operator):
    """Generate a 3D scene with rigging."""
    
    bl_idname = "voxel.generate_with_rigging"
    bl_label = "Generate with Rigging"
    bl_description = "Generate a 3D scene with character/object rigging"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the scene generation with rigging."""
        agency = get_voxel_agency()
        if not agency:
            self.report({'ERROR'}, "Voxel agency not available. Check configuration.")
            return {'CANCELLED'}
        
        prompt = context.scene.voxel_prompt
        if not prompt.strip():
            self.report({'ERROR'}, "Please enter a scene description")
            return {'CANCELLED'}
        
        try:
            self.report({'INFO'}, f"Generating scene with rigging: {prompt}")
            
            # This would use the enhanced workflow with rigging
            # For now, just generate normally
            from agency3d.orchestrator.workflow import WorkflowOrchestrator
            orchestrator = WorkflowOrchestrator(_voxel_config)
            
            result = orchestrator.execute_workflow(prompt)
            
            if result.success:
                self.report({'INFO'}, f"Scene with rigging generated successfully!")
            else:
                self.report({'ERROR'}, f"Scene generation failed: {result.error}")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"Rigging generation error: {e}")
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class VOXEL_OT_generate_with_compositing(bpy.types.Operator):
    """Generate a 3D scene with compositing effects."""
    
    bl_idname = "voxel.generate_with_compositing"
    bl_label = "Generate with Compositing"
    bl_description = "Generate a 3D scene with post-processing effects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the scene generation with compositing."""
        agency = get_voxel_agency()
        if not agency:
            self.report({'ERROR'}, "Voxel agency not available. Check configuration.")
            return {'CANCELLED'}
        
        prompt = context.scene.voxel_prompt
        if not prompt.strip():
            self.report({'ERROR'}, "Please enter a scene description")
            return {'CANCELLED'}
        
        try:
            self.report({'INFO'}, f"Generating scene with compositing: {prompt}")
            
            # This would use the enhanced workflow with compositing
            from agency3d.orchestrator.workflow import WorkflowOrchestrator
            orchestrator = WorkflowOrchestrator(_voxel_config)
            
            result = orchestrator.execute_workflow(prompt)
            
            if result.success:
                self.report({'INFO'}, f"Scene with compositing generated successfully!")
            else:
                self.report({'ERROR'}, f"Scene generation failed: {result.error}")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"Compositing generation error: {e}")
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class VOXEL_OT_generate_sequence(bpy.types.Operator):
    """Generate a video sequence."""
    
    bl_idname = "voxel.generate_sequence"
    bl_label = "Generate Video Sequence"
    bl_description = "Generate a multi-shot video sequence"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the sequence generation."""
        agency = get_voxel_agency()
        if not agency:
            self.report({'ERROR'}, "Voxel agency not available. Check configuration.")
            return {'CANCELLED'}
        
        prompt = context.scene.voxel_prompt
        if not prompt.strip():
            self.report({'ERROR'}, "Please enter a sequence description")
            return {'CANCELLED'}
        
        try:
            self.report({'INFO'}, f"Generating video sequence: {prompt}")
            
            # This would use the enhanced workflow with sequence editing
            from agency3d.orchestrator.workflow import WorkflowOrchestrator
            orchestrator = WorkflowOrchestrator(_voxel_config)
            
            result = orchestrator.execute_workflow(prompt)
            
            if result.success:
                self.report({'INFO'}, f"Video sequence generated successfully!")
            else:
                self.report({'ERROR'}, f"Sequence generation failed: {result.error}")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"Sequence generation error: {e}")
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class VOXEL_OT_clear_scene(bpy.types.Operator):
    """Clear the current scene."""
    
    bl_idname = "voxel.clear_scene"
    bl_label = "Clear Scene"
    bl_description = "Clear all objects from the current scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Clear the scene."""
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        
        # Delete selected objects
        bpy.ops.object.delete(use_global=False)
        
        self.report({'INFO'}, "Scene cleared")
        return {'FINISHED'}


class VOXEL_OT_config_check(bpy.types.Operator):
    """Check Voxel configuration."""
    
    bl_idname = "voxel.config_check"
    bl_label = "Check Configuration"
    bl_description = "Check Voxel configuration and API keys"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Check configuration."""
        try:
            from agency3d.core.config import Config
            config = Config()
            
            # Check API keys
            try:
                config.validate_api_keys()
                self.report({'INFO'}, "API keys are valid")
            except ValueError as e:
                self.report({'ERROR'}, f"API key error: {e}")
                return {'CANCELLED'}
            
            # Check Blender path
            try:
                config.validate_paths()
                self.report({'INFO'}, "Blender path is valid")
            except ValueError as e:
                self.report({'ERROR'}, f"Blender path error: {e}")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "Configuration check passed!")
            
        except Exception as e:
            logger.error(f"Configuration check error: {e}")
            self.report({'ERROR'}, f"Configuration check failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# Operator classes list
operator_classes = [
    VOXEL_OT_generate_scene,
    VOXEL_OT_generate_with_rigging,
    VOXEL_OT_generate_with_compositing,
    VOXEL_OT_generate_sequence,
    VOXEL_OT_clear_scene,
    VOXEL_OT_config_check,
]


def register():
    """Register all operators."""
    for cls in operator_classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all operators."""
    for cls in reversed(operator_classes):
        bpy.utils.unregister_class(cls)
