import styles from "./Pagination.module.css";

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: Props) {
  if (totalPages <= 1) return null;

  return (
    <div className={styles.root}>
      <button
        className={styles.btn}
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Previous page"
      >
        ←
      </button>

      <span className={styles.info}>
        {page} <span className={styles.sep}>/</span> {totalPages}
      </span>

      <button
        className={styles.btn}
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Next page"
      >
        →
      </button>
    </div>
  );
}
