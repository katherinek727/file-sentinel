"use client";

import { useCallback, useEffect, useState } from "react";
import { useFiles } from "@/hooks/useFiles";
import { useAlerts } from "@/hooks/useAlerts";
import { FileTable } from "@/components/FileTable";
import { AlertTable } from "@/components/AlertTable";
import { UploadModal } from "@/components/UploadModal";
import { Pagination } from "@/components/Pagination";
import styles from "./page.module.css";

const PAGE_SIZE = 20;

export default function Page() {
  const files = useFiles();
  const alerts = useAlerts();

  const [filesPage, setFilesPage] = useState(1);
  const [alertsPage, setAlertsPage] = useState(1);
  const [showModal, setShowModal] = useState(false);

  const loadFiles = useCallback(
    (page: number) => files.fetch({ page, pageSize: PAGE_SIZE }),
    [files.fetch],
  );

  const loadAlerts = useCallback(
    (page: number) => alerts.fetch({ page, pageSize: PAGE_SIZE }),
    [alerts.fetch],
  );

  useEffect(() => { void loadFiles(filesPage); }, [filesPage]);
  useEffect(() => { void loadAlerts(alertsPage); }, [alertsPage]);

  async function handleUpload(title: string, file: File) {
    await files.create({ title, file });
    setFilesPage(1);
    await loadFiles(1);
    await loadAlerts(alertsPage);
  }

  function handleFilesPage(page: number) {
    setFilesPage(page);
  }

  function handleAlertsPage(page: number) {
    setAlertsPage(page);
  }

  const isError = files.error ?? alerts.error;

  return (
    <div className={styles.root}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.brand}>
            <span className={styles.brandIcon}>⬡</span>
            <span className={styles.brandName}>File Sentinel</span>
          </div>
          <div className={styles.headerActions}>
            <button
              className={styles.refreshBtn}
              onClick={() => {
                void loadFiles(filesPage);
                void loadAlerts(alertsPage);
              }}
            >
              ↻ Refresh
            </button>
            <button
              className={styles.uploadBtn}
              onClick={() => setShowModal(true)}
            >
              + Upload File
            </button>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        {isError && (
          <div className={styles.errorBanner}>
            ⚠ {isError}
          </div>
        )}

        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionTitle}>
              <span className={styles.sectionDot} data-color="accent" />
              Files
            </div>
            {files.data && (
              <span className={styles.count}>{files.data.total}</span>
            )}
          </div>

          <div className={styles.card}>
            {files.isLoading ? (
              <div className={styles.skeleton}>
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className={styles.skeletonRow} />
                ))}
              </div>
            ) : (
              <>
                <FileTable files={files.data?.items ?? []} />
                <Pagination
                  page={filesPage}
                  totalPages={files.data?.total_pages ?? 1}
                  onPageChange={handleFilesPage}
                />
              </>
            )}
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionTitle}>
              <span className={styles.sectionDot} data-color="red" />
              Alerts
            </div>
            {alerts.data && (
              <span className={styles.count}>{alerts.data.total}</span>
            )}
          </div>

          <div className={styles.card}>
            {alerts.isLoading ? (
              <div className={styles.skeleton}>
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className={styles.skeletonRow} />
                ))}
              </div>
            ) : (
              <>
                <AlertTable alerts={alerts.data?.items ?? []} />
                <Pagination
                  page={alertsPage}
                  totalPages={alerts.data?.total_pages ?? 1}
                  onPageChange={handleAlertsPage}
                />
              </>
            )}
          </div>
        </section>
      </main>

      {showModal && (
        <UploadModal
          onClose={() => setShowModal(false)}
          onSubmit={handleUpload}
        />
      )}
    </div>
  );
}
