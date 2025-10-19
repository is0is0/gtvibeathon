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
    const socketRef = useRef(null)

    // ✅ Initialize socket - simpler version
    useEffect(() => {
        setDebugInfo("🔌 Starting connection...")
        console.log("🔌 Starting connection to backend...")

        // Connect directly with Socket.IO (skip health check for now)
        const socket = io(
            "https://jacque-seborrheic-nonaltruistically.ngrok-free.dev",
            {
                transports: ["websocket", "polling"],
                path: "/socket.io/",
                timeout: 10000,
                reconnection: true,
                reconnectionAttempts: 5,
                reconnectionDelay: 2000,
            }
        )

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

        socket.on("generation-complete", (data) => {
            console.log("✅ Generation complete:", data)
            setResponse(data)
            setLoading(false)
        })

        socket.on("generation-error", (msg) => {
            console.error("❌ Generation error:", msg)
            setError(msg)
            setLoading(false)
        })

        socket.on("progress", (data) => {
            console.log("📊 Progress:", data)
            setDebugInfo(`📊 ${data.message || "Processing..."}`)
        })

        return () => {
            console.log("🔌 Cleaning up socket connection")
            socket.disconnect()
        }
    }, [])

    const handleSubmit = async () => {
        if (!prompt.trim()) return
        if (!socketRef.current || !connected) {
            setError("Not connected to server. Please wait...")
            return
        }

        console.log("📤 Sending prompt:", prompt)
        setLoading(true)
        setError(null)
        setResponse(null)

        try {
            socketRef.current.emit("generate", {
                prompt: prompt,
                agents: props.selectedAgents || [
                    "concept",
                    "builder",
                    "texture",
                    "render",
                ],
            })
            setDebugInfo("📤 Generation started...")
        } catch (err) {
            console.error("❌ Emit error:", err)
            setError(err.message)
            setLoading(false)
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
