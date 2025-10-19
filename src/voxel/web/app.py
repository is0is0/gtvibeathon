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
    session_manager = SessionManager()

    # Store in app context
    app.voxel_config = config
    app.context_handler = context_handler
    app.session_manager = session_manager
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

        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = app.config['UPLOAD_FOLDER'] / session_id / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    file.save(str(file_path))

                    # Process the file to extract context
                    context_data = context_handler.process_file(file_path, filename)

                    uploaded_files.append({
                        'filename': filename,
                        'path': str(file_path),
                        'type': context_data['type'],
                        'metadata': context_data['metadata']
                    })

                    logger.info(f"Uploaded and processed: {filename}")

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

        return jsonify(session_data)

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

        if not session_data or session_data.get('status') != 'completed':
            return jsonify({'error': 'Session not found or incomplete'}), 404

        output_path = Path(session_data.get('output_path', ''))

        if not output_path.exists():
            return jsonify({'error': 'Output files not found'}), 404

        try:
            if file_type == 'blend':
                # Send the .blend file
                blend_file = output_path / 'scene.blend'
                if blend_file.exists():
                    return send_file(
                        blend_file,
                        as_attachment=True,
                        download_name=f'voxel_scene_{session_id}.blend',
                        mimetype='application/octet-stream'
                    )

            elif file_type == 'render':
                # Send the latest render
                renders_dir = output_path / 'renders'
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
                # Zip all scripts and send
                scripts_dir = output_path / 'scripts'
                if scripts_dir.exists():
                    # Create zip in memory
                    memory_file = io.BytesIO()
                    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for script in scripts_dir.glob('*.py'):
                            zf.write(script, script.name)
                    memory_file.seek(0)

                    return send_file(
                        memory_file,
                        as_attachment=True,
                        download_name=f'voxel_scripts_{session_id}.zip',
                        mimetype='application/zip'
                    )

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
            # Update session status
            app.session_manager.update_status(session_id, 'running')

            # Emit progress update
            app.socketio.emit('progress', {
                'session_id': session_id,
                'stage': 'initialization',
                'message': 'Initializing agents...'
            }, room=session_id)

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
