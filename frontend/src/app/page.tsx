"use client";

import React from "react";
import Link from "next/link";
import ChatWindow from "@/components/ChatWindow";

export default function Home() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <h1 className="app-title">RAG Chatbot</h1>
        <Link href="/data_admin" className="admin-link">
          Data Admin
        </Link>
      </header>
      <div className="app-body">
        <ChatWindow />
      </div>
    </div>
  );
}
