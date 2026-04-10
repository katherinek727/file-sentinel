"use client";

import { FormEvent, useRef, useState } from "react";
import styles from "./UploadModal.module.css";

interface Props {
  onClose: () => void;
  onSubmit: (title: string, file: File) => Promise<void>;
}

export function UploadModal({ onClose, onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) { setError("Title is required"); return; }
    if (!file) { setError("Please select a file"); return; }
    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(title.trim(), file);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.headerIcon}>📁</div>
            <div>
              <div className={styles.title}>Upload File</div>
              <div className={styles.subtitle}>Add a new file to the vault</div>
            </div>
          </div>
          <button className={styles.close} onClick={onClose} aria-label="Close">✕</button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Title</label>
            <input
              className={styles.input}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Contract with supplier"
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>File</label>
            <div className={styles.dropzone} onClick={() => inputRef.current?.click()}>
              {file ? (
                <span className={styles.fileName}>📎 {file.name}</span>
              ) : (
                <>
                  <div className={styles.dropIcon}>☁️</div>
                  <div className={styles.dropHint}>
                    <strong>Click to browse</strong> or drag & drop<br />
                    Any file type supported
                  </div>
                </>
              )}
              <input
                ref={inputRef}
                type="file"
                className={styles.fileInput}
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>
          </div>

          {error && <p className={styles.error}>⚠ {error}</p>}

          <div className={styles.divider} />

          <div className={styles.actions}>
            <button type="button" className={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
              {isSubmitting ? "Uploading…" : "Upload File"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
