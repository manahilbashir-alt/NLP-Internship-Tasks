import { useState } from "react";
import ChatMessage from "./components/ChatMessage";
import MessageInput from "./components/MessageInput";
import "./App.css";

function App() {
    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: "Hi! How can I help you?"
        }
    ]);

    const [isTyping, setIsTyping] = useState(false);

    async function handleSend(message) {
        setIsTyping(true);

        setMessages((previousMessages) => [
            ...previousMessages,
            {
                role: "user",
                content: message
            }
        ]);

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/api/chat",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        session_id: "react-demo-session",
                        message: message
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Failed to send message");
            }

            const data = await response.json();

            // Demo delay so typing indicator is visible
            await new Promise((resolve) => setTimeout(resolve, 1000));

            setMessages((previousMessages) => [
                ...previousMessages,
                {
                    role: "assistant",
                    content: data.response
                }
            ]);

        } catch (error) {
            console.error("Error:", error);

        } finally {
            setIsTyping(false);
        }
    }

    return (
        <div className="app">
            <div className="chat-container">

                {/* Header */}
                <header className="chat-header">
                    <div>
                        <h1>✨ AI Chat</h1>
                        <p>Your intelligent chat assistant</p>
                    </div>

                    <div className="status">
                        <span className="status-dot"></span>
                        Online
                    </div>
                </header>

                {/* Messages */}
                <main className="chat-messages">

                    {messages.map((message, index) => (
                        <ChatMessage
                            key={index}
                            role={message.role}
                            content={message.content}
                        />
                    ))}

                    {isTyping && (
                        <div className="typing-indicator">
                            <span>Assistant is typing</span>
                            <span className="dots">...</span>
                        </div>
                    )}

                </main>

                {/* Input */}
                <div className="chat-input">
                    <MessageInput onSend={handleSend} />
                </div>

            </div>
        </div>
    );
}

export default App;