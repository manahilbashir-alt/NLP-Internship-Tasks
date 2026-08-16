import "./Sidebar.css";

function Sidebar({
    sessions,
    activeSessionId,
    onSelect,
    onNewChat,
    onDeleteSession,
}) {
    return (
        <aside className="sidebar">

            <div className="sidebar-header">
                <div className="sidebar-brand">
                    <span className="brand-mark">✦</span>

                    <div>
                        <h2>Notebook</h2>
                        <span>Conversations</span>
                    </div>
                </div>
            </div>

            <button
                type="button"
                className="new-chat-button"
                onClick={onNewChat}
            >
                <span className="new-chat-icon">+</span>
                <span>New Chat</span>
            </button>

            <div className="session-section">

                <div className="session-section-label">
                    <span>Recent conversations</span>

                    <span className="session-count">
                        {sessions.length}
                    </span>
                </div>

                <div className="session-list">

                    {sessions.length === 0 && (
                        <div className="no-sessions">
                            No conversations yet.
                        </div>
                    )}

                    {sessions.map((session) => {
                        const isActive =
                            session.id === activeSessionId;

                        const lastMessage =
                            session.messages?.[
                                session.messages.length - 1
                            ];

                        const preview =
                            lastMessage?.content ||
                            "No messages yet";

                        return (
                            <div
                                key={session.id}
                                className={`session-item ${
                                    isActive ? "active" : ""
                                }`}
                            >

                                <button
                                    type="button"
                                    className="session-select"
                                    onClick={() =>
                                        onSelect(session.id)
                                    }
                                >
                                    <span className="session-indicator">
                                        {isActive ? "●" : "○"}
                                    </span>

                                    <span className="session-content">

                                        <span className="session-title">
                                            {session.titlePending
                                                ? "Creating title..."
                                                : session.title ||
                                                  "New Chat"}
                                        </span>

                                        <span className="session-preview">
                                            {preview}
                                        </span>

                                    </span>
                                </button>

                                <button
                                    type="button"
                                    className="session-delete"
                                    onClick={(event) => {
                                        event.stopPropagation();
                                        onDeleteSession(session.id);
                                    }}
                                    title="Delete chat"
                                    aria-label="Delete chat"
                                >
                                    ×
                                </button>

                            </div>
                        );
                    })}

                </div>
            </div>

            <div className="sidebar-footer">
                <span className="footer-dot"></span>

                <span>
                    Sessions are saved locally
                </span>
            </div>

        </aside>
    );
}

export default Sidebar;