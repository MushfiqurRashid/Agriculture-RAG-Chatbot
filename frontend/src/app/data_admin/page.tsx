"use client";

import React, { useCallback, useMemo, useRef, useState } from "react";
import {
  adminDeleteDocument,
  adminGetDocuments,
  adminUploadDocument,
  DocumentInfo,
} from "@/lib/api";

const DEFAULT_USERNAME = "fairfarm";
const DEFAULT_PASSWORD = "fairfarm";

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

export default function DataAdminPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [username, setUsername] = useState(DEFAULT_USERNAME);
  const [password, setPassword] = useState(DEFAULT_PASSWORD);
  const [isAuthed, setIsAuthed] = useState(false);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const canSubmit = useMemo(
    () => username.trim().length > 0 && password.trim().length > 0,
    [username, password]
  );

  const fetchDocs = useCallback(async () => {
    const docs = await adminGetDocuments(username, password);
    setDocuments(docs);
  }, [username, password]);

  const handleLogin = useCallback(async () => {
    setError("");
    setMessage("");
    setLoading(true);
    try {
      await fetchDocs();
      setIsAuthed(true);
      setMessage("Admin authenticated. You can now upload datasets.");
    } catch (e: unknown) {
      setIsAuthed(false);
      setError(getErrorMessage(e, "Invalid credentials"));
    } finally {
      setLoading(false);
    }
  }, [fetchDocs]);

  const handleUpload = useCallback(
    async (file: File) => {
      setError("");
      setMessage("");
      setLoading(true);
      try {
        const res = await adminUploadDocument(file, username, password);
        await fetchDocs();
        setMessage(res.message);
      } catch (e: unknown) {
        setError(getErrorMessage(e, "Upload failed"));
      } finally {
        setLoading(false);
      }
    },
    [fetchDocs, password, username]
  );

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
    if (fileRef.current) {
      fileRef.current.value = "";
    }
  };

  const handleDelete = useCallback(
    async (docId: string) => {
      setError("");
      setMessage("");
      setLoading(true);
      try {
        await adminDeleteDocument(docId, username, password);
        await fetchDocs();
        setMessage("Document deleted.");
      } catch (e: unknown) {
        setError(getErrorMessage(e, "Delete failed"));
      } finally {
        setLoading(false);
      }
    },
    [fetchDocs, password, username]
  );

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1 className="app-title">Data Admin</h1>
      </header>

      <div className="admin-page">
        <div className="admin-card">
          <h2 className="admin-heading">Uploader Login</h2>
          <input
            className="admin-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
          />
          <input
            type="password"
            className="admin-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button
            className="admin-btn"
            disabled={!canSubmit || loading}
            onClick={handleLogin}
          >
            {loading ? "Checking..." : "Login"}
          </button>
          {error && <div className="admin-error">{error}</div>}
          {message && <div className="admin-success">{message}</div>}
        </div>

        {isAuthed && (
          <div className="admin-card">
            <h2 className="admin-heading">Dataset Upload</h2>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt,.md,.csv"
              onChange={onFileChange}
            />
            <p className="admin-hint">Allowed: PDF, TXT, MD, CSV</p>

            <h3 className="admin-subheading">Uploaded Documents</h3>
            {documents.length === 0 ? (
              <p className="no-docs">No uploaded datasets.</p>
            ) : (
              <div className="doc-list admin-doc-list">
                {documents.map((doc) => (
                  <div key={doc.document_id} className="doc-item">
                    <div className="doc-info">
                      <span className="doc-name">{doc.filename}</span>
                      <span className="doc-meta">{doc.chunk_count} chunks</span>
                    </div>
                    <button
                      className="doc-delete"
                      disabled={loading}
                      onClick={() => handleDelete(doc.document_id)}
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
