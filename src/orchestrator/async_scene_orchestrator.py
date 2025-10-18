"""
Async Scene Orchestrator
------------------------
Asynchronous orchestration using message-passing agent system.

Coordinates all subsystems as independent agents communicating via message queues.
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from utils.logger import get_logger
from orchestrator.agent_framework import MessageBus, AgentResult
from orchestrator.subsystem_agents import create_all_agents

logger = get_logger(__name__)


class AsyncSceneOrchestrator:
    """
    Asynchronous scene orchestrator using agent-based architecture.

    Instead of sequential processing, agents can work concurrently and
    communicate via message passing for better performance and scalability.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize async scene orchestrator.

        Args:
            config: Configuration dictionary
        """
        print("\n" + "="*80)
        print("ASYNC VOXEL WEAVER - Scene Orchestrator Initialization")
        print("="*80)

        logger.info("Initializing Async Scene Orchestrator")

        self.config = config or {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(self.config.get('output_dir', 'output'))
        self.session_dir = self.output_dir / f"session_{self.session_id}"

        # Create output directories
        self.session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created session directory: {self.session_dir}")

        # Initialize message bus
        print("\n[1/2] Initializing Message Bus...")
        self.message_bus = MessageBus()
        print("  ✓ Message Bus ready")

        # Create all agents
        print("\n[2/2] Creating AI Agents...")
        self.agents = create_all_agents(config)

        # Register agents with bus
        for agent in self.agents.values():
            self.message_bus.register_agent(agent)
            print(f"  ✓ {agent.agent_name} registered")

        print("\n" + "="*80)
        print("All agents initialized and registered!")
        print("="*80 + "\n")

        logger.info("Async Scene Orchestrator initialization complete")

        # Pipeline state
        self.current_scene = None
        self.pipeline_state = {
            'prompt_analyzed': False,
            'geometry_generated': False,
            'textures_applied': False,
            'lighting_setup': False,
            'validation_passed': False,
            'render_configured': False
        }

    async def start(self):
        """Start the message bus and all agents."""
        await self.message_bus.start()
        logger.info("Agent system started")

    async def stop(self):
        """Stop all agents and message bus."""
        await self.message_bus.stop()
        logger.info("Agent system stopped")

    async def generate_complete_scene(
        self,
        prompt: str,
        style: str = "realistic",
        validate: bool = True,
        output_format: str = "blend"
    ) -> Dict[str, Any]:
        """
        Generate complete 3D scene using async agent system.

        Args:
            prompt: Natural language scene description
            style: Visual style
            validate: Whether to run spatial validation
            output_format: Output format

        Returns:
            Generation result dictionary
        """
        print("\n" + "="*80)
        print("STARTING ASYNC SCENE GENERATION PIPELINE")
        print("="*80)
        print(f"\nPrompt: '{prompt}'")
        print(f"Style: {style}")
        print(f"Validate: {validate}")
        print(f"Output Format: {output_format}")
        print("\n" + "-"*80 + "\n")

        logger.info(f"Starting async scene generation: {prompt}")

        try:
            # Start agent system
            await self.start()

            # Get agent references
            prompt_agent = self.agents['prompt_interpreter']
            texture_agent = self.agents['texture_synth']
            lighting_agent = self.agents['lighting_ai']
            validator_agent = self.agents['spatial_validator']
            render_agent = self.agents['render_director']
            registry_agent = self.agents['asset_registry']

            # Stage 1: Interpret Prompt
            print("\n[Stage 1/6] PROMPT INTERPRETATION")
            print("-" * 80)

            result = await prompt_agent.request(
                'prompt_interpreter',
                {'prompt': prompt, 'style': style},
                timeout=30.0
            )

            if not result.success:
                raise Exception(f"Prompt interpretation failed: {result.error}")

            interpreted_prompt = result.data
            self.pipeline_state['prompt_analyzed'] = True

            print(f"✓ Detected {result.metadata.get('num_objects', 0)} objects")
            print(f"✓ Found {result.metadata.get('num_relationships', 0)} relationships")
            print(f"  Duration: {result.duration:.2f}s")

            # Stage 2: Generate Geometry (would integrate with VoxelWeaver)
            print("\n[Stage 2/6] GEOMETRY GENERATION")
            print("-" * 80)
            print("⚠ VoxelWeaver integration (mock for demonstration)")

            # Mock geometry generation
            scene_data = {
                'interpreted_prompt': interpreted_prompt,
                'objects': interpreted_prompt.get('objects', []),
                'style': style,
                'materials': [],
                'lighting': {}
            }

            self.pipeline_state['geometry_generated'] = True
            print(f"✓ Generated {len(scene_data['objects'])} objects")

            # Stage 3 & 4: Apply Textures and Lighting (can run in parallel!)
            print("\n[Stages 3-4] TEXTURE & LIGHTING (Parallel Processing)")
            print("-" * 80)

            # Run texture and lighting agents concurrently
            texture_task = texture_agent.request(
                'texture_synth',
                {'scene_data': scene_data, 'style': style},
                timeout=60.0
            )

            lighting_task = lighting_agent.request(
                'lighting_ai',
                {'scene_data': scene_data, 'style': style},
                timeout=60.0
            )

            # Wait for both to complete
            texture_result, lighting_result = await asyncio.gather(
                texture_task,
                lighting_task,
                return_exceptions=True
            )

            # Check results
            if isinstance(texture_result, Exception):
                raise texture_result
            if isinstance(lighting_result, Exception):
                raise lighting_result

            if not texture_result.success:
                raise Exception(f"Texture synthesis failed: {texture_result.error}")
            if not lighting_result.success:
                raise Exception(f"Lighting setup failed: {lighting_result.error}")

            # Merge results
            scene_data = texture_result.data['scene_data']
            scene_data['lighting'] = lighting_result.data['scene_data']['lighting']

            self.pipeline_state['textures_applied'] = True
            self.pipeline_state['lighting_setup'] = True

            print(f"✓ Textures: {texture_result.metadata.get('num_materials', 0)} materials")
            print(f"  Duration: {texture_result.duration:.2f}s")
            print(f"✓ Lighting: {lighting_result.metadata.get('num_lights', 0)} lights")
            print(f"  Duration: {lighting_result.duration:.2f}s")
            print(f"  Total parallel time: {max(texture_result.duration, lighting_result.duration):.2f}s")
            print(f"  Time saved: {abs(texture_result.duration - lighting_result.duration):.2f}s")

            # Stage 5: Validate (if enabled)
            if validate:
                print("\n[Stage 5/6] SPATIAL VALIDATION")
                print("-" * 80)

                validation_result = await validator_agent.request(
                    'spatial_validator',
                    {'scene_data': scene_data, 'auto_fix': True},
                    timeout=45.0
                )

                if not validation_result.success:
                    logger.warning(f"Validation failed: {validation_result.error}")
                else:
                    scene_data = validation_result.data['scene_data']
                    self.pipeline_state['validation_passed'] = True

                    status = validation_result.metadata.get('validation_status', 'unknown')
                    issues = validation_result.metadata.get('issues_found', 0)

                    print(f"✓ Status: {status}")
                    print(f"✓ Issues found: {issues}")
                    print(f"  Duration: {validation_result.duration:.2f}s")
            else:
                print("\n[Stage 5/6] SPATIAL VALIDATION")
                print("-" * 80)
                print("⊘ Validation skipped")

            # Stage 6: Configure Rendering
            print("\n[Stage 6/6] RENDER CONFIGURATION")
            print("-" * 80)

            output_path = str(self.session_dir / f"scene.{output_format}")
            quality = self.config.get('quality', 'preview')

            render_result = await render_agent.request(
                'render_director',
                {
                    'scene_data': scene_data,
                    'output_path': output_path,
                    'quality': quality,
                    'format': output_format
                },
                timeout=90.0
            )

            if not render_result.success:
                raise Exception(f"Render configuration failed: {render_result.error}")

            self.pipeline_state['render_configured'] = True

            print(f"✓ Render configured: {quality}")
            print(f"✓ Output: {output_path}")
            print(f"  Duration: {render_result.duration:.2f}s")

            # Stage 7: Register Assets (non-blocking)
            print("\n[Bonus Stage] ASSET REGISTRATION")
            print("-" * 80)

            # Prepare assets for registration
            assets_to_register = [
                {
                    'name': obj.get('name', f"object_{i}"),
                    'path': output_path,
                    'asset_type': 'model',
                    'category': obj.get('category', 'generated'),
                    'tags': ['voxel', style, 'generated'],
                    'metadata': {
                        'session_id': self.session_id,
                        'prompt': prompt
                    }
                }
                for i, obj in enumerate(scene_data.get('objects', []))
            ]

            # Start registration (don't wait for completion)
            registration_task = asyncio.create_task(
                registry_agent.request(
                    'asset_registry',
                    {'action': 'register', 'assets': assets_to_register},
                    timeout=60.0
                )
            )

            print(f"⟳ Registering {len(assets_to_register)} assets in background...")

            # Build final result
            result = {
                'success': True,
                'output_path': output_path,
                'render_path': None,  # Would be set if actual rendering
                'session_dir': str(self.session_dir),
                'metadata': {
                    'session_id': self.session_id,
                    'prompt': prompt,
                    'style': style,
                    'num_objects': len(scene_data.get('objects', [])),
                    'num_lights': len(scene_data.get('lighting', {}).get('lights', [])),
                    'pipeline_state': self.pipeline_state,
                    'render_settings': render_result.data.get('render_plan', {})
                }
            }

            # Wait for registration to complete
            try:
                reg_result = await asyncio.wait_for(registration_task, timeout=10.0)
                if reg_result.success:
                    print(f"✓ Assets registered")
                else:
                    print(f"⚠ Asset registration failed: {reg_result.error}")
            except asyncio.TimeoutError:
                print("⚠ Asset registration timed out (continuing in background)")

            print("\n" + "="*80)
            print("ASYNC SCENE GENERATION COMPLETE!")
            print("="*80)
            print(f"\nOutput: {result.get('output_path', 'N/A')}")
            print("\n" + "="*80 + "\n")

            logger.info(f"Async scene generation complete: {result.get('output_path')}")

            # Get final statistics
            stats = self.message_bus.get_stats()
            print("\n📊 AGENT SYSTEM STATISTICS")
            print("-" * 80)
            print(f"Total messages: {stats['total_messages']}")
            print(f"Active agents: {stats['registered_agents']}")
            print("\nAgent Performance:")
            for agent_name, agent_stats in stats['agent_stats'].items():
                print(f"\n  {agent_name}:")
                print(f"    Tasks: {agent_stats['tasks_completed']} completed, {agent_stats['tasks_failed']} failed")
                print(f"    Avg time: {agent_stats['average_processing_time']:.2f}s")
                print(f"    Success rate: {agent_stats['success_rate']*100:.1f}%")

            return result

        except Exception as e:
            error_msg = f"Async scene generation failed: {str(e)}"
            print(f"\n❌ ERROR: {error_msg}\n")
            logger.error(error_msg, exc_info=True)

            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'metadata': {
                    'prompt': prompt,
                    'style': style,
                    'session_id': self.session_id
                }
            }

        finally:
            # Stop agent system
            await self.stop()


# Example usage
if __name__ == "__main__":
    from utils.logger import setup_logging

    setup_logging(level="INFO", console=True)

    async def test_async_orchestrator():
        """Test async scene orchestrator."""
        print("\n" + "="*80)
        print("ASYNC SCENE ORCHESTRATOR TEST")
        print("="*80 + "\n")

        # Create orchestrator
        config = {
            'output_dir': 'output/async_test',
            'quality': 'preview',
            'subsystems': {}
        }

        orchestrator = AsyncSceneOrchestrator(config=config)

        # Generate scene
        result = await orchestrator.generate_complete_scene(
            prompt="A cozy bedroom with a lamp and desk",
            style="realistic",
            validate=True,
            output_format="blend"
        )

        # Print result
        if result['success']:
            print(f"\n✅ Success! Scene: {result['output_path']}")
        else:
            print(f"\n❌ Failed: {result['error']}")

        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80 + "\n")

    # Run test
    asyncio.run(test_async_orchestrator())
