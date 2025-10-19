import { addPropertyControls, ControlType } from "framer"
import { useState, useEffect, useRef } from "react"

// ✅ Load socket.io-client from CDN (no npm install needed)
import { io } from "https://cdn.jsdelivr.net/npm/socket.io-client@4.8.1/dist/socket.io.esm.min.js"

export default function ChatInput(props) {
    const [prompt, setPrompt] = useState("")
    const [loading, setLoading] = useState(false)
    const [response, setResponse] = useState(null)
    const [error, setError] = useState(null)
    const [isFocused, setIsFocused] = useState(false)
    const [connected, setConnected] = useState(false)
    const [debugInfo, setDebugInfo] = useState("")
    const [currentSessionId, setCurrentSessionId] = useState(null)
    const socketRef = useRef(null)
    const pollingIntervalRef = useRef(null)

    const BACKEND_URL = "http://localhost:5002"

    // ✅ Initialize socket connection for real-time updates
    useEffect(() => {
        setDebugInfo("🔌 Starting connection...")
        console.log("🔌 Starting connection to backend...")

        const socket = io(BACKEND_URL, {
            transports: ["websocket", "polling"],
            path: "/socket.io/",
            timeout: 10000,
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 2000,
        })

        socketRef.current = socket

        socket.on("connect", () => {
            console.log("✅ Socket connected! ID:", socket.id)
            setConnected(true)
            setError(null)
            setDebugInfo(`✅ Connected! ID: ${socket.id}`)
        })

        socket.on("disconnect", (reason) => {
            console.warn("⚠️ Disconnected:", reason)
            setConnected(false)
            setDebugInfo(`⚠️ Disconnected: ${reason}`)
        })

        socket.on("connect_error", (err) => {
            console.error("❌ Connection error:", err.message)
            setConnected(false)
            setError(`Connection error: ${err.message}`)
            setDebugInfo(`❌ Error: ${err.message}`)
        })

        // Listen for progress updates
        socket.on("progress", (data) => {
            console.log("📊 Progress:", data)
            setDebugInfo(`📊 ${data.stage}: ${data.message || "Processing..."}`)
        })

        // Listen for completion
        socket.on("complete", (data) => {
            console.log("✅ Generation complete:", data)
            setResponse(data)
            setLoading(false)
            setDebugInfo("✅ Generation complete!")
            stopPolling()
        })

        // Listen for errors
        socket.on("error", (data) => {
            console.error("❌ Generation error:", data)
            setError(data.error || "Generation failed")
            setLoading(false)
            setDebugInfo(`❌ Error: ${data.error}`)
            stopPolling()
        })

        return () => {
            console.log("🔌 Cleaning up socket connection")
            socket.disconnect()
            stopPolling()
        }
    }, [])

    // Polling fallback to check session status
    const startPolling = (sessionId) => {
        console.log("🔄 Starting polling for session:", sessionId)

        pollingIntervalRef.current = setInterval(async () => {
            try {
                const response = await fetch(`${BACKEND_URL}/api/session/${sessionId}`)
                const data = await response.json()

                console.log("🔄 Poll update:", data.status)

                if (data.status === "completed") {
                    console.log("✅ Session completed via polling!")
                    setResponse(data)
                    setLoading(false)
                    setDebugInfo("✅ Generation complete!")
                    stopPolling()
                } else if (data.status === "failed") {
                    console.error("❌ Session failed:", data.result?.error)
                    setError(data.result?.error || "Generation failed")
                    setLoading(false)
                    setDebugInfo(`❌ Failed: ${data.result?.error}`)
                    stopPolling()
                } else {
                    // Update progress
                    setDebugInfo(`📊 ${data.current_stage || data.status}...`)
                }
            } catch (err) {
                console.error("❌ Polling error:", err)
            }
        }, 3000) // Poll every 3 seconds
    }

    const stopPolling = () => {
        if (pollingIntervalRef.current) {
            console.log("⏹️ Stopping polling")
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
        }
    }

    const handleSubmit = async () => {
        if (!prompt.trim()) return

        console.log("📤 Sending prompt:", prompt)
        setLoading(true)
        setError(null)
        setResponse(null)
        setDebugInfo("📤 Starting generation...")

        try {
            // Use REST API to start generation
            const response = await fetch(`${BACKEND_URL}/api/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: prompt,
                    agents: props.selectedAgents || [
                        "concept",
                        "builder",
                        "texture",
                        "render",
                    ],
                    context_files: [],
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()
            console.log("✅ Generation started:", data)

            const sessionId = data.session_id
            setCurrentSessionId(sessionId)
            setDebugInfo(`📊 Generation started! Session: ${sessionId.slice(0, 8)}...`)

            // Join the session room for real-time updates
            if (socketRef.current && connected) {
                console.log("🔗 Joining session room:", sessionId)
                socketRef.current.emit("join_session", { session_id: sessionId })
            }

            // Start polling as fallback
            startPolling(sessionId)

        } catch (err) {
            console.error("❌ Submit error:", err)
            setError(err.message || "Failed to start generation")
            setLoading(false)
            setDebugInfo(`❌ Error: ${err.message}`)
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
        if (loading) {
            return {
                color: "#E61042",
                text: debugInfo || "generating...",
                pulse: true,
            }
        } else if (connected) {
            return {
                color: "#4ADE80",
                text: "connected to voxel server",
                pulse: false,
            }
        } else {
            return {
                color: "#666",
                text: "connecting...",
                pulse: true,
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

            {/* Error Message */}
            {error && (
                <div
                    style={{
                        color: "#EF4444",
                        fontSize: "14px",
                        padding: "12px",
                        background: "rgba(239, 68, 68, 0.1)",
                        borderRadius: "8px",
                        border: "1px solid rgba(239, 68, 68, 0.3)",
                        textAlign: "center",
                    }}
                >
                    ✗ {error}
                </div>
            )}

            {/* Success Message */}
            {response && response.success && (
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
