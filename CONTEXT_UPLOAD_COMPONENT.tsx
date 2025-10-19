import { addPropertyControls, ControlType } from "framer"
import { useState, useEffect, useRef } from "react"

// ✅ Load socket.io-client from CDN (no npm install needed)
import { io } from "https://cdn.jsdelivr.net/npm/socket.io-client@4.5.4/dist/socket.io.esm.min.js"

interface UploadedFile {
    filename: string
    path: string
    type: string
    metadata: any
    assignedAgents?: string[]
    confidence?: number
}

interface AgentAssignment {
    agentId: string
    agentName: string
    confidence: number
    reason: string
}

export default function ContextUpload(props) {
    const [files, setFiles] = useState<UploadedFile[]>([])
    const [isDragOver, setIsDragOver] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [connected, setConnected] = useState(false)
    const [aiAssignments, setAiAssignments] = useState<
        Map<string, AgentAssignment[]>
    >(new Map())
    const fileInputRef = useRef<HTMLInputElement>(null)
    const socketRef = useRef(null)

    // ✅ Initialize socket connection
    useEffect(() => {
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
        })

        socket.on("disconnect", (reason) => {
            console.warn("⚠️ Disconnected:", reason)
            setConnected(false)
        })

        socket.on("connect_error", (err) => {
            console.error("❌ Connection error:", err.message)
            setConnected(false)
        })

        socket.on("context-assigned", (data) => {
            console.log("🎯 AI Context Assignment:", data)
            setAiAssignments((prev) => {
                const newMap = new Map(prev)
                newMap.set(data.file_id, data.assignments)
                return newMap
            })
        })

        return () => {
            console.log("🔌 Cleaning up socket connection")
            socket.disconnect()
        }
    }, [])

    const handleFileSelect = (selectedFiles: FileList) => {
        if (selectedFiles.length === 0) return

        setUploading(true)

        // Process each file
        Array.from(selectedFiles).forEach(async (file) => {
            await uploadFile(file)
        })
    }

    const uploadFile = async (file: File) => {
        try {
            const formData = new FormData()
            formData.append("files", file)
            formData.append("enable_ai_assignment", "true") // Enable AI agent assignment

            const response = await fetch(
                "https://jacque-seborrheic-nonaltruistically.ngrok-free.dev/api/upload",
                {
                    method: "POST",
                    body: formData,
                }
            )

            const data = await response.json()

            if (data.errors && data.errors.length > 0) {
                throw new Error(data.errors[0])
            }

            if (data.uploaded && data.uploaded.length > 0) {
                const uploadedFile = data.uploaded[0]

                // Add AI assignment info if available
                if (
                    data.ai_assignments &&
                    data.ai_assignments[uploadedFile.filename]
                ) {
                    setAiAssignments((prev) => {
                        const newMap = new Map(prev)
                        newMap.set(
                            uploadedFile.filename,
                            data.ai_assignments[uploadedFile.filename]
                        )
                        return newMap
                    })
                }

                setFiles((prev) => [...prev, uploadedFile])
            }
        } catch (error) {
            console.error("❌ Upload error:", error)
        } finally {
            setUploading(false)
        }
    }

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(true)
    }

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)

        const droppedFiles = e.dataTransfer.files
        handleFileSelect(droppedFiles)
    }

    const removeFile = (filename: string) => {
        setFiles((prev) => prev.filter((f) => f.filename !== filename))
        setAiAssignments((prev) => {
            const newMap = new Map(prev)
            newMap.delete(filename)
            return newMap
        })
    }

    const getFileIcon = (fileType: string) => {
        switch (fileType) {
            case "3d_model":
                return "🎲"
            case "image":
                return "🖼️"
            case "video":
                return "🎥"
            case "text":
                return "📄"
            default:
                return "📁"
        }
    }

    return (
        <div
            style={{
                width: "100%",
                fontFamily: "Inter, sans-serif",
                padding: "16px",
                background: "rgba(255, 255, 255, 0.03)",
                borderRadius: "12px",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "white",
                minHeight: "120px",
                display: "flex",
                flexDirection: "column",
            }}
        >
            {/* Header */}
            <div style={{ marginBottom: "12px" }}>
                <h3
                    style={{
                        color: "#FFFFFF",
                        fontSize: "16px",
                        fontWeight: 600,
                        margin: "0 0 4px 0",
                    }}
                >
                    context upload
                </h3>
                <p
                    style={{
                        color: "rgba(255, 255, 255, 0.6)",
                        fontSize: "12px",
                        margin: 0,
                    }}
                >
                    drag & drop files or click to browse
                </p>
            </div>

            {/* Upload Area */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                    border: isDragOver
                        ? "1px solid #E61042"
                        : files.length > 0
                        ? "1px solid #4ADE80"
                        : "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "12px",
                    padding: "12px 16px",
                    textAlign: "center",
                    cursor: "pointer",
                    transition: "all 0.25s ease",
                    background: isDragOver
                        ? "rgba(230, 16, 66, 0.1)"
                        : files.length > 0
                        ? "rgba(74, 222, 128, 0.1)"
                        : "rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(10px)",
                    boxShadow: isDragOver
                        ? "0 0 4px 2px rgba(230, 16, 66, 0.5)"
                        : files.length > 0
                        ? "0 0 4px 2px rgba(74, 222, 128, 0.5)"
                        : "none",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    flex: 1,
                    minHeight: "60px",
                }}
            >
                {/* Attachment Icon when files are uploaded */}
                {files.length > 0 && (
                    <div
                        style={{
                            fontSize: "20px",
                            color: "#4ADE80",
                            display: "flex",
                            alignItems: "center",
                            gap: "4px",
                        }}
                    >
                        <svg
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="#4ADE80"
                        >
                            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49" />
                        </svg>
                        <span style={{ fontSize: "12px", fontWeight: "600" }}>
                            {files.length}
                        </span>
                    </div>
                )}

                {/* Upload Icon */}
                <div style={{ fontSize: "16px", opacity: files.length > 0 ? 0.6 : 1 }}>
                    {uploading ? (
                        <div
                            style={{
                                width: "16px",
                                height: "16px",
                                border: "2px solid white",
                                borderTopColor: "transparent",
                                borderRadius: "50%",
                                animation: "spin 1s linear infinite",
                            }}
                        />
                    ) : (
                        <svg
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="white"
                        >
                            <path
                                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                                stroke="white"
                                strokeWidth="2"
                                fill="none"
                            />
                            <polyline
                                points="14,2 14,8 20,8"
                                stroke="white"
                                strokeWidth="2"
                                fill="none"
                            />
                            <line
                                x1="12"
                                y1="18"
                                x2="12"
                                y2="12"
                                stroke="white"
                                strokeWidth="2"
                                strokeLinecap="round"
                            />
                            <polyline
                                points="9,15 12,12 15,15"
                                stroke="white"
                                strokeWidth="2"
                                fill="none"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            />
                        </svg>
                    )}
                </div>

                {/* Upload Text */}
                <div style={{ flex: 1, textAlign: "left" }}>
                    <div
                        style={{
                            color: "white",
                            fontSize: "14px",
                            fontWeight: "600",
                            marginBottom: "2px",
                        }}
                    >
                        {uploading ? "uploading..." : files.length > 0 ? `${files.length} file${files.length > 1 ? 's' : ''} attached` : "upload context files"}
                    </div>
                    {files.length === 0 && (
                        <div
                            style={{
                                color: "rgba(255, 255, 255, 0.6)",
                                fontSize: "11px",
                            }}
                        >
                            supports: 3D models, images, videos, text
                        </div>
                    )}
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".blend,.obj,.fbx,.dae,.gltf,.glb,.stl,.ply,.3ds,.x3d,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.webp,.exr,.hdr,.mp4,.avi,.mov,.mkv,.webm,.flv,.txt,.md,.json,.yaml,.yml,.xml"
                    style={{ display: "none" }}
                    onChange={(e) =>
                        e.target.files && handleFileSelect(e.target.files)
                    }
                />
            </div>

            {/* Uploaded Files List (Compact) */}
            {files.length > 0 && (
                <div
                    style={{
                        marginTop: "12px",
                        maxHeight: "120px",
                        overflowY: "auto",
                    }}
                >
                    {files.map((file, index) => (
                        <div
                            key={file.filename}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                padding: "6px 8px",
                                background: "rgba(255, 255, 255, 0.05)",
                                borderRadius: "6px",
                                marginBottom: "4px",
                                border: "1px solid rgba(255, 255, 255, 0.1)",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "8px",
                                    flex: 1,
                                    minWidth: 0,
                                }}
                            >
                                <span style={{ fontSize: "12px" }}>
                                    {getFileIcon(file.type)}
                                </span>
                                <div style={{ minWidth: 0, flex: 1 }}>
                                    <div
                                        style={{
                                            color: "white",
                                            fontSize: "11px",
                                            fontWeight: "500",
                                            overflow: "hidden",
                                            textOverflow: "ellipsis",
                                            whiteSpace: "nowrap",
                                        }}
                                    >
                                        {file.filename}
                                    </div>
                                    <div
                                        style={{
                                            color: "rgba(255, 255, 255, 0.6)",
                                            fontSize: "9px",
                                        }}
                                    >
                                        {file.type} •{" "}
                                        {file.metadata?.size
                                            ? (
                                                  file.metadata.size /
                                                  1024 /
                                                  1024
                                              ).toFixed(1)
                                            : "0"}{" "}
                                        MB
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={() => removeFile(file.filename)}
                                style={{
                                    background: "rgba(255, 0, 0, 0.2)",
                                    border: "1px solid rgba(255, 0, 0, 0.3)",
                                    borderRadius: "4px",
                                    padding: "2px 6px",
                                    color: "#FF6B6B",
                                    fontSize: "10px",
                                    cursor: "pointer",
                                    transition: "all 0.2s",
                                    flexShrink: 0,
                                }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.background =
                                        "rgba(255, 0, 0, 0.3)"
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.background =
                                        "rgba(255, 0, 0, 0.2)"
                                }}
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}

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

addPropertyControls(ContextUpload, {
    enableAiAssignment: {
        type: ControlType.Boolean,
        title: "Enable AI Assignment",
        defaultValue: true,
    },
    maxFileSize: {
        type: ControlType.Number,
        title: "Max File Size (MB)",
        defaultValue: 100,
        min: 1,
        max: 500,
    },
    allowedTypes: {
        type: ControlType.Array,
        title: "Allowed File Types",
        control: { type: ControlType.String },
        defaultValue: ["3d_model", "image", "video", "text"],
    },
})
