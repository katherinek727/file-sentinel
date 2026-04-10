"use client";

import { StatusBadge } from "./StatusBadge";
import { filesApi } from "@/api/files";
import type { FileItem } from "@/types/file";
import styles from "./Table.module.css";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function processingVariant(status: string) {
  if (status === "failed") return "danger" as const;
  if (status === "processing") return "warning" as const;
  if (status === "processed") return "success" as const;
  return "neutral" as const;
}

function scanVariant(requiresAttention: boolean) {
  return requiresAttention ? ("warning" as const) : ("success" as const);
}

interface Props {
  files: FileItem[];
}

export function FileTable({ files }: Props) {
  if (files.length === 0) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>📂</div>
        <div>No files uploaded yet</div>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Title</th>
            <th>File</th>
            <th>MIME</th>
            <th>Size</th>
            <th>Status</th>
            <th>Scan</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id}>
              <td>
                <div className={styles.title}>{file.title}</div>
                <div className={styles.sub}>{file.id}</div>
              </td>
              <td>{file.original_name}</td>
              <td>
                <span className={styles.mono}>{file.mime_type}</span>
              </td>
              <td>{formatSize(file.size)}</td>
              <td>
                <StatusBadge
                  label={file.processing_status}
                  variant={processingVariant(file.processing_status)}
                />
              </td>
              <td>
                <div className={styles.scanCell}>
                  <StatusBadge
                    label={file.scan_status ?? "pending"}
                    variant={scanVariant(file.requires_attention)}
                  />
                  {file.scan_details && (
                    <span className={styles.sub}>{file.scan_details}</span>
                  )}
                </div>
              </td>
              <td>{formatDate(file.created_at)}</td>
              <td>
                <a
                  href={filesApi.downloadUrl(file.id)}
                  className={styles.downloadBtn}
                  download
                >
                  Download
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
