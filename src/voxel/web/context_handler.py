"""Handler for processing uploaded context files."""

import logging
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)


class ContextHandler:
    """Handles processing of uploaded context files."""

    def __init__(self, upload_dir: Path):
        """
        Initialize the context handler.

        Args:
            upload_dir: Directory for uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    def process_file(self, file_path: Path, filename: str, enable_ai_assignment: bool = False) -> Dict[str, Any]:
        """
        Process an uploaded file and extract context information.

        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            enable_ai_assignment: Whether to use AI to assign agents to this file

        Returns:
            Dictionary with file type, metadata, and AI assignments
        """
        file_type = self._detect_file_type(filename)

        metadata = {
            'filename': filename,
            'size': file_path.stat().st_size,
            'path': str(file_path)
        }

        # Process based on file type
        if file_type == '3d_model':
            metadata.update(self._process_3d_model(file_path))
        elif file_type == 'image':
            metadata.update(self._process_image(file_path))
        elif file_type == 'video':
            metadata.update(self._process_video(file_path))
        elif file_type == 'text':
            metadata.update(self._process_text(file_path))

        result = {
            'type': file_type,
            'metadata': metadata
        }

        # Add AI agent assignments if enabled
        if enable_ai_assignment:
            ai_assignments = self._get_ai_agent_assignments(file_path, file_type, metadata)
            result['ai_assignments'] = ai_assignments

        return result

    def _get_ai_agent_assignments(self, file_path: Path, file_type: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use AI to determine which agents should process this context file.
        
        Args:
            file_path: Path to the uploaded file
            file_type: Detected file type
            metadata: File metadata
            
        Returns:
            List of agent assignments with confidence scores
        """
        assignments = []
        
        # Define agent assignment rules based on file type and content
        agent_rules = {
            '3d_model': {
                'builder': {'confidence': 0.95, 'reason': '3D models are used for geometry and structure'},
                'texture': {'confidence': 0.85, 'reason': 'Models may need material and texture application'},
                'render': {'confidence': 0.80, 'reason': 'Models are rendered in final output'},
                'animation': {'confidence': 0.70, 'reason': 'Models may need animation setup'},
                'rigging': {'confidence': 0.60, 'reason': 'Character models may need rigging'}
            },
            'image': {
                'texture': {'confidence': 0.90, 'reason': 'Images are commonly used as textures'},
                'hdr': {'confidence': 0.85, 'reason': 'HDR images are used for environment lighting'},
                'render': {'confidence': 0.75, 'reason': 'Images may be used in compositing'},
                'compositing': {'confidence': 0.70, 'reason': 'Images may need post-processing effects'}
            },
            'video': {
                'sequence': {'confidence': 0.95, 'reason': 'Videos are used for sequence editing'},
                'compositing': {'confidence': 0.85, 'reason': 'Videos may need post-processing'},
                'animation': {'confidence': 0.75, 'reason': 'Video references for animation timing'},
                'render': {'confidence': 0.70, 'reason': 'Videos are rendered outputs'}
            },
            'text': {
                'concept': {'confidence': 0.90, 'reason': 'Text files contain scene descriptions and concepts'},
                'builder': {'confidence': 0.60, 'reason': 'Text may contain geometry specifications'},
                'animation': {'confidence': 0.55, 'reason': 'Text may contain animation scripts'}
            }
        }
        
        # Get assignments for this file type
        if file_type in agent_rules:
            for agent_id, assignment_info in agent_rules[file_type].items():
                # Adjust confidence based on file characteristics
                confidence = assignment_info['confidence']
                
                # Additional analysis based on filename and metadata
                filename_lower = metadata['filename'].lower()
                
                # HDR-specific detection
                if file_type == 'image' and ('hdr' in filename_lower or 'exr' in filename_lower):
                    if agent_id == 'hdr':
                        confidence = min(0.95, confidence + 0.1)
                    elif agent_id == 'texture':
                        confidence = max(0.3, confidence - 0.2)
                
                # Character/animation detection
                if ('character' in filename_lower or 'rig' in filename_lower or 'bone' in filename_lower):
                    if agent_id == 'rigging':
                        confidence = min(0.95, confidence + 0.2)
                    elif agent_id == 'animation':
                        confidence = min(0.90, confidence + 0.15)
                
                # Material/texture detection
                if ('material' in filename_lower or 'texture' in filename_lower or 'diffuse' in filename_lower):
                    if agent_id == 'texture':
                        confidence = min(0.95, confidence + 0.1)
                
                # Only include assignments with reasonable confidence
                if confidence >= 0.5:
                    assignments.append({
                        'agentId': agent_id,
                        'agentName': self._get_agent_display_name(agent_id),
                        'confidence': confidence,
                        'reason': assignment_info['reason']
                    })
        
        # Sort by confidence (highest first)
        assignments.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Limit to top 4 assignments
        return assignments[:4]

    def _get_agent_display_name(self, agent_id: str) -> str:
        """Get display name for agent ID."""
        display_names = {
            'concept': 'Concept Agent',
            'builder': 'Builder Agent',
            'texture': 'Texture Agent',
            'hdr': 'HDR Agent',
            'render': 'Render Agent',
            'animation': 'Animation Agent',
            'rigging': 'Rigging Agent',
            'particles': 'Particles Agent',
            'physics': 'Physics Agent',
            'compositing': 'Compositing Agent',
            'sequence': 'Sequence Agent'
        }
        return display_names.get(agent_id, f'{agent_id.title()} Agent')

    def _detect_file_type(self, filename: str) -> str:
        """Detect the type of file based on extension."""
        ext = filename.rsplit('.', 1)[-1].lower()

        type_mapping = {
            # 3D formats
            'blend': '3d_model',
            'obj': '3d_model',
            'fbx': '3d_model',
            'dae': '3d_model',
            'gltf': '3d_model',
            'glb': '3d_model',
            'stl': '3d_model',
            'ply': '3d_model',
            '3ds': '3d_model',
            'x3d': '3d_model',
            # Images
            'png': 'image',
            'jpg': 'image',
            'jpeg': 'image',
            'gif': 'image',
            'bmp': 'image',
            'tiff': 'image',
            'webp': 'image',
            'exr': 'image',
            'hdr': 'image',
            # Video
            'mp4': 'video',
            'avi': 'video',
            'mov': 'video',
            'mkv': 'video',
            'webm': 'video',
            'flv': 'video',
            # Text
            'txt': 'text',
            'md': 'text',
            'json': 'text',
            'yaml': 'text',
            'yml': 'text',
            'xml': 'text'
        }

        return type_mapping.get(ext, 'unknown')

    def _process_3d_model(self, file_path: Path) -> Dict[str, Any]:
        """
        Process 3D model files.

        Args:
            file_path: Path to the 3D model file

        Returns:
            Metadata dictionary
        """
        metadata = {'format': file_path.suffix[1:]}

        # For .obj files, we can extract some basic info
        if file_path.suffix.lower() == '.obj':
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    vertices = sum(1 for line in lines if line.startswith('v '))
                    faces = sum(1 for line in lines if line.startswith('f '))

                metadata['vertices'] = vertices
                metadata['faces'] = faces
                metadata['description'] = f"3D model with {vertices} vertices and {faces} faces"

            except Exception as e:
                logger.warning(f"Could not parse OBJ file: {e}")

        else:
            metadata['description'] = f"3D model in {file_path.suffix[1:].upper()} format"

        return metadata

    def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """
        Process image files.

        Args:
            file_path: Path to the image file

        Returns:
            Metadata dictionary
        """
        metadata = {'format': file_path.suffix[1:]}

        try:
            from PIL import Image

            with Image.open(file_path) as img:
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['mode'] = img.mode
                metadata['description'] = f"{img.width}x{img.height} {img.mode} image"

        except ImportError:
            logger.warning("PIL not available, using basic image metadata")
            metadata['description'] = f"Image file in {file_path.suffix[1:].upper()} format"

        except Exception as e:
            logger.warning(f"Could not process image: {e}")
            metadata['description'] = "Image file"

        return metadata

    def _process_video(self, file_path: Path) -> Dict[str, Any]:
        """
        Process video files.

        Args:
            file_path: Path to the video file

        Returns:
            Metadata dictionary
        """
        metadata = {'format': file_path.suffix[1:]}

        try:
            import cv2

            cap = cv2.VideoCapture(str(file_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            metadata['fps'] = fps
            metadata['frame_count'] = frame_count
            metadata['width'] = width
            metadata['height'] = height
            metadata['duration'] = duration
            metadata['description'] = f"{width}x{height} video, {duration:.1f}s at {fps}fps"

            cap.release()

        except ImportError:
            logger.warning("OpenCV not available, using basic video metadata")
            metadata['description'] = f"Video file in {file_path.suffix[1:].upper()} format"

        except Exception as e:
            logger.warning(f"Could not process video: {e}")
            metadata['description'] = "Video file"

        return metadata

    def _process_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Process text files.

        Args:
            file_path: Path to the text file

        Returns:
            Metadata dictionary
        """
        metadata = {'format': file_path.suffix[1:]}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                metadata['content'] = content
                metadata['lines'] = content.count('\n') + 1
                metadata['characters'] = len(content)
                metadata['description'] = f"Text file with {metadata['lines']} lines"

                # For JSON/YAML, try to parse
                if file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                    try:
                        if file_path.suffix.lower() == '.json':
                            data = json.loads(content)
                            metadata['parsed'] = True
                            metadata['data_type'] = 'json'
                        else:
                            import yaml
                            data = yaml.safe_load(content)
                            metadata['parsed'] = True
                            metadata['data_type'] = 'yaml'

                        metadata['description'] += f" (valid {metadata['data_type']})"

                    except Exception as e:
                        logger.warning(f"Could not parse structured data: {e}")

        except Exception as e:
            logger.warning(f"Could not read text file: {e}")
            metadata['description'] = "Text file"

        return metadata

    def load_context(self, file_path: str) -> Dict[str, Any]:
        """
        Load context data from a processed file.

        Args:
            file_path: Path to the context file

        Returns:
            Context data dictionary
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {file_path}")

        return self.process_file(path, path.name)

    def get_context_summary(self, context_files: list) -> str:
        """
        Generate a summary of context files for agent prompts.

        Args:
            context_files: List of context file paths

        Returns:
            Text summary of context
        """
        summaries = []

        for file_path in context_files:
            try:
                context = self.load_context(file_path)
                file_type = context['type']
                metadata = context['metadata']

                summary = f"- {metadata['filename']} ({file_type}): {metadata.get('description', 'No description')}"
                summaries.append(summary)

            except Exception as e:
                logger.warning(f"Could not load context from {file_path}: {e}")

        return "\n".join(summaries) if summaries else "No context files provided"
