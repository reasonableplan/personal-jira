import styles from './LoadingSpinner.module.css';

export function LoadingSpinner() {
  return (
    <div className={styles.wrapper} data-testid="loading-spinner">
      <div className={styles.spinner} />
    </div>
  );
}
