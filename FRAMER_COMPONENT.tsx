/**
 * Voxel Generator - Complete Component for Framer
 *
 * INSTRUCTIONS:
 * 1. In Framer: Assets → + → Code Component
 * 2. Name it "VoxelGenerator"
 * 3. Copy this entire file and paste it
 * 4. Install dependency: File → Dependencies → Add "socket.io-client@4.5.4"
 * 5. Update API_URL below with your deployed backend URL
 * 6. Drag component onto your canvas
 * 7. Done!
 */

import { addPropertyControls, ControlType } from "framer"
import { useState, useEffect } from "react"
import io from 'socket.io-client'

// ⚠️ UPDATE THIS WITH YOUR DEPLOYED BACKEND URL
const API_URL = 'https://your-app.up.railway.app'  // or ngrok URL

const socket = io(API_URL)

const AGENTS = [
    { id: 'concept', name: 'Concept', emoji: '💡', description: 'Scene planning', color: '#8B5CF6' },
    { id: 'builder', name: 'Builder', emoji: '🏗️', description: 'Geometry', color: '#10B981' },
    { id: 'texture', name: 'Texture', emoji: '🎨', description: 'Materials', color: '#F59E0B' },
    { id: 'hdr', name: 'HDR', emoji: '🌅', description: 'Lighting', color: '#3B82F6' },
    { id: 'render', name: 'Render', emoji: '📸', description: 'Camera', color: '#EC4899' },
    { id: 'animation', name: 'Animation', emoji: '🎬', description: 'Movement', color: '#EF4444' }
]

export default function VoxelGenerator(props) {
    const [prompt, setPrompt] = useState("")
    const [selectedAgents, setSelectedAgents] = useState(['concept', 'builder', 'texture', 'render'])
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [progress, setProgress] = useState(null)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        socket.on('connect', () => {
            console.log('Connected to Voxel API')
        })

        socket.on('progress', (data) => {
            if (data.session_id === sessionId) {
                setProgress(data)
            }
        })

        socket.on('complete', (data) => {
            if (data.session_id === sessionId) {
                setLoading(false)
                setResult(data)
                setProgress(null)
            }
        })

        socket.on('error', (data) => {
            if (data.session_id === sessionId) {
                setLoading(false)
                setError(data.error)
                setProgress(null)
            }
        })

        return () => {
            socket.off('connect')
            socket.off('progress')
            socket.off('complete')
            socket.off('error')
        }
    }, [sessionId])

    const toggleAgent = (id) => {
        if (selectedAgents.includes(id)) {
            const newSelected = selectedAgents.filter(a => a !== id)
            if (newSelected.length > 0) { // Keep at least one agent
                setSelectedAgents(newSelected)
            }
        } else {
            setSelectedAgents([...selectedAgents, id])
        }
    }

    const handleSubmit = async () => {
        if (!prompt.trim() || selectedAgents.length === 0) return

        setLoading(true)
        setError(null)
        setResult(null)
        setProgress(null)

        try {
            const res = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt.trim(),
                    agents: selectedAgents
                })
            })

            const data = await res.json()

            if (res.ok) {
                setSessionId(data.session_id)
                socket.emit('join_session', { session_id: data.session_id })
            } else {
                setError(data.error || 'Failed to start generation')
                setLoading(false)
            }

        } catch (err) {
            setError(`Connection error: ${err.message}`)
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit()
        }
    }

    const downloadFile = (fileType) => {
        if (sessionId && result?.success) {
            window.open(`${API_URL}/api/download/${sessionId}/${fileType}`, '_blank')
        }
    }

    return (
        <div style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '40px 20px',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            color: 'white'
        }}>
            {/* Title Section */}
            <div style={{ marginBottom: '48px', textAlign: 'center' }}>
                <h1 style={{
                    fontSize: '64px',
                    fontWeight: 700,
                    margin: 0,
                    background: 'linear-gradient(135deg, #FF006E, #8B5CF6)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-2px'
                }}>
                    voxel
                </h1>
                <p style={{
                    fontSize: '16px',
                    color: '#FF006E',
                    margin: '8px 0 0 0',
                    fontWeight: 500
                }}>
                    create structured blender worlds using intelligent voxel-based modeling.
                </p>
            </div>

            {/* Agent Selector */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                }}>
                    <h3 style={{
                        fontSize: '18px',
                        fontWeight: 600,
                        margin: 0,
                        color: 'white'
                    }}>
                        select agents
                    </h3>
                    <div style={{
                        fontSize: '14px',
                        color: 'rgba(255,255,255,0.6)'
                    }}>
                        {selectedAgents.length} selected
                    </div>
                </div>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
                    gap: '12px'
                }}>
                    {AGENTS.map(agent => {
                        const isSelected = selectedAgents.includes(agent.id)
                        return (
                            <button
                                key={agent.id}
                                onClick={() => toggleAgent(agent.id)}
                                disabled={loading}
                                style={{
                                    background: isSelected
                                        ? 'linear-gradient(135deg, rgba(255, 0, 110, 0.15), rgba(139, 92, 246, 0.15))'
                                        : 'rgba(255, 255, 255, 0.03)',
                                    border: isSelected
                                        ? '2px solid ' + agent.color
                                        : '1px solid rgba(255, 255, 255, 0.08)',
                                    borderRadius: '16px',
                                    padding: '20px 16px',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                    textAlign: 'center',
                                    position: 'relative',
                                    transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                                    boxShadow: isSelected ? `0 0 20px ${agent.color}40` : 'none'
                                }}
                                onMouseEnter={(e) => {
                                    if (!loading && !isSelected) {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'
                                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)'
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (!isSelected) {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
                                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)'
                                    }
                                }}
                            >
                                {isSelected && (
                                    <div style={{
                                        position: 'absolute',
                                        top: '10px',
                                        right: '10px',
                                        width: '20px',
                                        height: '20px',
                                        borderRadius: '50%',
                                        background: agent.color,
                                        fontSize: '11px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontWeight: 'bold',
                                        boxShadow: `0 2px 8px ${agent.color}60`
                                    }}>✓</div>
                                )}
                                <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                                    {agent.emoji}
                                </div>
                                <div style={{
                                    fontSize: '14px',
                                    fontWeight: 600,
                                    color: 'white',
                                    marginBottom: '4px'
                                }}>
                                    {agent.name}
                                </div>
                                <div style={{
                                    fontSize: '11px',
                                    color: 'rgba(255,255,255,0.5)',
                                    lineHeight: '1.3'
                                }}>
                                    {agent.description}
                                </div>
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Chat Input */}
            <div style={{ marginBottom: '32px' }}>
                <h3 style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    marginBottom: '12px',
                    color: 'white'
                }}>
                    what's in your world?
                </h3>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '20px',
                    padding: '8px',
                    backdropFilter: 'blur(20px)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
                }}>
                    <input
                        type="text"
                        placeholder="create a 3D scene of..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={loading}
                        style={{
                            flex: 1,
                            background: 'transparent',
                            border: 'none',
                            outline: 'none',
                            color: 'white',
                            fontSize: '16px',
                            padding: '16px 20px',
                            fontFamily: 'inherit'
                        }}
                    />
                    <button
                        onClick={handleSubmit}
                        disabled={loading || !prompt.trim() || selectedAgents.length === 0}
                        style={{
                            background: (loading || !prompt.trim() || selectedAgents.length === 0)
                                ? 'rgba(255,255,255,0.1)'
                                : 'linear-gradient(135deg, #FF006E, #8B5CF6)',
                            border: 'none',
                            borderRadius: '14px',
                            width: '52px',
                            height: '52px',
                            cursor: (loading || !prompt.trim() || selectedAgents.length === 0) ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.3s',
                            boxShadow: (loading || !prompt.trim() || selectedAgents.length === 0)
                                ? 'none'
                                : '0 4px 16px rgba(255, 0, 110, 0.4)'
                        }}
                        onMouseEnter={(e) => {
                            if (!loading && prompt.trim() && selectedAgents.length > 0) {
                                e.currentTarget.style.transform = 'scale(1.05)'
                            }
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'scale(1)'
                        }}
                    >
                        {loading ? (
                            <div className="spinner" />
                        ) : (
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                                <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* Progress */}
            {progress && (
                <div style={{
                    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(255, 0, 110, 0.1))',
                    border: '1px solid rgba(139, 92, 246, 0.3)',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '24px',
                    backdropFilter: 'blur(10px)'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '12px'
                    }}>
                        <div className="pulse-dot" />
                        <div style={{
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#8B5CF6'
                        }}>
                            {progress.agent || 'Processing'}
                        </div>
                    </div>
                    <div style={{
                        fontSize: '14px',
                        color: 'rgba(255,255,255,0.8)',
                        marginBottom: '16px'
                    }}>
                        {progress.message}
                    </div>
                    <div style={{
                        height: '6px',
                        background: 'rgba(255,255,255,0.1)',
                        borderRadius: '3px',
                        overflow: 'hidden'
                    }}>
                        <div className="progress-bar" />
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div style={{
                    background: 'rgba(255, 0, 110, 0.1)',
                    border: '1px solid rgba(255, 0, 110, 0.3)',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '24px',
                    color: '#FF006E'
                }}>
                    <strong>⚠️ Error:</strong> {error}
                </div>
            )}

            {/* Download Section */}
            {result && result.success && (
                <div style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(74, 222, 128, 0.3)',
                    borderRadius: '20px',
                    padding: '32px',
                    boxShadow: '0 0 40px rgba(74, 222, 128, 0.1)'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '8px'
                    }}>
                        <div style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #4ADE80, #22C55E)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '20px'
                        }}>✓</div>
                        <div style={{
                            fontSize: '24px',
                            fontWeight: 600,
                            color: '#4ADE80'
                        }}>
                            Scene Generated!
                        </div>
                    </div>
                    <div style={{
                        fontSize: '14px',
                        color: 'rgba(255,255,255,0.6)',
                        marginBottom: '32px',
                        paddingLeft: '52px'
                    }}>
                        Rendered in {result.render_time?.toFixed(1)}s • {result.iterations} iteration(s)
                    </div>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                        gap: '16px'
                    }}>
                        <button
                            onClick={() => downloadFile('blend')}
                            style={{
                                background: 'linear-gradient(135deg, #FF006E, #8B5CF6)',
                                border: 'none',
                                borderRadius: '16px',
                                padding: '24px',
                                cursor: 'pointer',
                                transition: 'all 0.3s',
                                textAlign: 'left',
                                boxShadow: '0 4px 16px rgba(255, 0, 110, 0.3)'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)'
                                e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 0, 110, 0.4)'
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)'
                                e.currentTarget.style.boxShadow = '0 4px 16px rgba(255, 0, 110, 0.3)'
                            }}
                        >
                            <div style={{ fontSize: '36px', marginBottom: '12px' }}>📦</div>
                            <div style={{ fontSize: '18px', fontWeight: 600, color: 'white', marginBottom: '4px' }}>
                                Blender File
                            </div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.8)' }}>
                                Complete .blend scene
                            </div>
                        </button>

                        <button
                            onClick={() => downloadFile('render')}
                            style={{
                                background: 'rgba(139, 92, 246, 0.3)',
                                border: '1px solid rgba(139, 92, 246, 0.5)',
                                borderRadius: '16px',
                                padding: '24px',
                                cursor: 'pointer',
                                transition: 'all 0.3s',
                                textAlign: 'left'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)'
                                e.currentTarget.style.background = 'rgba(139, 92, 246, 0.4)'
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)'
                                e.currentTarget.style.background = 'rgba(139, 92, 246, 0.3)'
                            }}
                        >
                            <div style={{ fontSize: '36px', marginBottom: '12px' }}>🖼️</div>
                            <div style={{ fontSize: '18px', fontWeight: 600, color: 'white', marginBottom: '4px' }}>
                                Rendered Image
                            </div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.8)' }}>
                                High-quality PNG
                            </div>
                        </button>

                        <button
                            onClick={() => downloadFile('scripts')}
                            style={{
                                background: 'rgba(255, 0, 110, 0.3)',
                                border: '1px solid rgba(255, 0, 110, 0.5)',
                                borderRadius: '16px',
                                padding: '24px',
                                cursor: 'pointer',
                                transition: 'all 0.3s',
                                textAlign: 'left'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)'
                                e.currentTarget.style.background = 'rgba(255, 0, 110, 0.4)'
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)'
                                e.currentTarget.style.background = 'rgba(255, 0, 110, 0.3)'
                            }}
                        >
                            <div style={{ fontSize: '36px', marginBottom: '12px' }}>📜</div>
                            <div style={{ fontSize: '18px', fontWeight: 600, color: 'white', marginBottom: '4px' }}>
                                Python Scripts
                            </div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.8)' }}>
                                All generated code
                            </div>
                        </button>
                    </div>
                </div>
            )}

            <style>{`
                .spinner {
                    width: 22px;
                    height: 22px;
                    border: 2.5px solid rgba(255,255,255,0.2);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                .progress-bar {
                    height: 100%;
                    background: linear-gradient(90deg, #FF006E, #8B5CF6, #FF006E);
                    background-size: 200% 100%;
                    animation: gradient-shift 2s ease-in-out infinite;
                    border-radius: 3px;
                }

                .pulse-dot {
                    width: 10px;
                    height: 10px;
                    background: #8B5CF6;
                    border-radius: 50%;
                    animation: pulse 1.5s ease-in-out infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                @keyframes gradient-shift {
                    0%, 100% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                }

                @keyframes pulse {
                    0%, 100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                    50% {
                        opacity: 0.5;
                        transform: scale(1.2);
                    }
                }
            `}</style>
        </div>
    )
}

addPropertyControls(VoxelGenerator, {})
