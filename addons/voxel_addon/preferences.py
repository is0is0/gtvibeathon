"""Voxel addon preferences for Blender."""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty


class VOXEL_AddonPreferences(AddonPreferences):
    """Voxel addon preferences."""
    
    bl_idname = __package__
    
    # API Keys
    anthropic_api_key: StringProperty(
        name="Anthropic API Key",
        description="Your Anthropic API key for Claude",
        default="",
        subtype='PASSWORD'
    )
    
    openai_api_key: StringProperty(
        name="OpenAI API Key",
        description="Your OpenAI API key for GPT models",
        default="",
        subtype='PASSWORD'
    )
    
    # AI Provider
    ai_provider: EnumProperty(
        name="AI Provider",
        description="Choose the AI provider to use",
        items=[
            ('anthropic', 'Anthropic Claude', 'Use Anthropic Claude models'),
            ('openai', 'OpenAI GPT', 'Use OpenAI GPT models'),
        ],
        default='anthropic'
    )
    
    # Model Selection
    ai_model: StringProperty(
        name="AI Model",
        description="AI model to use for generation",
        default="claude-3-5-sonnet-20241022"
    )
    
    # Blender Path
    blender_path: StringProperty(
        name="Blender Path",
        description="Path to Blender executable (if different from current)",
        default="",
        subtype='FILE_PATH'
    )
    
    # Output Settings
    output_directory: StringProperty(
        name="Output Directory",
        description="Directory to save generated scenes",
        default="",
        subtype='DIR_PATH'
    )
    
    # Agent Settings
    agent_temperature: bpy.props.FloatProperty(
        name="Agent Temperature",
        description="Creativity level for AI agents (0.0-1.0)",
        default=0.7,
        min=0.0,
        max=1.0
    )
    
    agent_max_tokens: IntProperty(
        name="Max Tokens",
        description="Maximum tokens per agent response",
        default=4000,
        min=100,
        max=8000
    )
    
    # Feature Toggles
    enable_reviewer: BoolProperty(
        name="Enable Reviewer",
        description="Enable automatic scene review and refinement",
        default=True
    )
    
    enable_animation: BoolProperty(
        name="Enable Animation",
        description="Enable animation generation by default",
        default=True
    )
    
    enable_physics: BoolProperty(
        name="Enable Physics",
        description="Enable physics simulation",
        default=False
    )
    
    enable_particles: BoolProperty(
        name="Enable Particles",
        description="Enable particle systems",
        default=False
    )
    
    enable_geometry_nodes: BoolProperty(
        name="Enable Geometry Nodes",
        description="Enable procedural geometry generation",
        default=False
    )
    
    # Render Settings
    default_render_samples: IntProperty(
        name="Default Render Samples",
        description="Default number of render samples",
        default=128,
        min=1,
        max=4096
    )
    
    default_render_engine: EnumProperty(
        name="Default Render Engine",
        description="Default render engine",
        items=[
            ('CYCLES', 'Cycles', 'Cycles render engine'),
            ('EEVEE', 'Eevee', 'Eevee render engine'),
        ],
        default='CYCLES'
    )
    
    # Animation Settings
    default_animation_frames: IntProperty(
        name="Default Animation Frames",
        description="Default number of animation frames",
        default=180,
        min=1,
        max=10000
    )
    
    default_animation_fps: IntProperty(
        name="Default Animation FPS",
        description="Default animation frames per second",
        default=24,
        min=1,
        max=120
    )
    
    # Logging
    log_level: EnumProperty(
        name="Log Level",
        description="Logging level for debugging",
        items=[
            ('DEBUG', 'Debug', 'Detailed debug information'),
            ('INFO', 'Info', 'General information'),
            ('WARNING', 'Warning', 'Warnings only'),
            ('ERROR', 'Error', 'Errors only'),
        ],
        default='INFO'
    )
    
    def draw(self, context):
        """Draw the preferences UI."""
        layout = self.layout
        
        # API Configuration
        layout.label(text="API Configuration:", icon='PREFERENCES')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "ai_provider")
        
        if self.ai_provider == 'anthropic':
            col.prop(self, "anthropic_api_key")
        else:
            col.prop(self, "openai_api_key")
        
        col.prop(self, "ai_model")
        
        # Blender Configuration
        layout.separator()
        layout.label(text="Blender Configuration:", icon='BLENDER')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "blender_path")
        col.prop(self, "output_directory")
        
        # Agent Settings
        layout.separator()
        layout.label(text="Agent Settings:", icon='MODIFIER')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "agent_temperature")
        col.prop(self, "agent_max_tokens")
        
        # Feature Toggles
        layout.separator()
        layout.label(text="Feature Toggles:", icon='SETTINGS')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "enable_reviewer")
        col.prop(self, "enable_animation")
        col.prop(self, "enable_physics")
        col.prop(self, "enable_particles")
        col.prop(self, "enable_geometry_nodes")
        
        # Render Settings
        layout.separator()
        layout.label(text="Render Settings:", icon='RENDER_RESULT')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "default_render_samples")
        col.prop(self, "default_render_engine")
        
        # Animation Settings
        layout.separator()
        layout.label(text="Animation Settings:", icon='ANIM')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "default_animation_frames")
        col.prop(self, "default_animation_fps")
        
        # Logging
        layout.separator()
        layout.label(text="Logging:", icon='CONSOLE')
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(self, "log_level")
        
        # Help
        layout.separator()
        layout.label(text="Help:", icon='HELP')
        box = layout.box()
        
        col = box.column(align=True)
        col.operator("voxel.config_check", text="Check Configuration", icon='CHECKMARK')
        
        # Save/Load buttons
        layout.separator()
        row = layout.row(align=True)
        row.operator("preferences.addon_show", text="Save Preferences", icon='SAVE_PREFS')
        row.operator("preferences.addon_show", text="Reset to Defaults", icon='LOOP_BACK')


def register():
    """Register preferences."""
    bpy.utils.register_class(VOXEL_AddonPreferences)


def unregister():
    """Unregister preferences."""
    bpy.utils.unregister_class(VOXEL_AddonPreferences)
