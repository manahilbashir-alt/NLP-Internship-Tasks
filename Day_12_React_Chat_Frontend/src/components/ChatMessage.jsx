import "./ChatMessage.css";

function ChatMessage({ role, content }) {
    return (
        <div className={`message ${role}`}>
            {content}
        </div>
    );
}

export default ChatMessage;