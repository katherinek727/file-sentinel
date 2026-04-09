"use client";

import { StatusBadge } from "./StatusBadge";
import type { AlertItem } from "@/types/alert";
import styles from "./Table.module.css";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function levelVariant(level: string) {
  if (level === "critical") return "danger" as const;
  if (level === "warning") return "warning" as const;
  if (level === "info") return "info" as const;
  return "neutral" as const;
}

interface Props {
  alerts: AlertItem[];
}

export function AlertTable({ alerts }: Props) {
  if (alerts.length === 0) {
    return <p className={styles.empty}>No alerts yet</p>;
  }

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>#</th>
            <th>File ID</th>
            <th>Level</th>
            <th>Message</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id}>
              <td className={styles.mono}>{alert.id}</td>
              <td>
                <span className={styles.mono}>{alert.file_id}</span>
              </td>
              <td>
                <StatusBadge
                  label={alert.level}
                  variant={levelVariant(alert.level)}
                />
              </td>
              <td>{alert.message}</td>
              <td>{formatDate(alert.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
