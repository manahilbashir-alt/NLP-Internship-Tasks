import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import MessageInput from "./components/MessageInput";
import { useLocalStorage } from "./hooks/useLocalStorage";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function createSession() {
    const now = new Date().toISOString();

    return {
        id: crypto.randomUUID(),
        title: "New Chat",
        titlePending: false,
        createdAt: now,
        updatedAt: now,
        messages: [],
    };
}

function App() {
    const [sessions, setSessions] = useLocalStorage(
        "chat.sessions",
        () => [createSession()]
    );

    const [activeSessionId, setActiveSessionId] =
        useLocalStorage(
            "chat.activeSessionId",
            sessions[0]?.id ?? null
        );

    const [typingSessions, setTypingSessions] =
        useState({});

    const requestIds = useRef({});

    const [copiedMessageId, setCopiedMessageId] =
        useState(null);

    const messagesEndRef = useRef(null);

    const activeSession = sessions.find(
        (session) => session.id === activeSessionId
    );

    const isTyping =
        activeSessionId &&
        Boolean(typingSessions[activeSessionId]);

    useEffect(() => {
        if (sessions.length === 0) {
            const newSession = createSession();

            setSessions([newSession]);
            setActiveSessionId(newSession.id);

            return;
        }

        const exists = sessions.some(
            (session) =>
                session.id === activeSessionId
        );

        if (!exists) {
            setActiveSessionId(sessions[0].id);
        }
    }, [
        sessions,
        activeSessionId,
        setSessions,
        setActiveSessionId,
    ]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [
        activeSession?.messages.length,
        isTyping,
    ]);

    function updateSession(sessionId, updater) {
        setSessions((previousSessions) =>
            previousSessions.map((session) =>
                session.id === sessionId
                    ? updater(session)
                    : session
            )
        );
    }

    function setSessionTyping(sessionId, value) {
        setTypingSessions((previous) => ({
            ...previous,
            [sessionId]: value,
        }));
    }

    function handleNewChat() {
        const newSession = createSession();

        setSessions((previousSessions) => [
            newSession,
            ...previousSessions,
        ]);

        setActiveSessionId(newSession.id);
    }

    function handleDeleteSession(sessionId) {
        setSessions((previousSessions) => {
            const remainingSessions =
                previousSessions.filter(
                    (session) =>
                        session.id !== sessionId
                );

            if (
                sessionId === activeSessionId
            ) {
                if (remainingSessions.length > 0) {
                    setActiveSessionId(
                        remainingSessions[0].id
                    );
                } else {
                    const newSession =
                        createSession();

                    setActiveSessionId(
                        newSession.id
                    );

                    return [newSession];
                }
            }

            return remainingSessions;
        });

        setTypingSessions((previous) => {
            const updated = {
                ...previous,
            };

            delete updated[sessionId];

            return updated;
        });

        delete requestIds.current[sessionId];
    }

    async function handleSelectSession(sessionId) {
        setActiveSessionId(sessionId);

        try {
            const response = await fetch(
                `${API_BASE}/api/sessions/${sessionId}`
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            if (!Array.isArray(data.history)) {
                return;
            }

            const backendMessages =
                data.history.filter(
                    (message) =>
                        message.role !== "system"
                );

            updateSession(
                sessionId,
                (session) => ({
                    ...session,
                    messages:
                        backendMessages.map(
                            (message) => ({
                                id: crypto.randomUUID(),
                                role: message.role,
                                content:
                                    message.content,
                            })
                        ),
                    updatedAt:
                        new Date().toISOString(),
                })
            );
        } catch (error) {
            console.warn(
                "Could not load backend session:",
                error
            );
        }
    }

    async function sendChatRequest(
        sessionId,
        message,
        requestId
    ) {
        const response = await fetch(
            `${API_BASE}/api/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message,
                }),
            }
        );

        if (!response.ok) {
            let errorMessage =
                `Request failed with status ${response.status}`;

            try {
                const errorData =
                    await response.json();

                if (errorData.detail) {
                    errorMessage =
                        typeof errorData.detail ===
                        "string"
                            ? errorData.detail
                            : JSON.stringify(
                                  errorData.detail
                              );
                }
            } catch {
                //
            }

            throw new Error(errorMessage);
        }

        const data = await response.json();

        if (
            requestIds.current[sessionId] !==
            requestId
        ) {
            return null;
        }

        return data.response;
    }

    async function generateTitle(
        sessionId,
        message
    ) {
        try {
            const response = await fetch(
                `${API_BASE}/api/chat/title`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Title generation failed"
                );
            }

            const data =
                await response.json();

            if (
                data.title &&
                typeof data.title ===
                    "string"
            ) {
                updateSession(
                    sessionId,
                    (session) => ({
                        ...session,
                        title: data.title,
                        titlePending: false,
                    })
                );

                return;
            }

            throw new Error(
                "Invalid title response"
            );
        } catch (error) {
            console.warn(
                "Title generation failed:",
                error
            );

            const fallbackTitle = message
                .trim()
                .split(/\s+/)
                .slice(0, 5)
                .join(" ");

            updateSession(
                sessionId,
                (session) => ({
                    ...session,
                    title:
                        fallbackTitle ||
                        "New Chat",
                    titlePending: false,
                })
            );
        }
    }

    async function handleSend(message) {
        const sessionId =
            activeSessionId;

        if (!sessionId || isTyping) {
            return;
        }

        const trimmedMessage =
            message.trim();

        if (!trimmedMessage) {
            return;
        }

        const currentSession =
            sessions.find(
                (session) =>
                    session.id === sessionId
            );

        if (!currentSession) {
            return;
        }

        const isFirstMessage =
            currentSession.messages.length ===
            0;

        const requestId =
            crypto.randomUUID();

        requestIds.current[sessionId] =
            requestId;

        updateSession(
            sessionId,
            (session) => ({
                ...session,
                updatedAt:
                    new Date().toISOString(),
                messages: [
                    ...session.messages,
                    {
                        id: crypto.randomUUID(),
                        role: "user",
                        content:
                            trimmedMessage,
                    },
                ],
            })
        );

        setSessionTyping(
            sessionId,
            true
        );

        if (isFirstMessage) {
            updateSession(
                sessionId,
                (session) => ({
                    ...session,
                    titlePending: true,
                })
            );

            generateTitle(
                sessionId,
                trimmedMessage
            );
        }

        try {
            const assistantResponse =
                await sendChatRequest(
                    sessionId,
                    trimmedMessage,
                    requestId
                );

            if (
                assistantResponse === null
            ) {
                return;
            }

            updateSession(
                sessionId,
                (session) => ({
                    ...session,
                    updatedAt:
                        new Date().toISOString(),
                    messages: [
                        ...session.messages,
                        {
                            id: crypto.randomUUID(),
                            role: "assistant",
                            content:
                                assistantResponse,
                        },
                    ],
                })
            );
        } catch (error) {
            console.error(
                "Chat request error:",
                error
            );

            updateSession(
                sessionId,
                (session) => ({
                    ...session,
                    messages: [
                        ...session.messages,
                        {
                            id: crypto.randomUUID(),
                            role: "assistant",
                            content:
                                "Something went wrong. Please check that the FastAPI server is running.",
                            isError: true,
                        },
                    ],
                })
            );
        } finally {
            setSessionTyping(
                sessionId,
                false
            );
        }
    }

    async function handleCopy(
        content,
        messageId
    ) {
        try {
            await navigator.clipboard.writeText(
                content
            );

            setCopiedMessageId(messageId);

            setTimeout(() => {
                setCopiedMessageId(null);
            }, 1500);
        } catch (error) {
            console.error(
                "Copy failed:",
                error
            );
        }
    }

    async function handleRegenerate() {
        const sessionId =
            activeSessionId;

        if (!sessionId || isTyping) {
            return;
        }

        const currentSession =
            sessions.find(
                (session) =>
                    session.id === sessionId
            );

        if (!currentSession) {
            return;
        }

        const messages =
            currentSession.messages;

        let lastUserIndex = -1;

        for (
            let index =
                messages.length - 1;
            index >= 0;
            index--
        ) {
            if (
                messages[index].role ===
                "user"
            ) {
                lastUserIndex = index;
                break;
            }
        }

        if (lastUserIndex === -1) {
            return;
        }

        const requestId =
            crypto.randomUUID();

        requestIds.current[sessionId] =
            requestId;

        setSessionTyping(
            sessionId,
            true
        );

        try {
            const response = await fetch(
                `${API_BASE}/api/chat/regenerate`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        session_id:
                            sessionId,
                    }),
                }
            );

            if (!response.ok) {
                let errorMessage =
                    "Regeneration failed.";

                try {
                    const errorData =
                        await response.json();

                    if (errorData.detail) {
                        errorMessage =
                            typeof errorData.detail ===
                            "string"
                                ? errorData.detail
                                : JSON.stringify(
                                      errorData.detail
                                  );
                    }
                } catch {
                    //
                }

                throw new Error(
                    errorMessage
                );
            }

            const data =
                await response.json();

            if (
                requestIds.current[
                    sessionId
                ] !== requestId
            ) {
                return;
            }

            updateSession(
                sessionId,
                (session) => {
                    const updatedMessages =
                        session.messages.slice(
                            0,
                            lastUserIndex + 1
                        );

                    updatedMessages.push({
                        id: crypto.randomUUID(),
                        role: "assistant",
                        content:
                            data.response,
                    });

                    return {
                        ...session,
                        updatedAt:
                            new Date().toISOString(),
                        messages:
                            updatedMessages,
                    };
                }
            );
        } catch (error) {
            console.error(
                "Regeneration failed:",
                error
            );
        } finally {
            setSessionTyping(
                sessionId,
                false
            );
        }
    }

    if (!activeSession) {
        return null;
    }

    return (
        <div className="app">

            <Sidebar
                sessions={sessions}
                activeSessionId={
                    activeSessionId
                }
                onSelect={
                    handleSelectSession
                }
                onNewChat={
                    handleNewChat
                }
                onDeleteSession={
                    handleDeleteSession
                }
            />

            <div className="chat-container">

                <header className="chat-header">

                    <div>
                        <h1>
                            {activeSession.titlePending
                                ? "Creating title..."
                                : activeSession.title}
                        </h1>

                        <p>
                            {
                                activeSession
                                    .messages
                                    .length
                            }{" "}
                            message
                            {activeSession
                                .messages
                                .length === 1
                                ? ""
                                : "s"}
                        </p>
                    </div>

                    <div className="status">
                        <span className="status-dot"></span>
                        Online
                    </div>

                </header>

                <main className="chat-messages">

                    {activeSession.messages
                        .length === 0 && (
                        <div className="empty-state">

                            <div className="empty-icon">
                                ✦
                            </div>

                            <h2>
                                Start writing
                            </h2>

                            <p>
                                Begin a new
                                conversation
                                whenever you're
                                ready.
                            </p>

                        </div>
                    )}

                    {activeSession.messages.map(
                        (
                            message,
                            index
                        ) => (
                            <ChatMessage
                                key={
                                    message.id ||
                                    `${activeSession.id}-${index}`
                                }
                                role={
                                    message.role
                                }
                                content={
                                    message.content
                                }
                                onCopy={() =>
                                    handleCopy(
                                        message.content,
                                        message.id
                                    )
                                }
                                copied={
                                    copiedMessageId ===
                                    message.id
                                }
                                onRegenerate={
                                    handleRegenerate
                                }
                                canRegenerate={
                                    message.role ===
                                        "assistant" &&
                                    index ===
                                        activeSession
                                            .messages
                                            .length -
                                            1 &&
                                    !isTyping
                                }
                            />
                        )
                    )}

                    {isTyping && (
                        <div className="typing-indicator">
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                        </div>
                    )}

                    <div
                        ref={messagesEndRef}
                    />

                </main>

                <div className="chat-input">
                    <MessageInput
                        onSend={
                            handleSend
                        }
                        disabled={
                            isTyping
                        }
                    />
                </div>

            </div>
        </div>
    );
}

export default App;