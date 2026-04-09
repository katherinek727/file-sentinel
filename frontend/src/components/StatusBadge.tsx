import styles from "./StatusBadge.module.css";

type Variant = "success" | "warning" | "danger" | "info" | "neutral";

interface Props {
  label: string;
  variant: Variant;
}

export function StatusBadge({ label, variant }: Props) {
  return (
    <span className={`${styles.badge} ${styles[variant]}`}>
      {label}
    </span>
  );
}
