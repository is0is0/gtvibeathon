"""Blender script execution engine."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

from voxel.core.config import Config
from voxel.core.models import BlenderScriptResult

logger = logging.getLogger(__name__)


class BlenderExecutor:
    """Executes Python scripts in Blender."""

    def __init__(self, config: Config):
        """
        Initialize the Blender executor.

        Args:
            config: Application configuration
        """
        self.config = config
        self.blender_path = config.blender_path

        if not self.blender_path.exists():
            raise FileNotFoundError(f"Blender not found at {self.blender_path}")

    def execute_script(
        self,
        script_path: Path,
        background: bool = True,
        timeout: int = 300,
    ) -> BlenderScriptResult:
        """
        Execute a Python script in Blender.

        Args:
            script_path: Path to the Python script
            background: Run in background mode (no GUI)
            timeout: Maximum execution time in seconds

        Returns:
            BlenderScriptResult with execution details
        """
        start_time = time.time()

        try:
            # Build command
            cmd = [str(self.blender_path)]

            if background:
                cmd.extend(["--background", "--python", str(script_path)])
            else:
                cmd.extend(["--python", str(script_path)])

            logger.info(f"Executing Blender script: {script_path}")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=script_path.parent,
            )

            execution_time = time.time() - start_time

            # Check for errors
            success = result.returncode == 0

            if not success:
                logger.error(f"Script execution failed: {result.stderr}")
            else:
                logger.info(f"Script executed successfully in {execution_time:.2f}s")

            return BlenderScriptResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                script_path=script_path,
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Script execution timed out after {timeout}s")
            return BlenderScriptResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                execution_time=execution_time,
                script_path=script_path,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Script execution failed: {e}")
            return BlenderScriptResult(
                success=False,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                script_path=script_path,
            )

    def execute_script_and_save_blend(
        self,
        script_path: Path,
        output_blend_path: Path,
        background: bool = True,
        timeout: int = 300,
    ) -> BlenderScriptResult:
        """
        Execute a Python script in Blender and save the resulting scene as a .blend file.

        Args:
            script_path: Path to the Python script
            output_blend_path: Path where to save the .blend file
            background: Run in background mode (no GUI)
            timeout: Maximum execution time in seconds

        Returns:
            BlenderScriptResult with execution details
        """
        start_time = time.time()

        try:
            # Build command with save operation
            cmd = [str(self.blender_path)]

            if background:
                cmd.extend(["--background", "--python", str(script_path)])
            else:
                cmd.extend(["--python", str(script_path)])

            # Add command to save the blend file after script execution
            save_script = f"""
import bpy

# Save the current scene as a .blend file
try:
    bpy.ops.wm.save_as_mainfile(filepath="{output_blend_path}", check_existing=False)
    print("✅ Scene saved as .blend file")
except Exception as e:
    print(f"❌ Failed to save .blend file: {{e}}")
"""
            
            # Create a temporary script that runs the original script and saves the blend file
            temp_script_path = script_path.parent / f"temp_exec_{script_path.name}"
            
            # Read original script content
            original_content = script_path.read_text()
            
            # Combine original script with save operation
            combined_content = original_content + "\n\n" + save_script
            temp_script_path.write_text(combined_content)

            logger.info(f"Executing Blender script and saving .blend file: {script_path}")
            logger.info(f"Output .blend file: {output_blend_path}")

            # Update command to use the temporary combined script
            if background:
                cmd = [str(self.blender_path), "--background", "--python", str(temp_script_path)]
            else:
                cmd = [str(self.blender_path), "--python", str(temp_script_path)]

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=script_path.parent,
            )

            execution_time = time.time() - start_time

            # Check for errors
            success = result.returncode == 0 and output_blend_path.exists()

            if not success:
                logger.error(f"Script execution or .blend file creation failed: {result.stderr}")
                if not output_blend_path.exists():
                    logger.error(f".blend file not created at: {output_blend_path}")
            else:
                logger.info(f"Script executed and .blend file saved successfully in {execution_time:.2f}s")
                logger.info(f"Blend file saved to: {output_blend_path}")

            # Clean up temporary script
            if temp_script_path.exists():
                temp_script_path.unlink()

            return BlenderScriptResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                script_path=script_path,
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Script execution timed out after {timeout}s")
            return BlenderScriptResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                execution_time=execution_time,
                script_path=script_path,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing script: {e}")
            return BlenderScriptResult(
                success=False,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                script_path=script_path,
            )

    def execute_scripts_sequence(
        self,
        script_paths: list[Path],
        blend_file: Optional[Path] = None,
        timeout: int = 300,
    ) -> list[BlenderScriptResult]:
        """
        Execute multiple scripts in sequence on the same Blender file.

        Args:
            script_paths: List of script paths to execute
            blend_file: Optional .blend file to work with
            timeout: Timeout per script in seconds

        Returns:
            List of BlenderScriptResults
        """
        results = []

        for script_path in script_paths:
            result = self.execute_script(script_path, timeout=timeout)
            results.append(result)

            if not result.success:
                logger.error(f"Script {script_path.name} failed, stopping sequence")
                break

        return results

    def render_scene(
        self,
        blend_file: Path,
        output_path: Path,
        samples: Optional[int] = None,
        engine: Optional[str] = None,
        timeout: int = 600,
    ) -> BlenderScriptResult:
        """
        Render a Blender scene to an image.

        Args:
            blend_file: Path to the .blend file
            output_path: Where to save the render
            samples: Number of render samples (overrides file settings)
            engine: Render engine ('CYCLES' or 'EEVEE')
            timeout: Maximum render time in seconds

        Returns:
            BlenderScriptResult with render details
        """
        # Create a temporary script for rendering
        render_script = blend_file.parent / "temp_render.py"

        script_content = f"""
import bpy

# Set render settings
scene = bpy.context.scene
scene.render.filepath = "{output_path}"
scene.render.image_settings.file_format = 'PNG'

"""

        if samples is not None:
            script_content += f"scene.cycles.samples = {samples}\n"

        if engine is not None:
            script_content += f"scene.render.engine = '{engine}'\n"

        script_content += """
# Render
bpy.ops.render.render(write_still=True)
print(f"Render complete: {scene.render.filepath}")
"""

        # Write temporary script
        render_script.write_text(script_content)

        try:
            # Execute render
            cmd = [
                str(self.blender_path),
                "--background",
                str(blend_file),
                "--python",
                str(render_script),
            ]

            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            execution_time = time.time() - start_time

            success = result.returncode == 0 and output_path.exists()

            return BlenderScriptResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                script_path=render_script,
            )

        finally:
            # Clean up temporary script
            if render_script.exists():
                render_script.unlink()
