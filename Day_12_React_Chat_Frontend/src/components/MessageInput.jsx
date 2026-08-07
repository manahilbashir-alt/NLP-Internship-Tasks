import { useState } from "react";
import "./MessageInput.css";

function MessageInput({ onSend }) {
    const [message, setMessage] = useState("");

    const handleSubmit = () => {
        const trimmedMessage = message.trim();

        if (trimmedMessage === "") {
            return;
        }

        onSend(trimmedMessage);
        setMessage("");
    };

    return (
        <div className="message-input-container">
            <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Type your message..."
                rows="1"
            />

            <button type="button" onClick={handleSubmit}>
                Send
            </button>
        </div>
    );
}

export default MessageInput;