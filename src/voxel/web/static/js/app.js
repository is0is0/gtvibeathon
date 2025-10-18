// Voxel Web Interface JavaScript

class VoxelApp {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.selectedAgents = [];
        this.uploadedFiles = [];
        this.availableAgents = [];
        this.isGenerating = false;

        this.init();
    }

    async init() {
        // Initialize Socket.IO
        this.socket = io();

        // Set up socket event listeners
        this.setupSocketListeners();

        // Set up UI event listeners
        this.setupUIListeners();

        // Load available agents
        await this.loadAgents();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateStatus('Connected', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateStatus('Disconnected', 'error');
        });

        this.socket.on('progress', (data) => {
            console.log('Progress update:', data);
            this.addProgressUpdate(data);
            this.updateStatus(`${data.stage}: ${data.message}`, 'info');
        });

        this.socket.on('complete', (data) => {
            console.log('Generation complete:', data);
            this.handleGenerationComplete(data);
        });

        this.socket.on('error', (data) => {
            console.error('Generation error:', data);
            this.handleGenerationError(data);
        });

        this.socket.on('agents_modified', (data) => {
            console.log('Agents modified:', data);
            this.handleAgentsModified(data);
        });
    }

    setupUIListeners() {
        // New session button
        document.getElementById('newSessionBtn').addEventListener('click', () => {
            this.newSession();
        });

        // Generate button
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateScene();
        });

        // Upload button
        document.getElementById('uploadBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Select/Deselect all agents
        document.getElementById('selectAllAgents').addEventListener('click', () => {
            this.selectAllAgents();
        });

        document.getElementById('deselectAllAgents').addEventListener('click', () => {
            this.deselectAllAgents();
        });

        // Prompt input - allow Enter to generate (with Shift for new line)
        const promptInput = document.getElementById('promptInput');
        promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.generateScene();
            }
        });

        // Add/Remove agents during generation
        document.getElementById('addAgentsBtn').addEventListener('click', () => {
            this.showAddAgentsDialog();
        });

        document.getElementById('removeAgentsBtn').addEventListener('click', () => {
            this.showRemoveAgentsDialog();
        });
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const data = await response.json();

            this.availableAgents = data.agents;
            this.renderAgents();

            // Select core agents by default
            const coreAgents = ['concept', 'builder', 'texture', 'render'];
            coreAgents.forEach(agentId => {
                const index = this.availableAgents.findIndex(a => a.id === agentId);
                if (index !== -1) {
                    this.toggleAgent(agentId);
                }
            });

        } catch (error) {
            console.error('Failed to load agents:', error);
            this.showError('Failed to load agents');
        }
    }

    renderAgents() {
        const container = document.getElementById('agentsContainer');
        container.innerHTML = '';

        this.availableAgents.forEach(agent => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.dataset.agentId = agent.id;

            agentCard.innerHTML = `
                <div class="agent-header">
                    <span class="agent-icon">${agent.icon}</span>
                    <span class="agent-name">${agent.name}</span>
                </div>
                <div class="agent-description">${agent.description}</div>
                <div class="agent-capabilities">
                    ${agent.capabilities.map(cap =>
                        `<span class="capability-tag">${cap.replace('_', ' ')}</span>`
                    ).join('')}
                </div>
            `;

            agentCard.addEventListener('click', () => {
                this.toggleAgent(agent.id);
            });

            container.appendChild(agentCard);
        });
    }

    toggleAgent(agentId) {
        const index = this.selectedAgents.indexOf(agentId);

        if (index === -1) {
            this.selectedAgents.push(agentId);
        } else {
            this.selectedAgents.splice(index, 1);
        }

        this.updateAgentUI();
    }

    updateAgentUI() {
        // Update agent cards
        document.querySelectorAll('.agent-card').forEach(card => {
            const agentId = card.dataset.agentId;
            if (this.selectedAgents.includes(agentId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });

        // Update active agents list
        this.renderActiveAgents();
    }

    renderActiveAgents() {
        const container = document.getElementById('activeAgentsList');

        if (this.selectedAgents.length === 0) {
            container.innerHTML = '<p class="empty-state">No agents selected</p>';
            return;
        }

        container.innerHTML = '';

        this.selectedAgents.forEach(agentId => {
            const agent = this.availableAgents.find(a => a.id === agentId);
            if (agent) {
                const item = document.createElement('div');
                item.className = 'active-agent-item';
                item.innerHTML = `
                    <div class="active-agent-name">${agent.icon} ${agent.name}</div>
                    <div class="active-agent-role">${agent.role}</div>
                `;
                container.appendChild(item);
            }
        });

        // Enable/disable agent control buttons
        const isGenerating = this.isGenerating;
        document.getElementById('addAgentsBtn').disabled = !isGenerating;
        document.getElementById('removeAgentsBtn').disabled = !isGenerating || this.selectedAgents.length === 0;
    }

    selectAllAgents() {
        this.selectedAgents = this.availableAgents.map(a => a.id);
        this.updateAgentUI();
    }

    deselectAllAgents() {
        this.selectedAgents = [];
        this.updateAgentUI();
    }

    async handleFileUpload(files) {
        if (files.length === 0) return;

        const formData = new FormData();

        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        if (this.sessionId) {
            formData.append('session_id', this.sessionId);
        }

        try {
            this.updateStatus('Uploading files...', 'info');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.errors && data.errors.length > 0) {
                data.errors.forEach(error => {
                    this.showError(error);
                });
            }

            if (data.uploaded && data.uploaded.length > 0) {
                this.sessionId = data.session_id;
                this.uploadedFiles.push(...data.uploaded);
                this.renderUploadedFiles();
                this.renderContextList();
                this.updateStatus(`Uploaded ${data.uploaded.length} file(s)`, 'success');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload files');
        }

        // Reset file input
        document.getElementById('fileInput').value = '';
    }

    renderUploadedFiles() {
        const container = document.getElementById('uploadedFiles');
        container.innerHTML = '';

        this.uploadedFiles.forEach((file, index) => {
            const fileTag = document.createElement('div');
            fileTag.className = 'uploaded-file';
            fileTag.innerHTML = `
                <span>📎 ${file.filename}</span>
                <button class="file-remove" data-index="${index}">×</button>
            `;

            fileTag.querySelector('.file-remove').addEventListener('click', () => {
                this.removeFile(index);
            });

            container.appendChild(fileTag);
        });
    }

    renderContextList() {
        const container = document.getElementById('contextList');

        if (this.uploadedFiles.length === 0) {
            container.innerHTML = '<p class="empty-state">No files uploaded yet</p>';
            return;
        }

        container.innerHTML = '';

        this.uploadedFiles.forEach(file => {
            const item = document.createElement('div');
            item.className = 'context-item';
            item.innerHTML = `
                <div class="context-item-name">${file.filename}</div>
                <div class="context-item-desc">${file.metadata.description || file.type}</div>
            `;
            container.appendChild(item);
        });
    }

    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.renderUploadedFiles();
        this.renderContextList();
    }

    async generateScene() {
        const prompt = document.getElementById('promptInput').value.trim();

        if (!prompt) {
            this.showError('Please enter a scene description');
            return;
        }

        if (this.selectedAgents.length === 0) {
            this.showError('Please select at least one agent');
            return;
        }

        try {
            this.isGenerating = true;
            this.updateGenerateButton(true);
            this.clearProgress();

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    agents: this.selectedAgents,
                    session_id: this.sessionId,
                    context_files: this.uploadedFiles.map(f => f.path)
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.sessionId = data.session_id;

                // Join the session room for real-time updates
                this.socket.emit('join_session', { session_id: this.sessionId });

                // Add user message to chat
                this.addMessage('user', prompt);

                this.updateStatus('Generation started...', 'info');

            } else {
                throw new Error(data.error || 'Generation failed');
            }

        } catch (error) {
            console.error('Generation error:', error);
            this.showError(error.message);
            this.isGenerating = false;
            this.updateGenerateButton(false);
        }
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addProgressUpdate(data) {
        const container = document.getElementById('progressContainer');

        // Remove "no progress" message
        const noProgress = container.querySelector('.no-progress');
        if (noProgress) {
            noProgress.remove();
        }

        // Check if stage already exists
        let stageDiv = container.querySelector(`[data-stage="${data.stage}"]`);

        if (!stageDiv) {
            stageDiv = document.createElement('div');
            stageDiv.className = 'progress-stage';
            stageDiv.dataset.stage = data.stage;
            container.appendChild(stageDiv);
        }

        // Mark as active
        container.querySelectorAll('.progress-stage').forEach(s => s.classList.remove('active'));
        stageDiv.classList.add('active');

        stageDiv.innerHTML = `
            <div class="stage-header">
                <span class="stage-name">${this.formatStageName(data.stage)}</span>
                <span class="stage-agent">${data.agent || ''}</span>
            </div>
            <div class="stage-message">${this.escapeHtml(data.message)}</div>
        `;

        container.scrollTop = container.scrollHeight;
    }

    handleGenerationComplete(data) {
        this.isGenerating = false;
        this.updateGenerateButton(false);

        if (data.success) {
            this.updateStatus('Generation complete!', 'success');

            // Add success message to chat
            this.addMessage('system', `Scene generated successfully! Render saved to: ${data.output_path}`);

            // Show result modal
            this.showResultModal(data);

        } else {
            this.updateStatus('Generation failed', 'error');
            this.showError('Scene generation failed');
        }
    }

    handleGenerationError(data) {
        this.isGenerating = false;
        this.updateGenerateButton(false);
        this.updateStatus('Error', 'error');
        this.showError(data.error || 'An error occurred during generation');
    }

    handleAgentsModified(data) {
        // Update UI to reflect agent changes
        this.addMessage('system', `Agents ${data.action}: ${data.agents.join(', ')}`);
    }

    showResultModal(data) {
        const modal = document.getElementById('resultModal');
        const content = document.getElementById('resultContent');

        content.innerHTML = `
            <p><strong>Output:</strong> ${data.output_path}</p>
            <p><strong>Iterations:</strong> ${data.iterations}</p>
            <p><strong>Render Time:</strong> ${data.render_time.toFixed(2)}s</p>
            <div style="margin-top: 1.5rem;">
                <button class="btn btn-primary" onclick="voxelApp.closeModal()">Close</button>
            </div>
        `;

        modal.classList.add('active');

        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Close button
        modal.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });
    }

    closeModal() {
        document.getElementById('resultModal').classList.remove('active');
    }

    async modifyAgents(action, agentIds) {
        if (!this.sessionId) return;

        try {
            const response = await fetch(`/api/session/${this.sessionId}/agents`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: action,
                    agents: agentIds
                })
            });

            const data = await response.json();

            if (response.ok) {
                if (action === 'add') {
                    agentIds.forEach(id => {
                        if (!this.selectedAgents.includes(id)) {
                            this.selectedAgents.push(id);
                        }
                    });
                } else if (action === 'remove') {
                    this.selectedAgents = this.selectedAgents.filter(id => !agentIds.includes(id));
                }

                this.updateAgentUI();

            } else {
                throw new Error(data.error || 'Failed to modify agents');
            }

        } catch (error) {
            console.error('Error modifying agents:', error);
            this.showError(error.message);
        }
    }

    showAddAgentsDialog() {
        // Get agents not currently selected
        const availableToAdd = this.availableAgents.filter(a => !this.selectedAgents.includes(a.id));

        if (availableToAdd.length === 0) {
            this.showError('All agents are already active');
            return;
        }

        // Simple prompt for now (can be enhanced with a proper modal)
        const agentList = availableToAdd.map((a, i) => `${i + 1}. ${a.name} (${a.id})`).join('\n');
        const selection = prompt(`Enter agent numbers to add (comma-separated):\n\n${agentList}`);

        if (selection) {
            const indices = selection.split(',').map(s => parseInt(s.trim()) - 1);
            const agentsToAdd = indices
                .filter(i => i >= 0 && i < availableToAdd.length)
                .map(i => availableToAdd[i].id);

            if (agentsToAdd.length > 0) {
                this.modifyAgents('add', agentsToAdd);
            }
        }
    }

    showRemoveAgentsDialog() {
        const agentList = this.selectedAgents
            .map((id, i) => {
                const agent = this.availableAgents.find(a => a.id === id);
                return `${i + 1}. ${agent ? agent.name : id} (${id})`;
            })
            .join('\n');

        const selection = prompt(`Enter agent numbers to remove (comma-separated):\n\n${agentList}`);

        if (selection) {
            const indices = selection.split(',').map(s => parseInt(s.trim()) - 1);
            const agentsToRemove = indices
                .filter(i => i >= 0 && i < this.selectedAgents.length)
                .map(i => this.selectedAgents[i]);

            if (agentsToRemove.length > 0) {
                this.modifyAgents('remove', agentsToRemove);
            }
        }
    }

    newSession() {
        // Reset everything
        this.sessionId = null;
        this.uploadedFiles = [];
        this.isGenerating = false;

        // Clear UI
        document.getElementById('promptInput').value = '';
        document.getElementById('uploadedFiles').innerHTML = '';
        this.renderContextList();
        this.clearProgress();

        // Reset messages
        const messagesContainer = document.getElementById('chatMessages');
        const systemMessages = messagesContainer.querySelectorAll('.system-message');
        messagesContainer.innerHTML = '';
        systemMessages.forEach(msg => messagesContainer.appendChild(msg.cloneNode(true)));

        this.updateStatus('Ready', 'success');
    }

    clearProgress() {
        const container = document.getElementById('progressContainer');
        container.innerHTML = '<div class="no-progress"><p>No active generation</p></div>';
    }

    updateGenerateButton(isGenerating) {
        const btn = document.getElementById('generateBtn');
        btn.disabled = isGenerating;
        btn.textContent = isGenerating ? '⏳ Generating...' : '🚀 Generate Scene';
    }

    updateStatus(text, type = 'info') {
        const indicator = document.getElementById('statusIndicator');
        const statusText = indicator.querySelector('.status-text');
        const statusDot = indicator.querySelector('.status-dot');

        statusText.textContent = text;

        // Update dot color
        statusDot.style.background = {
            'success': '#10b981',
            'error': '#ef4444',
            'info': '#3b82f6',
            'warning': '#f59e0b'
        }[type] || '#10b981';
    }

    showError(message) {
        this.addMessage('system', `⚠️ Error: ${message}`);
    }

    formatStageName(stage) {
        return stage
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
let voxelApp;
document.addEventListener('DOMContentLoaded', () => {
    voxelApp = new VoxelApp();
});
