"""Flask web application for Voxel interface."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from voxel import Voxel, Config
from voxel.core.models import AgentRole
from voxel.web.context_handler import ContextHandler
from voxel.web.session_manager import SessionManager
from voxel.validation import BlenderScriptValidator

logger = logging.getLogger(__name__)


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config: Optional Voxel configuration

    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    app.config['UPLOAD_FOLDER'] = Path('uploads')
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

    # Enable CORS for API endpoints - more permissive for ngrok
    CORS(app, 
         origins="*", 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Initialize SocketIO for real-time updates - enhanced for ngrok
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        cors_credentials=True,
        async_mode='threading',
        logger=True,
        engineio_logger=True,
        always_connect=True,
        allow_upgrades=True,
        ping_timeout=60,
        ping_interval=25
    )

    # Load Voxel configuration
    if config is None:
        config = Config()

    # Initialize managers
    context_handler = ContextHandler(app.config['UPLOAD_FOLDER'])
    session_manager = SessionManager(output_dir=config.output_dir)
    script_validator = BlenderScriptValidator()

    # Store in app context
    app.voxel_config = config
    app.context_handler = context_handler
    app.session_manager = session_manager
    app.script_validator = script_validator
    app.socketio = socketio

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        # 3D formats
        'blend', 'obj', 'fbx', 'dae', 'gltf', 'glb', 'stl', 'ply', '3ds', 'x3d',
        # Images
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'exr', 'hdr',
        # Video
        'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv',
        # Text/Documents
        'txt', 'md', 'json', 'yaml', 'yml', 'xml'
    }

    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def index():
        """Render the main application page."""
        return render_template('index.html')

    @app.route('/api/agents', methods=['GET'])
    def get_agents():
        """Get list of available agents with their descriptions."""
        agents = [
            {
                'id': 'concept',
                'name': 'Concept Agent',
                'role': AgentRole.CONCEPT.value,
                'description': 'Interprets your vision and creates detailed scene concepts',
                'personality': 'creative_visionary',
                'icon': '🎨',
                'capabilities': ['scene_planning', 'mood_design', 'composition']
            },
            {
                'id': 'builder',
                'name': 'Builder Agent',
                'role': AgentRole.BUILDER.value,
                'description': 'Constructs 3D geometry and models from concepts',
                'personality': 'technical_architect',
                'icon': '🏗️',
                'capabilities': ['geometry_creation', 'modifiers', 'collections']
            },
            {
                'id': 'texture',
                'name': 'Texture Artist Agent',
                'role': AgentRole.TEXTURE.value,
                'description': 'Creates stunning materials and shaders',
                'personality': 'artistic_perfectionist',
                'icon': '🎭',
                'capabilities': ['materials', 'shaders', 'procedural_textures']
            },
            {
                'id': 'render',
                'name': 'Cinematographer Agent',
                'role': AgentRole.RENDER.value,
                'description': 'Sets up cameras, lighting, and render settings',
                'personality': 'cinematic_expert',
                'icon': '📸',
                'capabilities': ['camera_setup', 'lighting', 'render_optimization']
            },
            {
                'id': 'animation',
                'name': 'Animation Director Agent',
                'role': AgentRole.ANIMATION.value,
                'description': 'Brings scenes to life with dynamic animations',
                'personality': 'energetic_storyteller',
                'icon': '🎬',
                'capabilities': ['keyframe_animation', 'camera_motion', 'physics']
            },
            {
                'id': 'reviewer',
                'name': 'Quality Reviewer Agent',
                'role': AgentRole.REVIEWER.value,
                'description': 'Critiques and refines the final output',
                'personality': 'meticulous_critic',
                'icon': '🔍',
                'capabilities': ['quality_assurance', 'feedback', 'refinement']
            },
            {
                'id': 'rigging',
                'name': 'Rigging Specialist Agent',
                'role': 'rigging',
                'description': 'Creates character rigs and armatures',
                'personality': 'technical_animator',
                'icon': '🦴',
                'capabilities': ['armature_creation', 'weight_painting', 'constraints']
            },
            {
                'id': 'compositing',
                'name': 'Compositing Artist Agent',
                'role': 'compositing',
                'description': 'Adds post-processing effects and enhancements',
                'personality': 'visual_effects_wizard',
                'icon': '✨',
                'capabilities': ['post_processing', 'effects', 'color_grading']
            },
            {
                'id': 'sequence',
                'name': 'Sequence Editor Agent',
                'role': 'sequence',
                'description': 'Edits and arranges multi-shot sequences',
                'personality': 'film_editor',
                'icon': '🎞️',
                'capabilities': ['video_editing', 'shot_composition', 'transitions']
            }
        ]
        return jsonify({'agents': agents})

    @app.route('/api/upload', methods=['POST'])
    def upload_context():
        """Upload context files (3D models, images, videos, etc.)."""
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        session_id = request.form.get('session_id', session_manager.create_session())

        uploaded_files = []
        errors = []

        # Check if AI assignment is enabled
        enable_ai_assignment = request.form.get('enable_ai_assignment', 'false').lower() == 'true'

        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = app.config['UPLOAD_FOLDER'] / session_id / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    file.save(str(file_path))

                    # Process the file to extract context with AI assignment
                    context_data = context_handler.process_file(file_path, filename, enable_ai_assignment)

                    uploaded_file = {
                        'filename': filename,
                        'path': str(file_path),
                        'type': context_data['type'],
                        'metadata': context_data['metadata']
                    }

                    # Add AI assignments if available
                    if 'ai_assignments' in context_data:
                        uploaded_file['ai_assignments'] = context_data['ai_assignments']

                    uploaded_files.append(uploaded_file)

                    logger.info(f"Uploaded and processed: {filename}")

                    # Emit AI assignment data via socket if available
                    if enable_ai_assignment and 'ai_assignments' in context_data:
                        app.socketio.emit('context-assigned', {
                            'file_id': filename,
                            'assignments': context_data['ai_assignments']
                        })

                except Exception as e:
                    errors.append(f"Failed to process {filename}: {str(e)}")
                    logger.error(f"Error processing {filename}: {e}")
            else:
                errors.append(f"File type not allowed: {file.filename}")

        return jsonify({
            'session_id': session_id,
            'uploaded': uploaded_files,
            'errors': errors
        })

    @app.route('/api/generate', methods=['POST'])
    def generate_scene():
        """Start scene generation with selected agents and context."""
        data = request.json

        prompt = data.get('prompt')
        selected_agents = data.get('agents', [])
        session_id = data.get('session_id')
        context_files = data.get('context_files', [])

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        try:
            # Create generation session
            gen_session = session_manager.start_generation(
                session_id=session_id,
                prompt=prompt,
                agents=selected_agents,
                context=context_files
            )

            # Start generation in background thread
            socketio.start_background_task(
                target=run_generation,
                app=app,
                session_id=gen_session['id'],
                prompt=prompt,
                selected_agents=selected_agents,
                context_files=context_files
            )

            return jsonify({
                'session_id': gen_session['id'],
                'status': 'started',
                'message': 'Scene generation started'
            })

        except Exception as e:
            logger.error(f"Generation error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.route('/api/session/<session_id>', methods=['GET'])
    def get_session_status(session_id: str):
        """Get the status of a generation session."""
        session_data = session_manager.get_session(session_id)

        if not session_data:
            return jsonify({'error': 'Session not found'}), 404

        # Add download URLs if session has files (regardless of status)
        base_url = request.url_root.rstrip('/')
        session_data['download_urls'] = {
            'blend': f"{base_url}/api/download/{session_id}/blend",
            'scripts': f"{base_url}/api/download/{session_id}/scripts",
            'render': f"{base_url}/api/download/{session_id}/render"
        }
        
        # Check if files actually exist
        session_dir = Path(session_data.get('output_path', ''))
        if not session_dir.exists():
            # Try to find session directory in output folder
            session_id_from_data = session_data.get('id')
            if session_id_from_data:
                session_dir = Path(f"output/{session_id_from_data}")
        
        if session_dir.exists():
            session_data['download_available'] = {
                'blend': len(list(session_dir.glob('*.blend'))) > 0,
                'scripts': len(list((session_dir / 'scripts').glob('*.py'))) > 0 if (session_dir / 'scripts').exists() else False,
                'render': len(list((session_dir / 'renders').glob('*.png'))) > 0 if (session_dir / 'renders').exists() else False
            }
        else:
            session_data['download_available'] = {
                'blend': False,
                'scripts': False,
                'render': False
            }

        return jsonify(session_data)

    @app.route('/api/sessions', methods=['GET'])
    def list_sessions():
        """
        List all sessions (including recovered ones).
        Supports filtering by status and limiting results.
        """
        status_filter = request.args.get('status')  # e.g., 'completed', 'running', 'failed'
        limit = request.args.get('limit', type=int, default=50)

        with session_manager.lock:
            sessions_list = list(session_manager.sessions.values())

        # Filter by status if provided
        if status_filter:
            sessions_list = [s for s in sessions_list if s.get('status') == status_filter]

        # Sort by created_at (most recent first)
        sessions_list.sort(key=lambda s: s.get('created_at', ''), reverse=True)

        # Limit results
        sessions_list = sessions_list[:limit]

        return jsonify({
            'sessions': sessions_list,
            'total': len(sessions_list)
        })

    @app.route('/api/session/<session_id>/agents', methods=['POST'])
    def modify_session_agents(session_id: str):
        """Add or remove agents during generation."""
        data = request.json
        action = data.get('action')  # 'add' or 'remove'
        agent_ids = data.get('agents', [])

        if action not in ['add', 'remove']:
            return jsonify({'error': 'Invalid action'}), 400

        try:
            session_manager.modify_agents(session_id, action, agent_ids)

            # Emit event for real-time update
            socketio.emit('agents_modified', {
                'session_id': session_id,
                'action': action,
                'agents': agent_ids
            }, room=session_id)

            return jsonify({
                'status': 'success',
                'message': f'Agents {action}ed successfully'
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'status': 'connected'})
        return True

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")

    @socketio.on('join_session')
    def handle_join_session(data):
        """Join a generation session room for updates."""
        session_id = data.get('session_id')
        if session_id:
            from flask_socketio import join_room
            join_room(session_id)
            emit('joined_session', {'session_id': session_id})
        return True

    @socketio.on('test_connection')
    def handle_test_connection():
        """Test SocketIO connection."""
        emit('test_response', {'status': 'connected', 'message': 'SocketIO is working!'})
        return True

    @app.route('/api/download/<session_id>/<file_type>', methods=['GET'])
    def download_file(session_id: str, file_type: str):
        """Download generated files (blend, render, scripts)."""
        from flask import send_file
        import zipfile
        import io

        session_data = session_manager.get_session(session_id)

        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        # Allow downloads for sessions that have files, regardless of status
        # Check if session directory exists and has files
        session_dir = Path(session_data.get('output_path', ''))
        if not session_dir.exists():
            # Try to find session directory in output folder
            session_id = session_data.get('id')
            if session_id:
                session_dir = Path(f"output/{session_id}")
            
        if not session_dir.exists():
            return jsonify({'error': 'Session files not found'}), 404

        logger.info(f"Download request for session {session_id}, type {file_type}, dir: {session_dir}")

        try:
            if file_type == 'blend':
                # Send the .blend file (look for any .blend file)
                blend_files = list(session_dir.glob('*.blend'))
                if blend_files:
                    # Use the first .blend file found
                    blend_file = blend_files[0]
                    return send_file(
                        blend_file,
                        as_attachment=True,
                        download_name=f'voxel_scene_{session_id}.blend',
                        mimetype='application/octet-stream'
                    )

            elif file_type == 'render':
                # Send the latest render
                renders_dir = session_dir / 'renders'
                if renders_dir.exists():
                    renders = sorted(renders_dir.glob('*.png'))
                    if renders:
                        return send_file(
                            renders[-1],
                            as_attachment=True,
                            download_name=f'voxel_render_{session_id}.png',
                            mimetype='image/png'
                        )

            elif file_type == 'scripts':
                # Send only the complete compiled script (not individual agent scripts)
                scripts_dir = session_dir / 'scripts'
                if scripts_dir.exists():
                    # Look for the combined/complete script first
                    combined_scripts = list(scripts_dir.glob('combined_*.py'))
                    if combined_scripts:
                        # Use the latest combined script
                        latest_combined = max(combined_scripts, key=lambda x: x.stat().st_mtime)
                        
                        # Final validation before serving
                        script_content = latest_combined.read_text()
                        validation_result = app.script_validator.validate_script(script_content)
                        
                        if validation_result.errors:
                            logger.error(f"Final script validation failed for {latest_combined}:")
                            for error in validation_result.errors:
                                logger.error(f"  - {error}")
                            return jsonify({'error': 'Script validation failed. Please try regenerating.'}), 500
                        
                        # Use fixed script if available
                        if validation_result.fixed_script:
                            # Save the fixed version
                            fixed_path = latest_combined.with_suffix('.py.fixed')
                            fixed_path.write_text(validation_result.fixed_script)
                            logger.info(f"Fixed script saved to {fixed_path}")
                            return send_file(
                                fixed_path,
                                as_attachment=True,
                                download_name=f'voxel_complete_script_{session_id}.py',
                                mimetype='text/plain'
                            )
                        
                        return send_file(
                            latest_combined,
                            as_attachment=True,
                            download_name=f'voxel_complete_script_{session_id}.py',
                            mimetype='text/plain'
                        )
                    else:
                        # Fallback: look for any complete script (not individual agent scripts)
                        all_scripts = list(scripts_dir.glob('*.py'))
                        # Filter out individual agent scripts (they have specific naming patterns)
                        individual_patterns = ['01_concept_', '02_builder_', '03_texture_', '04_render_', '05_animation_', '06_hdr_', '07_rigging_', '08_particles_', '09_physics_', '10_compositing_', '11_sequence_']
                        complete_scripts = [s for s in all_scripts if not any(pattern in s.name for pattern in individual_patterns)]
                        
                        if complete_scripts:
                            # Use the latest complete script
                            latest_complete = max(complete_scripts, key=lambda x: x.stat().st_mtime)
                            return send_file(
                                latest_complete,
                                as_attachment=True,
                                download_name=f'voxel_complete_script_{session_id}.py',
                                mimetype='text/plain'
                            )
                        else:
                            return jsonify({'error': 'No complete script found'}), 404

            return jsonify({'error': f'File type {file_type} not available'}), 404

        except Exception as e:
            logger.error(f"Download error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'voxel-api',
            'version': '0.1.0'
        })

    @app.route('/socket.io/', methods=['GET', 'POST', 'OPTIONS'])
    def socketio_handler():
        """Handle SocketIO requests with proper CORS headers."""
        from flask import request, make_response
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        return "SocketIO endpoint"

    return app


def run_generation(app, session_id: str, prompt: str, selected_agents: List[str], context_files: List[str]):
    """
    Run the scene generation process in background.

    Args:
        app: Flask app instance
        session_id: Session identifier
        prompt: User's scene description
        selected_agents: List of agent IDs to use
        context_files: List of context file paths
    """
    with app.app_context():
        try:
            # Small delay to ensure client has joined the room
            import time
            time.sleep(0.5)

            # Update session status
            app.session_manager.update_status(session_id, 'running')

            # Emit progress update
            app.socketio.emit('progress', {
                'session_id': session_id,
                'stage': 'initialization',
                'message': 'Initializing agents...'
            }, room=session_id)

            logger.info(f"Emitting progress updates to room: {session_id}")

            # Initialize Voxel with dynamic agent configuration
            config = app.voxel_config
            voxel = Voxel(config)

            # Configure which agents to use
            voxel.configure_agents(selected_agents)

            # Load context from uploaded files
            if context_files:
                for context_file in context_files:
                    context_data = app.context_handler.load_context(context_file)
                    voxel.add_context(context_data)

            # Progress callback
            def on_progress(stage: str, agent: str, message: str):
                app.socketio.emit('progress', {
                    'session_id': session_id,
                    'stage': stage,
                    'agent': agent,
                    'message': message
                }, room=session_id)

            # Set progress callback
            voxel.set_progress_callback(on_progress)

            # Generate scene
            result = voxel.create_scene(
                prompt=prompt,
                session_name=session_id
            )

            # Update session with result
            app.session_manager.complete_generation(session_id, result)

            # Emit completion
            app.socketio.emit('complete', {
                'session_id': session_id,
                'success': result.success,
                'output_path': str(result.output_path) if result.output_path else None,
                'iterations': result.iterations,
                'render_time': result.render_time
            }, room=session_id)

        except Exception as e:
            logger.error(f"Generation error in session {session_id}: {e}", exc_info=True)

            app.session_manager.update_status(session_id, 'failed', str(e))

            app.socketio.emit('error', {
                'session_id': session_id,
                'error': str(e)
            }, room=session_id)
