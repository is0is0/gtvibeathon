import { addPropertyControls, ControlType } from "framer"
import { useState, useEffect } from "react"

export default function DownloadSection(props) {
    const [sessionData, setSessionData] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (props.sessionId) {
            fetchSessionStatus()
        }
    }, [props.sessionId])

    const fetchSessionStatus = async () => {
        if (!props.sessionId) return
        
        setLoading(true)
        try {
            const response = await fetch(`http://localhost:5001/api/session/${props.sessionId}`)
            if (response.ok) {
                const data = await response.json()
                setSessionData(data)
            }
        } catch (error) {
            console.error('Error fetching session status:', error)
        } finally {
            setLoading(false)
        }
    }

    const downloadFile = (type) => {
        if (sessionData && sessionData.download_urls && sessionData.download_urls[type]) {
            const link = document.createElement("a")
            link.href = sessionData.download_urls[type]
            link.download = `voxel_${type}_${Date.now()}.${type === "blend" ? "blend" : "py"}`
            link.click()
        } else {
            // Fallback to props URLs
            const url = props[`${type}Url`] || "#"
            if (url !== "#") {
                const link = document.createElement("a")
                link.href = url
                link.download = `voxel_${type}_${Date.now()}.${type === "blend" ? "blend" : "py"}`
                link.click()
            }
        }
    }

    const isDownloadAvailable = (type) => {
        if (sessionData && sessionData.download_available) {
            return sessionData.download_available[type]
        }
        return props[`${type}Url`] && props[`${type}Url`] !== "#"
    }

    const Button = ({
        label,
        fileName,
        onClick,
        disabled,
        icon,
        gradient,
        borderColor,
    }) => (
        <button
            onClick={onClick}
            disabled={disabled}
            style={{
                background: disabled
                    ? "rgba(255, 255, 255, 0.05)"
                    : "rgba(20, 20, 20, 0.45)",
                border: disabled
                    ? "1px solid rgba(255,255,255,0.1)"
                    : `1px solid ${borderColor}`,
                borderRadius: "12px",
                padding: "12px 16px",
                cursor: disabled ? "not-allowed" : "pointer",
                opacity: disabled ? 0.4 : 1,
                textAlign: "left",
                color: "white",
                transition: "all 0.25s ease",
                backdropFilter: "blur(20px) saturate(180%)",
                WebkitBackdropFilter: "blur(20px) saturate(180%)",
                position: "relative",
                overflow: "hidden",
                flex: "1 1 0px",
                minWidth: "140px",
            }}
            onMouseEnter={(e) => {
                if (!disabled)
                    e.currentTarget.style.boxShadow = `0 0 10px 2px ${borderColor}55`
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = "none"
            }}
        >
            {!disabled && (
                <div
                    style={{
                        position: "absolute",
                        inset: 0,
                        borderRadius: "16px",
                        padding: "1.5px",
                        background: gradient,
                        WebkitMask:
                            "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                        WebkitMaskComposite: "xor",
                        maskComposite: "exclude",
                        pointerEvents: "none",
                    }}
                />
            )}

            <div style={{ position: "relative", zIndex: 2 }}>
                <div
                    style={{
                        width: "24px",
                        height: "24px",
                        marginBottom: "8px",
                    }}
                    dangerouslySetInnerHTML={{ __html: icon }}
                />
                <div
                    style={{
                        fontSize: "14px",
                        fontWeight: 600,
                        marginBottom: "2px",
                        color: "#FFFFFF",
                    }}
                >
                    {label}
                </div>
                <div
                    style={{
                        color: "rgba(255, 255, 255, 0.7)",
                        fontSize: "11px",
                    }}
                >
                    {fileName}
                </div>
            </div>
        </button>
    )

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
                    download your scene
                </h3>
                <p
                    style={{
                        color: "rgba(255, 255, 255, 0.6)",
                        fontSize: "12px",
                        margin: 0,
                    }}
                >
                    get your generated 3d scene and outputs
                </p>
            </div>

            {/* Horizontal Button Row */}
            <div
                style={{
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "space-between",
                    alignItems: "stretch",
                    gap: "12px",
                    flexWrap: "wrap",
                }}
            >
                <Button
                    label="Blender File"
                    fileName="scene.blend"
                    onClick={() => downloadFile("blend")}
                    disabled={!isDownloadAvailable("blend")}
                    gradient="linear-gradient(135deg, #E61042, #3639FF)"
                    borderColor="#E61042"
                    icon={`<svg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='#E61042' stroke-width='2' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' d='M12 5v14m7-7H5'/></svg>`}
                />

                <Button
                    label="Python Script"
                    fileName="complete_script.py"
                    onClick={() => downloadFile("scripts")}
                    disabled={!isDownloadAvailable("scripts")}
                    gradient="linear-gradient(135deg, #E61042, #8B5CF6)"
                    borderColor="#E61042"
                    icon={`<svg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='#E61042' stroke-width='2' viewBox='0 0 24 24'><path d='M16 18v-6H8v6m8 0H8m8 0v3H8v-3'/><path d='M6 9V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v4'/></svg>`}
                />
            </div>

            {/* Status Message and Refresh Button */}
            {!isDownloadAvailable("blend") && !isDownloadAvailable("scripts") && (
                <div
                    style={{
                        marginTop: "12px",
                        textAlign: "center",
                        color: "rgba(255, 255, 255, 0.4)",
                        fontSize: "12px",
                    }}
                >
                    {loading ? "checking for files..." : "generate a scene to download files"}
                </div>
            )}
            
            {/* Refresh Button */}
            {props.sessionId && (
                <div
                    style={{
                        marginTop: "8px",
                        textAlign: "center",
                    }}
                >
                    <button
                        onClick={fetchSessionStatus}
                        disabled={loading}
                        style={{
                            background: "rgba(54, 57, 255, 0.1)",
                            border: "1px solid rgba(54, 57, 255, 0.3)",
                            borderRadius: "6px",
                            padding: "6px 12px",
                            color: "#3639FF",
                            fontSize: "11px",
                            cursor: loading ? "not-allowed" : "pointer",
                            opacity: loading ? 0.5 : 1,
                        }}
                    >
                        {loading ? "checking..." : "refresh files"}
                    </button>
                </div>
            )}
        </div>
    )
}

addPropertyControls(DownloadSection, {
    sessionId: { type: ControlType.String, title: "Session ID" },
    blendUrl: { type: ControlType.String, title: "Blend File URL (Fallback)" },
    scriptsUrl: { type: ControlType.String, title: "Scripts URL (Fallback)" },
})
