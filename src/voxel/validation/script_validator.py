"""
Script Validation and Proofreading System
Ensures generated Blender scripts are syntactically correct and ready to run.
"""

import ast
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of script validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_script: Optional[str] = None
    fixes_applied: List[str] = None


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    line_number: int
    column: int
    issue_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    fix_suggestion: Optional[str] = None


class BlenderScriptValidator:
    """
    Validates and proofreads Blender Python scripts to ensure they're ready to run.
    """
    
    def __init__(self):
        self.common_imports = [
            'bpy',
            'bmesh',
            'mathutils',
            'math',
            'os',
            'pathlib',
            'json',
            'datetime'
        ]
        
        self.blender_modules = [
            'bpy',
            'bmesh',
            'mathutils',
            'gpu',
            'bl_math',
            'bl_ui',
            'bl_operators'
        ]
        
        self.common_patterns = {
            'missing_imports': [
                r'bpy\.ops\.',
                r'bpy\.data\.',
                r'bpy\.context\.',
                r'mathutils\.',
                r'bmesh\.'
            ],
            'deprecated_api': [
                r'bpy\.ops\.object\.mode_set\(mode=([\'"])(EDIT|OBJECT|POSE|SCULPT|VERTEX_PAINT|WEIGHT_PAINT|TEXTURE_PAINT|PARTICLE_EDIT)\1\)',
                r'bpy\.ops\.mesh\.select_all\(action=([\'"])(SELECT|DESELECT|INVERT)\1\)'
            ],
            'potential_errors': [
                r'bpy\.context\.scene\.objects\[([\'"])([^\'\"]+)\1\]',
                r'bpy\.data\.objects\[([\'"])([^\'\"]+)\1\]',
                r'bpy\.data\.materials\[([\'"])([^\'\"]+)\1\]'
            ]
        }

    def validate_script(self, script_content: str) -> ValidationResult:
        """
        Validate a Blender script for syntax errors and common issues.
        
        Args:
            script_content: The Python script content to validate
            
        Returns:
            ValidationResult with validation status and any issues found
        """
        import time
        start_time = time.time()
        
        errors = []
        warnings = []
        fixes_applied = []
        
        # Step 1: Basic Python syntax validation
        syntax_result = self._validate_syntax(script_content)
        if not syntax_result.is_valid:
            errors.extend(syntax_result.errors)
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                fixes_applied=fixes_applied
            )
        
        # Step 2: Check for missing imports
        import_result = self._check_imports(script_content)
        if import_result.errors:
            errors.extend(import_result.errors)
        if import_result.warnings:
            warnings.extend(import_result.warnings)
        
        # Step 3: Check Blender API usage
        blender_result = self._check_blender_api(script_content)
        if blender_result.errors:
            errors.extend(blender_result.errors)
        if blender_result.warnings:
            warnings.extend(blender_result.warnings)
        
        # Step 4: Check for common issues
        common_result = self._check_common_issues(script_content)
        if common_result.errors:
            errors.extend(common_result.errors)
        if common_result.warnings:
            warnings.extend(common_result.warnings)
        
        # Step 5: Auto-fix common issues if possible
        fixed_script = script_content
        if warnings and not errors:
            fixed_script, fixes = self._auto_fix_issues(script_content)
            if fixes:
                fixes_applied.extend(fixes)
                logger.info(f"Applied {len(fixes)} automatic fixes to script")
        
        # Log performance metrics
        validation_time = time.time() - start_time
        logger.info(f"Script validation completed in {validation_time:.3f}s - Status: {'VALID' if len(errors) == 0 else 'INVALID'}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixed_script=fixed_script if fixes_applied else None,
            fixes_applied=fixes_applied
        )

    def _validate_syntax(self, script_content: str) -> ValidationResult:
        """Validate Python syntax."""
        try:
            ast.parse(script_content)
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}"
            return ValidationResult(is_valid=False, errors=[error_msg], warnings=[])
        except Exception as e:
            error_msg = f"Parse error: {str(e)}"
            return ValidationResult(is_valid=False, errors=[error_msg], warnings=[])

    def _check_imports(self, script_content: str) -> ValidationResult:
        """Check for missing imports."""
        errors = []
        warnings = []
        
        lines = script_content.split('\n')
        
        # Find existing imports
        existing_imports = set()
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                # Extract module name
                match = re.match(r'(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line.strip())
                if match:
                    existing_imports.add(match.group(1))
        
        # Check for missing imports based on usage
        for pattern in self.common_patterns['missing_imports']:
            matches = re.findall(pattern, script_content)
            if matches:
                module = pattern.split('.')[0]
                if module not in existing_imports and module in self.blender_modules:
                    if module == 'bpy':
                        warnings.append(f"Consider adding 'import bpy' at the top of the script")
                    elif module == 'mathutils':
                        warnings.append(f"Consider adding 'from mathutils import Vector, Euler, Matrix' for 3D math operations")
                    elif module == 'bmesh':
                        warnings.append(f"Consider adding 'import bmesh' for mesh operations")
        
        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)

    def _check_blender_api(self, script_content: str) -> ValidationResult:
        """Check for Blender API usage issues."""
        errors = []
        warnings = []
        
        lines = script_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for deprecated API usage
            for pattern in self.common_patterns['deprecated_api']:
                if re.search(pattern, line):
                    warnings.append(f"Line {i}: Potential deprecated API usage: {line.strip()}")
            
            # Check for potential object access errors
            for pattern in self.common_patterns['potential_errors']:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple):
                        obj_name = match[1] if len(match) > 1 else match[0]
                        warnings.append(f"Line {i}: Direct object access by name '{obj_name}' may fail if object doesn't exist")
            
            # Check for common Blender mistakes
            if 'bpy.context.active_object' in line and 'if' not in line:
                warnings.append(f"Line {i}: Consider checking if active_object exists before using it")
            
            if 'bpy.data.objects.new(' in line and 'bpy.context.scene.collection.objects.link(' not in script_content:
                warnings.append(f"Line {i}: Objects created with bpy.data.objects.new() should be linked to scene")
            
            # Check for invalid world.volume access
            if 'world.volume' in line:
                errors.append(f"Line {i}: Invalid access to `world.volume` - this attribute does not exist in Blender's World object. Use world shader nodes instead for volumetric effects.")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _check_common_issues(self, script_content: str) -> ValidationResult:
        """Check for common scripting issues."""
        errors = []
        warnings = []
        
        lines = script_content.split('\n')
        
        # Check for common issues
        has_clear_operation = False
        has_camera_setup = False
        has_lighting_setup = False
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()
            
            # Check for clear scene operation
            if 'bpy.ops.object.select_all' in line or 'bpy.ops.object.delete' in line:
                has_clear_operation = True
            
            # Check for camera setup
            if 'bpy.ops.object.camera_add' in line or 'camera' in line_lower:
                has_camera_setup = True
            
            # Check for lighting setup
            if 'bpy.ops.object.light_add' in line or 'light' in line_lower:
                has_lighting_setup = True
            
            # Check for potential infinite loops or performance issues
            if 'while True:' in line or 'while 1:' in line:
                errors.append(f"Line {i}: Potential infinite loop detected")
            
            # Check for missing error handling
            if 'bpy.ops.' in line and 'try:' not in script_content:
                warnings.append(f"Line {i}: Consider adding error handling for Blender operations")
        
        # Add suggestions for scene setup
        if not has_clear_operation:
            warnings.append("Consider adding scene clearing operations at the beginning")
        if not has_camera_setup:
            warnings.append("Consider adding a camera for rendering")
        if not has_lighting_setup:
            warnings.append("Consider adding lighting to the scene")
        
        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)

    def _auto_fix_issues(self, script_content: str) -> Tuple[str, List[str]]:
        """Automatically fix common issues in the script."""
        fixed_script = script_content
        fixes_applied = []
        
        lines = fixed_script.split('\n')
        
        # Fix 1: Add missing imports at the top
        if 'import bpy' not in fixed_script and 'bpy.' in fixed_script:
            # Find the first non-comment, non-empty line
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    insert_index = i
                    break
            
            lines.insert(insert_index, 'import bpy')
            fixes_applied.append("Added missing 'import bpy'")
        
        # Fix 2: Add mathutils import if needed
        if 'from mathutils' not in fixed_script and ('Vector(' in fixed_script or 'Euler(' in fixed_script):
            # Find import section
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            if insert_index > 0:
                lines.insert(insert_index, 'from mathutils import Vector, Euler, Matrix')
                fixes_applied.append("Added missing 'from mathutils import Vector, Euler, Matrix'")
        
        # Fix 3: Add object existence checks
        fixed_lines = []
        for line in lines:
            # Add existence check before object access
            if 'bpy.data.objects[' in line and 'if' not in line:
                # Extract object name
                match = re.search(r'bpy\.data\.objects\[([\'"])([^\'\"]+)\1\]', line)
                if match:
                    obj_name = match.group(2)
                    fixed_lines.append(f"    if '{obj_name}' in bpy.data.objects:")
                    fixed_lines.append(f"        {line}")
                    fixes_applied.append(f"Added existence check for object '{obj_name}'")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Fix 4: Ensure proper scene linking for created objects
        if 'bpy.data.objects.new(' in fixed_script and 'bpy.context.scene.collection.objects.link(' not in fixed_script:
            # This is more complex and would need context analysis
            # For now, just add a warning comment
            insert_index = len(fixed_lines) - 1
            fixed_lines.insert(insert_index, '# Note: Ensure created objects are linked to scene collection')
            fixes_applied.append("Added reminder comment about scene linking")
        
        fixed_script = '\n'.join(fixed_lines)
        
        return fixed_script, fixes_applied

    def validate_and_fix_script(self, script_path: Path) -> ValidationResult:
        """
        Validate and fix a script file.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            ValidationResult with validation status and fixes
        """
        try:
            script_content = script_path.read_text(encoding='utf-8')
            result = self.validate_script(script_content)
            
            # If fixes were applied, save the fixed script
            if result.fixed_script and result.fixes_applied:
                backup_path = script_path.with_suffix('.py.backup')
                backup_path.write_text(script_content, encoding='utf-8')
                
                script_path.write_text(result.fixed_script, encoding='utf-8')
                logger.info(f"Fixed script saved: {script_path}")
                logger.info(f"Original script backed up to: {backup_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating script {script_path}: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to validate script: {str(e)}"],
                warnings=[],
                fixes_applied=[]
            )


def validate_script_content(script_content: str) -> ValidationResult:
    """
    Convenience function to validate script content.
    
    Args:
        script_content: The script content to validate
        
    Returns:
        ValidationResult with validation status
    """
    validator = BlenderScriptValidator()
    return validator.validate_script(script_content)


def validate_script_file(script_path: Path) -> ValidationResult:
    """
    Convenience function to validate a script file.
    
    Args:
        script_path: Path to the script file
        
    Returns:
        ValidationResult with validation status
    """
    validator = BlenderScriptValidator()
    return validator.validate_and_fix_script(script_path)
