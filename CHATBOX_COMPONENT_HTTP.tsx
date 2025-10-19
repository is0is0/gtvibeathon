import { addPropertyControls, ControlType } from "framer"
import { useState, useEffect, useRef } from "react"

export default function ChatInput(props) {
    const [prompt, setPrompt] = useState("")
    const [loading, setLoading] = useState(false)
    const [response, setResponse] = useState(null)
    const [error, setError] = useState(null)
    const [isFocused, setIsFocused] = useState(false)
    const [connected, setConnected] = useState(false)
    const [generationStatus, setGenerationStatus] = useState("")
    const [currentStage, setCurrentStage] = useState("")
    const [currentAgent, setCurrentAgent] = useState("")
    const [progressMessage, setProgressMessage] = useState("")

    // Poll generation status
    const pollGenerationStatus = async (sessionId) => {
        const maxAttempts = 60 // 5 minutes max
        let attempts = 0
        
        const poll = async () => {
            try {
                const response = await fetch(`http://localhost:5002/api/session/${sessionId}`)
                const data = await response.json()
                
                if (response.ok) {
                    setGenerationStatus(data.status || "processing")
                    
                    // Update detailed progress information
                    if (data.current_stage) {
                        setCurrentStage(data.current_stage)
                    }
                    
                    // Get latest progress entry
                    if (data.progress && data.progress.length > 0) {
                        const latestProgress = data.progress[data.progress.length - 1]
                        setCurrentAgent(latestProgress.agent || "")
                        setProgressMessage(latestProgress.message || "")
                    }
                    
                    if (data.status === "completed") {
                        setResponse(data.result)
                        setLoading(false)
                        return
                    } else if (data.status === "failed") {
                        setError(data.error || "Generation failed")
                        setLoading(false)
                        return
                    }
                    
                    // Continue polling if still processing
                    if (attempts < maxAttempts) {
                        attempts++
                        setTimeout(poll, 3000) // Poll every 3 seconds for better updates
                    } else {
                        setError("Generation timeout - please try again")
                        setLoading(false)
                    }
                } else {
                    // Don't immediately fail - session might not exist yet
                    if (data.error === "Session not found") {
                        // Continue polling - session might be created soon
                        if (attempts < maxAttempts) {
                            attempts++
                            setTimeout(poll, 2000) // Poll more frequently if session not found
                        } else {
                            setError("Session not found - generation may have failed")
                            setLoading(false)
                        }
                    } else {
                        setError(`Failed to check generation status: ${data.error || response.statusText}`)
                        setLoading(false)
                    }
                }
            } catch (err) {
                console.error("Polling error:", err)
                // Don't immediately fail - might be network issue
                if (attempts < maxAttempts) {
                    attempts++
                    setTimeout(poll, 3000) // Retry after 3 seconds
                } else {
                    setError(`Error checking generation status: ${err.message}`)
                    setLoading(false)
                }
            }
        }
        
        poll()
    }

    // Check backend connection on component mount
    useEffect(() => {
        const checkConnection = async () => {
            try {
                const response = await fetch("http://localhost:5002/api/health")
                if (response.ok) {
                    setConnected(true)
                    setError(null)
                } else {
                    setConnected(false)
                    setError("Backend not responding")
                }
            } catch (err) {
                setConnected(false)
                setError("Cannot connect to backend")
            }
        }

        checkConnection()
        // Check connection every 30 seconds
        const interval = setInterval(checkConnection, 30000)
        return () => clearInterval(interval)
    }, [])

    const handleSubmit = async () => {
        if (!prompt.trim()) return
        if (!connected) {
            setError("Not connected to server. Please wait...")
            return
        }

        console.log("📤 Sending prompt:", prompt)
        setLoading(true)
        setError(null)
        setResponse(null)

        try {
            const response = await fetch("http://localhost:5002/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt: prompt,
                    agents: props.selectedAgents || [
                        "concept",
                        "builder",
                        "texture",
                        "render",
                    ],
                }),
            })

            const data = await response.json()
            
            if (response.ok) {
                // Don't show success immediately - generation is just starting
                console.log("✅ Generation started:", data)
                
                // Start polling for completion - keep loading until done
                pollGenerationStatus(data.session_id)
            } else {
                setError(data.error || "Generation failed")
                console.error("❌ Generation error:", data)
                setLoading(false) // Only stop loading on error
            }
        } catch (err) {
            console.error("❌ Request error:", err)
            setError(err.message)
            setLoading(false) // Only stop loading on error
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSubmit()
        }
    }

    // Determine connection status and color
    const getConnectionStatus = () => {
        if (connected) {
            return {
                color: "#4ADE80", // Green when connected
                text: "connected to voxel server",
                pulse: false
            }
        } else if (loading) {
            return {
                color: "#E61042", // Red while connecting/generating
                text: "connecting to server...",
                pulse: true
            }
        } else {
            return {
                color: "#666", // Grey when not connected
                text: "disconnected",
                pulse: false
            }
        }
    }

    const connectionStatus = getConnectionStatus()

    return (
        <div
            style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                gap: "20px",
                fontFamily: "Inter, sans-serif",
            }}
        >
            {/* Chat Input */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    background: "rgba(255, 255, 255, 0.05)",
                    border: isFocused
                        ? "1px solid #E61042"
                        : "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "12px",
                    padding: "4px",
                    backdropFilter: "blur(10px)",
                    boxShadow: isFocused
                        ? "0 0 4px 2px rgba(230, 16, 66, 0.5)"
                        : "none",
                    transition: "all 0.25s ease",
                }}
            >
                <input
                    type="text"
                    placeholder="create a 3D scene of..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyPress={handleKeyPress}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    disabled={loading}
                    style={{
                        flex: 1,
                        background: "transparent",
                        border: "none",
                        outline: "none",
                        color: "white",
                        fontSize: "16px",
                        padding: "16px 20px",
                        fontFamily: "inherit",
                    }}
                />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !prompt.trim()}
                    style={{
                        background: loading ? "#666" : "#333",
                        border: "none",
                        borderRadius: "8px",
                        width: "44px",
                        height: "44px",
                        cursor: loading ? "not-allowed" : "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        transition: "all 0.2s",
                        opacity: !prompt.trim() || loading ? 0.5 : 1,
                    }}
                >
                    {loading ? (
                        <div
                            style={{
                                width: "20px",
                                height: "20px",
                                border: "2px solid white",
                                borderTopColor: "transparent",
                                borderRadius: "50%",
                                animation: "spin 1s linear infinite",
                            }}
                        />
                    ) : (
                        <svg
                            width="20"
                            height="20"
                            viewBox="0 0 20 20"
                            fill="white"
                        >
                            <path
                                d="M10 3L10 17M10 17L15 12M10 17L5 12"
                                stroke="white"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            />
                        </svg>
                    )}
                </button>
            </div>

            {/* Generation Status */}
            {loading && (
                <div
                    style={{
                        color: "#8B5CF6",
                        fontSize: "14px",
                        padding: "12px",
                        background: "rgba(139, 92, 246, 0.1)",
                        borderRadius: "8px",
                        border: "1px solid rgba(139, 92, 246, 0.3)",
                        textAlign: "center",
                    }}
                >
                    {/* Basic Status */}
                    <div style={{ marginBottom: "8px" }}>
                        {generationStatus === "running" && "🔄 Generating your 3D scene..."}
                        {generationStatus === "processing" && "⚙️ Processing scene..."}
                        {generationStatus === "pending" && "⏳ Starting generation..."}
                        {generationStatus === "rate_limiting" && "⏰ Respecting rate limits - this may take a few minutes..."}
                        {!generationStatus && "🔄 Initializing..."}
                    </div>
                    
                    {/* Detailed Progress */}
                    {currentStage && (
                        <div style={{ fontSize: "12px", opacity: 0.8 }}>
                            <div><strong>Stage:</strong> {currentStage.replace(/_/g, ' ').toUpperCase()}</div>
                            {currentAgent && <div><strong>Agent:</strong> {currentAgent}</div>}
                            {progressMessage && <div><strong>Status:</strong> {progressMessage}</div>}
                        </div>
                    )}
                </div>
            )}

            {/* Success Message */}
            {response && (
                <div
                    style={{
                        color: "#4ADE80",
                        fontSize: "14px",
                        padding: "12px",
                        background: "rgba(74, 222, 128, 0.1)",
                        borderRadius: "8px",
                        border: "1px solid rgba(74, 222, 128, 0.3)",
                        textAlign: "center",
                    }}
                >
                    ✓ scene generated — check your downloads
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div
                    style={{
                        color: "#FF006E",
                        fontSize: "14px",
                        padding: "12px",
                        background: "rgba(255, 0, 110, 0.1)",
                        borderRadius: "8px",
                        border: "1px solid rgba(255, 0, 110, 0.3)",
                        textAlign: "center",
                    }}
                >
                    {error}
                </div>
            )}

            {/* Connection Status */}
            <div
                style={{
                    fontSize: "12px",
                    color: connectionStatus.color,
                    textAlign: "center",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                }}
            >
                <div
                    style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        backgroundColor: connectionStatus.color,
                        animation: connectionStatus.pulse
                            ? "pulse 1.5s ease-in-out infinite"
                            : "none",
                    }}
                />
                {connectionStatus.text}
            </div>

            <style>{`
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `}</style>
        </div>
    )
}

addPropertyControls(ChatInput, {
    selectedAgents: {
        type: ControlType.Array,
        control: { type: ControlType.String },
    },
})
