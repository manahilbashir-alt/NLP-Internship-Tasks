import "./ChatMessage.css";

function ChatMessage({
    role,
    content,
    onCopy,
    copied,
    onRegenerate,
    canRegenerate,
}) {
    const isUser = role === "user";

    return (
        <div
            className={`message-row ${
                isUser ? "user" : "assistant"
            }`}
        >
            {/* Avatar */}

            <div
                className="message-avatar"
                aria-hidden="true"
            >
                {isUser ? "Y" : "A"}
            </div>

            {/* Message */}

            <div className="message-body">

                <div className="message-label">
                    {isUser
                        ? "You"
                        : "Assistant"}
                </div>

                <div className="message-text">
                    {content}
                </div>

                {/* Actions */}

                <div className="message-actions">

                    {/* Copy */}

                    <button
                        type="button"
                        className="message-action"
                        onClick={onCopy}
                        title="Copy message"
                    >
                        {copied
                            ? "Copied!"
                            : "Copy"}
                    </button>

                    {/* Regenerate */}

                    {!isUser &&
                        canRegenerate && (
                            <button
                                type="button"
                                className="message-action"
                                onClick={
                                    onRegenerate
                                }
                                title="Regenerate response"
                            >
                                Regenerate
                            </button>
                        )}

                </div>
            </div>
        </div>
    );
}

export default ChatMessage;
