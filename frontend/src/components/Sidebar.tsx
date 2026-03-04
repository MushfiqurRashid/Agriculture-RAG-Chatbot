"use client";

import React from "react";
import { DocumentInfo } from "@/lib/api";

interface Props {
  documents: DocumentInfo[];
}

export default function Sidebar({ documents }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Documents</h2>
      </div>

      <div className="sidebar-note">
        Upload and manage documents from <strong>/data_admin</strong>.
      </div>

      <div className="doc-list">
        {documents.length === 0 ? (
          <p className="no-docs">No documents uploaded yet</p>
        ) : (
          documents.map((doc) => (
            <div key={doc.document_id} className="doc-item">
              <div className="doc-info">
                <span className="doc-name" title={doc.filename}>
                  {doc.filename}
                </span>
                <span className="doc-meta">{doc.chunk_count} chunks</span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
