const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  response: string;
  conversation_id: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  chunks: number;
  message: string;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  uploaded_at: string;
  chunk_count: number;
}

export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Failed to send message");
  }
  return res.json();
}

function buildAuthHeader(username: string, password: string): string {
  const token = btoa(`${username}:${password}`);
  return `Basic ${token}`;
}

export async function adminUploadDocument(
  file: File,
  username: string,
  password: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/admin/upload`, {
    method: "POST",
    headers: { Authorization: buildAuthHeader(username, password) },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Failed to upload document");
  }
  return res.json();
}

export async function adminGetDocuments(
  username: string,
  password: string
): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_URL}/api/admin/documents`, {
    headers: { Authorization: buildAuthHeader(username, password) },
  });
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function adminDeleteDocument(
  docId: string,
  username: string,
  password: string
): Promise<void> {
  const res = await fetch(`${API_URL}/api/admin/documents/${docId}`, {
    method: "DELETE",
    headers: { Authorization: buildAuthHeader(username, password) },
  });
  if (!res.ok) throw new Error("Failed to delete document");
}
