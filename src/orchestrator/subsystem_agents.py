"""
Subsystem Agents
----------------
Asynchronous agent wrappers for each subsystem.

Each agent wraps a subsystem and provides async message-based interface.
"""

import asyncio
from typing import Dict, Any, Optional
from orchestrator.agent_framework import AgentInterface, AgentResult
from utils.logger import get_logger

# Import subsystems
from subsystems.prompt_interpreter import PromptInterpreter
from subsystems.texture_synth import TextureSynthesizer
from subsystems.lighting_ai import LightingAI
from subsystems.spatial_validator import SpatialValidator
from subsystems.render_director import RenderDirector, RenderQuality, RenderEngine
from subsystems.asset_registry import AssetRegistry, StorageBackend

logger = get_logger(__name__)


class PromptInterpreterAgent(AgentInterface):
    """
    Agent for prompt interpretation using NLP.

    Handles:
    - Natural language parsing
    - Style extraction
    - Mood analysis
    - Relationship identification
    - Scene graph generation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize prompt interpreter agent."""
        super().__init__("prompt_interpreter", config)
        self.interpreter = PromptInterpreter(config=config)
        logger.info("Prompt Interpreter Agent initialized")

    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process prompt interpretation task.

        Args:
            data: Task data containing:
                - prompt: Natural language prompt
                - style: Optional style preference

        Returns:
            Agent result with interpreted prompt data
        """
        start_time = asyncio.get_event_loop().time()

        try:
            prompt = data.get('prompt', '')
            style = data.get('style', 'realistic')

            logger.info(f"Interpreting prompt: '{prompt}'")

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()

            # Parse prompt
            interpreted_data = await loop.run_in_executor(
                None,
                self.interpreter.parse_prompt,
                prompt
            )

            # Extract style
            style_info = await loop.run_in_executor(
                None,
                self.interpreter.extract_style,
                prompt,
                style
            )
            interpreted_data['style'] = style_info

            # Extract mood
            mood_info = await loop.run_in_executor(
                None,
                self.interpreter.extract_mood,
                prompt
            )
            interpreted_data['mood'] = mood_info

            # Analyze relationships
            relationships = await loop.run_in_executor(
                None,
                self.interpreter.analyze_relationships,
                interpreted_data['objects']
            )
            interpreted_data['relationships'] = relationships

            # Generate scene graph
            scene_graph = await loop.run_in_executor(
                None,
                self.interpreter.generate_scene_graph,
                interpreted_data
            )
            interpreted_data['scene_graph'] = scene_graph

            duration = asyncio.get_event_loop().time() - start_time

            logger.info(
                f"Prompt interpretation complete: "
                f"{len(interpreted_data.get('objects', []))} objects, "
                f"{len(relationships)} relationships"
            )

            return AgentResult(
                success=True,
                data=interpreted_data,
                duration=duration,
                metadata={
                    'num_objects': len(interpreted_data.get('objects', [])),
                    'num_relationships': len(relationships)
                }
            )

        except Exception as e:
            logger.error(f"Prompt interpretation failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


class TextureSynthAgent(AgentInterface):
    """
    Agent for texture synthesis and material application.

    Handles:
    - Advanced material creation
    - PBR texture generation
    - UV mapping optimization
    - Node-based shader networks
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize texture synth agent."""
        super().__init__("texture_synth", config)
        self.synthesizer = TextureSynthesizer(config=config)
        logger.info("Texture Synth Agent initialized")

    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process texture synthesis task.

        Args:
            data: Task data containing:
                - scene_data: Scene with geometry
                - style: Visual style

        Returns:
            Agent result with enhanced scene data
        """
        start_time = asyncio.get_event_loop().time()

        try:
            scene_data = data.get('scene_data', {})
            style = data.get('style', 'realistic')

            logger.info(f"Applying textures (style: {style})")

            # Run in executor
            loop = asyncio.get_event_loop()
            enhanced_scene = await loop.run_in_executor(
                None,
                self.synthesizer.apply,
                scene_data,
                style
            )

            duration = asyncio.get_event_loop().time() - start_time

            num_materials = len(enhanced_scene.get('materials', []))
            logger.info(f"Texture synthesis complete: {num_materials} materials")

            return AgentResult(
                success=True,
                data={'scene_data': enhanced_scene},
                duration=duration,
                metadata={'num_materials': num_materials}
            )

        except Exception as e:
            logger.error(f"Texture synthesis failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


class LightingAgent(AgentInterface):
    """
    Agent for intelligent lighting setup.

    Handles:
    - Scene analysis for lighting
    - HDRI environment maps
    - Three-point lighting
    - Dramatic/cinematic lighting
    - Light optimization
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize lighting agent."""
        super().__init__("lighting_ai", config)
        self.lighting = LightingAI(config=config)
        logger.info("Lighting Agent initialized")

    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process lighting setup task.

        Args:
            data: Task data containing:
                - scene_data: Scene with geometry and materials
                - style: Visual style

        Returns:
            Agent result with lit scene data
        """
        start_time = asyncio.get_event_loop().time()

        try:
            scene_data = data.get('scene_data', {})
            style = data.get('style', 'realistic')

            logger.info(f"Setting up lighting (style: {style})")

            # Run in executor
            loop = asyncio.get_event_loop()

            # Analyze scene
            await loop.run_in_executor(
                None,
                self.lighting.analyze_scene,
                scene_data
            )

            # Apply lighting
            lit_scene = await loop.run_in_executor(
                None,
                self.lighting.apply,
                scene_data,
                style
            )

            duration = asyncio.get_event_loop().time() - start_time

            num_lights = len(lit_scene.get('lighting', {}).get('lights', []))
            logger.info(f"Lighting setup complete: {num_lights} lights")

            return AgentResult(
                success=True,
                data={'scene_data': lit_scene},
                duration=duration,
                metadata={
                    'num_lights': num_lights,
                    'lighting_mode': lit_scene.get('lighting', {}).get('mode', 'N/A')
                }
            )

        except Exception as e:
            logger.error(f"Lighting setup failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


class SpatialValidatorAgent(AgentInterface):
    """
    Agent for spatial validation and physics checks.

    Handles:
    - Collision detection
    - Gravity and support validation
    - Overlap resolution
    - Spatial relationship validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize spatial validator agent."""
        super().__init__("spatial_validator", config)
        self.validator = SpatialValidator(config=config)
        logger.info("Spatial Validator Agent initialized")

    async def process_task(self, data: Dict[str, Any]) = > AgentResult:
        """
        Process spatial validation task.

        Args:
            data: Task data containing:
                - scene_data: Scene to validate
                - auto_fix: Whether to auto-fix issues

        Returns:
            Agent result with validated scene data
        """
        start_time = asyncio.get_event_loop().time()

        try:
            scene_data = data.get('scene_data', {})
            auto_fix = data.get('auto_fix', True)

            logger.info("Validating spatial relationships")

            # Run in executor
            loop = asyncio.get_event_loop()

            # Check validation
            validation_result = await loop.run_in_executor(
                None,
                self.validator.check,
                scene_data
            )

            # Apply fixes if needed
            if auto_fix and validation_result['report']['total_issues'] > 0:
                validated_scene = await loop.run_in_executor(
                    None,
                    self.validator.apply,
                    scene_data
                )
            else:
                validated_scene = scene_data

            duration = asyncio.get_event_loop().time() - start_time

            num_issues = validation_result['report']['total_issues']
            status = validation_result['status']

            logger.info(f"Spatial validation complete: {status}, {num_issues} issues")

            return AgentResult(
                success=True,
                data={'scene_data': validated_scene},
                duration=duration,
                metadata={
                    'validation_status': status,
                    'issues_found': num_issues,
                    'auto_fixed': auto_fix
                }
            )

        except Exception as e:
            logger.error(f"Spatial validation failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


class RenderDirectorAgent(AgentInterface):
    """
    Agent for render configuration and optimization.

    Handles:
    - Camera setup
    - Multi-angle rendering
    - Quality optimization
    - Format export (PNG, EXR, GLTF)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize render director agent."""
        super().__init__("render_director", config)
        self.director = RenderDirector(config=config)
        logger.info("Render Director Agent initialized")

    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process render configuration task.

        Args:
            data: Task data containing:
                - scene_data: Complete scene data
                - output_path: Output file path
                - quality: Render quality
                - format: Export format

        Returns:
            Agent result with render configuration
        """
        start_time = asyncio.get_event_loop().time()

        try:
            scene_data = data.get('scene_data', {})
            output_path = data.get('output_path', 'output/scene.blend')
            quality = data.get('quality', 'preview')
            file_format = data.get('format', 'blend')

            logger.info(f"Configuring render (quality: {quality}, format: {file_format})")

            # Run in executor
            loop = asyncio.get_event_loop()

            # Setup camera
            camera = await loop.run_in_executor(
                None,
                self.director.setup_camera,
                scene_data,
                "Camera",
                "perspective"
            )

            # Plan render
            render_plan = await loop.run_in_executor(
                None,
                self.director.plan_render,
                scene_data
            )

            # Configure render
            render_result = await loop.run_in_executor(
                None,
                self.director.render_scene,
                output_path,
                scene_data,
                (1920, 1080),
                RenderQuality(quality) if isinstance(quality, str) else quality
            )

            duration = asyncio.get_event_loop().time() - start_time

            logger.info(f"Render configuration complete: {output_path}")

            return AgentResult(
                success=True,
                data={
                    'render_result': render_result,
                    'render_plan': render_plan,
                    'camera': camera.__dict__
                },
                duration=duration,
                metadata={
                    'output_path': output_path,
                    'quality': quality,
                    'format': file_format
                }
            )

        except Exception as e:
            logger.error(f"Render configuration failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


class AssetRegistryAgent(AgentInterface):
    """
    Agent for asset management and registration.

    Handles:
    - Asset registration
    - Library management
    - Search and retrieval
    - Metadata management
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize asset registry agent."""
        super().__init__("asset_registry", config)

        # Determine storage backend
        backend = config.get('backend', 'json') if config else 'json'

        self.registry = AssetRegistry(
            storage_path=config.get('storage_path') if config else None,
            backend=StorageBackend(backend) if isinstance(backend, str) else backend
        )
        logger.info("Asset Registry Agent initialized")

    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process asset registry task.

        Args:
            data: Task data containing:
                - action: Action to perform (register, search, get)
                - assets: Assets to register (for register action)
                - query: Search query (for search action)
                - asset_id: Asset ID (for get action)

        Returns:
            Agent result with registry operation result
        """
        start_time = asyncio.get_event_loop().time()

        try:
            action = data.get('action', 'register')

            loop = asyncio.get_event_loop()

            if action == 'register':
                # Register assets
                assets = data.get('assets', [])
                registered = []

                for asset_data in assets:
                    asset = await loop.run_in_executor(
                        None,
                        self.registry.add_asset,
                        asset_data.get('name'),
                        asset_data.get('path'),
                        asset_data.get('asset_type'),
                        **{k: v for k, v in asset_data.items()
                           if k not in ['name', 'path', 'asset_type']}
                    )
                    registered.append(asset.asset_id)

                logger.info(f"Registered {len(registered)} assets")

                result_data = {'registered_assets': registered}

            elif action == 'search':
                # Search assets
                query = data.get('query', '')
                results = await loop.run_in_executor(
                    None,
                    self.registry.search_assets,
                    query
                )

                logger.info(f"Search '{query}' found {len(results)} assets")

                result_data = {
                    'results': [asset.to_dict() for asset in results]
                }

            elif action == 'get':
                # Get specific asset
                asset_id = data.get('asset_id', '')
                asset = await loop.run_in_executor(
                    None,
                    self.registry.get_asset,
                    asset_id
                )

                if asset:
                    result_data = {'asset': asset.to_dict()}
                else:
                    return AgentResult(
                        success=False,
                        error=f"Asset not found: {asset_id}"
                    )

            else:
                return AgentResult(
                    success=False,
                    error=f"Unknown action: {action}"
                )

            duration = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                success=True,
                data=result_data,
                duration=duration,
                metadata={'action': action}
            )

        except Exception as e:
            logger.error(f"Asset registry operation failed: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e)
            )


# Factory functions for easy agent creation
def create_all_agents(config: Optional[Dict[str, Any]] = None) -> Dict[str, AgentInterface]:
    """
    Create all subsystem agents.

    Args:
        config: Configuration dictionary with subsystem configs

    Returns:
        Dictionary mapping agent names to agent instances
    """
    config = config or {}
    subsystem_configs = config.get('subsystems', {})

    agents = {
        'prompt_interpreter': PromptInterpreterAgent(
            config=subsystem_configs.get('prompt_interpreter')
        ),
        'texture_synth': TextureSynthAgent(
            config=subsystem_configs.get('texture_synth')
        ),
        'lighting_ai': LightingAgent(
            config=subsystem_configs.get('lighting_ai')
        ),
        'spatial_validator': SpatialValidatorAgent(
            config=subsystem_configs.get('spatial_validator')
        ),
        'render_director': RenderDirectorAgent(
            config=subsystem_configs.get('render_director')
        ),
        'asset_registry': AssetRegistryAgent(
            config=subsystem_configs.get('asset_registry')
        )
    }

    logger.info(f"Created {len(agents)} subsystem agents")

    return agents


# Example usage
if __name__ == "__main__":
    from utils.logger import setup_logging
    from orchestrator.agent_framework import MessageBus

    setup_logging(level="INFO", console=True)

    async def test_subsystem_agents():
        """Test subsystem agents."""
        print("\n" + "="*80)
        print("SUBSYSTEM AGENTS TEST")
        print("="*80 + "\n")

        # Create message bus
        bus = MessageBus()

        # Create all agents
        agents = create_all_agents()

        # Register with bus
        for agent in agents.values():
            bus.register_agent(agent)

        # Start system
        await bus.start()
        print("✓ Agent system started\n")

        # Test prompt interpretation
        print("Test: Prompt Interpretation")
        prompt_agent = agents['prompt_interpreter']
        result = await prompt_agent.request(
            "prompt_interpreter",  # Send to self for testing
            {
                'prompt': 'A cozy bedroom with a lamp and desk',
                'style': 'realistic'
            }
        )

        if result.success:
            print(f"  ✓ Interpreted {result.metadata.get('num_objects', 0)} objects")
            print(f"  Duration: {result.duration:.2f}s\n")
        else:
            print(f"  ✗ Failed: {result.error}\n")

        # Get statistics
        print("System Statistics:")
        stats = bus.get_stats()
        print(f"  Total messages: {stats['total_messages']}")
        print(f"  Active agents: {stats['registered_agents']}\n")

        # Stop system
        await bus.stop()
        print("✓ Agent system stopped")

        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80 + "\n")

    asyncio.run(test_subsystem_agents())
