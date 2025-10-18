"""Voxel addon UI panels for Blender."""

import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty


class VOXEL_PT_main_panel(Panel):
    """Main Voxel panel in the 3D viewport sidebar."""
    
    bl_label = "Voxel"
    bl_idname = "VOXEL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Voxel'
    
    def draw(self, context):
        """Draw the main panel."""
        layout = self.layout
        
        # Scene properties
        scene = context.scene
        
        # Prompt input
        layout.label(text="Scene Description:")
        layout.prop(scene, "voxel_prompt", text="")
        
        # Generation options
        layout.separator()
        layout.label(text="Generation Options:")
        
        col = layout.column(align=True)
        col.prop(scene, "voxel_enable_rigging", text="Enable Rigging")
        col.prop(scene, "voxel_enable_compositing", text="Enable Compositing")
        col.prop(scene, "voxel_enable_sequence", text="Enable Video Sequence")
        col.prop(scene, "voxel_enable_rag", text="Enable RAG Enhancement")
        
        # Generation buttons
        layout.separator()
        layout.label(text="Generate Scene:")
        
        col = layout.column(align=True)
        col.operator("voxel.generate_scene", text="Generate Basic Scene", icon='MESH_CUBE')
        
        if scene.voxel_enable_rigging:
            col.operator("voxel.generate_with_rigging", text="Generate with Rigging", icon='ARMATURE_DATA')
        
        if scene.voxel_enable_compositing:
            col.operator("voxel.generate_with_compositing", text="Generate with Effects", icon='COMPOSITE')
        
        if scene.voxel_enable_sequence:
            col.operator("voxel.generate_sequence", text="Generate Video Sequence", icon='SEQUENCE')
        
        # Utility buttons
        layout.separator()
        layout.label(text="Utilities:")
        
        col = layout.column(align=True)
        col.operator("voxel.clear_scene", text="Clear Scene", icon='TRASH')
        col.operator("voxel.config_check", text="Check Configuration", icon='PREFERENCES')


class VOXEL_PT_advanced_panel(Panel):
    """Advanced Voxel panel with more options."""
    
    bl_label = "Advanced Options"
    bl_idname = "VOXEL_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Voxel'
    bl_parent_id = "VOXEL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        """Draw the advanced panel."""
        layout = self.layout
        scene = context.scene
        
        # Render settings
        layout.label(text="Render Settings:")
        col = layout.column(align=True)
        col.prop(scene, "voxel_render_samples", text="Samples")
        col.prop(scene, "voxel_render_engine", text="Engine")
        
        # Animation settings
        layout.separator()
        layout.label(text="Animation Settings:")
        col = layout.column(align=True)
        col.prop(scene, "voxel_animation_frames", text="Frames")
        col.prop(scene, "voxel_animation_fps", text="FPS")
        
        # Quality settings
        layout.separator()
        layout.label(text="Quality Settings:")
        col = layout.column(align=True)
        col.prop(scene, "voxel_quality_level", text="Quality")
        col.prop(scene, "voxel_max_iterations", text="Max Iterations")


class VOXEL_PT_status_panel(Panel):
    """Status panel showing generation progress and results."""
    
    bl_label = "Status"
    bl_idname = "VOXEL_PT_status_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Voxel'
    bl_parent_id = "VOXEL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        """Draw the status panel."""
        layout = self.layout
        scene = context.scene
        
        # Status information
        layout.label(text="Last Generation:")
        
        if hasattr(scene, 'voxel_last_status'):
            status = scene.voxel_last_status
            if status == 'success':
                layout.label(text="✓ Success", icon='CHECKMARK')
            elif status == 'error':
                layout.label(text="✗ Error", icon='ERROR')
            else:
                layout.label(text="⏳ Processing...", icon='TIME')
        
        # Output information
        if hasattr(scene, 'voxel_last_output'):
            output = scene.voxel_last_output
            layout.label(text=f"Output: {output}")


# Scene properties
class VOXEL_SceneProperties(PropertyGroup):
    """Scene properties for Voxel addon."""
    
    # Main prompt
    voxel_prompt: StringProperty(
        name="Scene Prompt",
        description="Describe the scene you want to generate",
        default="",
        maxlen=1000
    )
    
    # Generation options
    voxel_enable_rigging: BoolProperty(
        name="Enable Rigging",
        description="Enable rigging agent for character/object rigs",
        default=False
    )
    
    voxel_enable_compositing: BoolProperty(
        name="Enable Compositing",
        description="Enable compositing agent for post-processing effects",
        default=False
    )
    
    voxel_enable_sequence: BoolProperty(
        name="Enable Video Sequence",
        description="Enable sequence agent for video editing",
        default=False
    )
    
    voxel_enable_rag: BoolProperty(
        name="Enable RAG",
        description="Enable RAG system for pattern-based enhancement",
        default=False
    )
    
    # Render settings
    voxel_render_samples: bpy.props.IntProperty(
        name="Render Samples",
        description="Number of render samples",
        default=128,
        min=1,
        max=4096
    )
    
    voxel_render_engine: EnumProperty(
        name="Render Engine",
        description="Render engine to use",
        items=[
            ('CYCLES', 'Cycles', 'Cycles render engine'),
            ('EEVEE', 'Eevee', 'Eevee render engine'),
        ],
        default='CYCLES'
    )
    
    # Animation settings
    voxel_animation_frames: bpy.props.IntProperty(
        name="Animation Frames",
        description="Number of animation frames",
        default=180,
        min=1,
        max=10000
    )
    
    voxel_animation_fps: bpy.props.IntProperty(
        name="Animation FPS",
        description="Animation frames per second",
        default=24,
        min=1,
        max=120
    )
    
    # Quality settings
    voxel_quality_level: EnumProperty(
        name="Quality Level",
        description="Generation quality level",
        items=[
            ('LOW', 'Low', 'Fast generation, lower quality'),
            ('MEDIUM', 'Medium', 'Balanced quality and speed'),
            ('HIGH', 'High', 'High quality, slower generation'),
        ],
        default='MEDIUM'
    )
    
    voxel_max_iterations: bpy.props.IntProperty(
        name="Max Iterations",
        description="Maximum refinement iterations",
        default=3,
        min=1,
        max=10
    )
    
    # Status properties
    voxel_last_status: StringProperty(
        name="Last Status",
        description="Status of last generation",
        default=""
    )
    
    voxel_last_output: StringProperty(
        name="Last Output",
        description="Output path of last generation",
        default=""
    )


# Panel classes list
panel_classes = [
    VOXEL_PT_main_panel,
    VOXEL_PT_advanced_panel,
    VOXEL_PT_status_panel,
    VOXEL_SceneProperties,
]


def register():
    """Register all panels and properties."""
    for cls in panel_classes:
        bpy.utils.register_class(cls)
    
    # Register scene properties
    bpy.types.Scene.voxel_prompt = bpy.props.StringProperty(
        name="Scene Prompt",
        description="Describe the scene you want to generate",
        default="",
        maxlen=1000
    )
    bpy.types.Scene.voxel_enable_rigging = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.voxel_enable_compositing = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.voxel_enable_sequence = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.voxel_enable_rag = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.voxel_render_samples = bpy.props.IntProperty(default=128, min=1, max=4096)
    bpy.types.Scene.voxel_render_engine = bpy.props.EnumProperty(
        items=[('CYCLES', 'Cycles', ''), ('EEVEE', 'Eevee', '')],
        default='CYCLES'
    )
    bpy.types.Scene.voxel_animation_frames = bpy.props.IntProperty(default=180, min=1, max=10000)
    bpy.types.Scene.voxel_animation_fps = bpy.props.IntProperty(default=24, min=1, max=120)
    bpy.types.Scene.voxel_quality_level = bpy.props.EnumProperty(
        items=[('LOW', 'Low', ''), ('MEDIUM', 'Medium', ''), ('HIGH', 'High', '')],
        default='MEDIUM'
    )
    bpy.types.Scene.voxel_max_iterations = bpy.props.IntProperty(default=3, min=1, max=10)
    bpy.types.Scene.voxel_last_status = bpy.props.StringProperty(default="")
    bpy.types.Scene.voxel_last_output = bpy.props.StringProperty(default="")


def unregister():
    """Unregister all panels and properties."""
    # Unregister scene properties
    del bpy.types.Scene.voxel_prompt
    del bpy.types.Scene.voxel_enable_rigging
    del bpy.types.Scene.voxel_enable_compositing
    del bpy.types.Scene.voxel_enable_sequence
    del bpy.types.Scene.voxel_enable_rag
    del bpy.types.Scene.voxel_render_samples
    del bpy.types.Scene.voxel_render_engine
    del bpy.types.Scene.voxel_animation_frames
    del bpy.types.Scene.voxel_animation_fps
    del bpy.types.Scene.voxel_quality_level
    del bpy.types.Scene.voxel_max_iterations
    del bpy.types.Scene.voxel_last_status
    del bpy.types.Scene.voxel_last_output
    
    # Unregister panels
    for cls in reversed(panel_classes):
        bpy.utils.unregister_class(cls)
