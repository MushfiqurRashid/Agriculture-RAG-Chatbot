"use client";

import React from "react";

interface Props {
    role: "user" | "assistant";
    content: string;
}

export default function MessageBubble({ role, content }: Props) {
    const isUser = role === "user";

    return (
        <div className={`message-row ${isUser ? "user" : "assistant"}`}>
            <div className={`avatar ${isUser ? "user-avatar" : "bot-avatar"}`}>
                {isUser ? "U" : "AI"}
            </div>
            <div className={`bubble ${isUser ? "user-bubble" : "bot-bubble"}`}>
                <div
                    className="bubble-content"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(content) }}
                />
            </div>
        </div>
    );
}

function formatMarkdown(text: string): string {
    return text
        .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/\*([^*]+)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br/>");
}
