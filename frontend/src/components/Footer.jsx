import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <div className={styles.brand}>
          <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="12" stroke="var(--accent)" strokeWidth="1.5" opacity="0.4" />
            <circle cx="14" cy="14" r="7" stroke="var(--accent)" strokeWidth="1.5" />
            <circle cx="14" cy="14" r="2.5" fill="var(--accent)" />
          </svg>
          <span>CORA</span>
        </div>
        <p className={styles.text}>
          Cognitive Orchestration & Reasoning Allocator. Designed for scale.
        </p>
        <div className={styles.links}>
          <a href="#">Documentation</a>
          <a href="#">API Ref</a>
          <a href="https://github.com/mohammadzaieemkhan/CORA" target="_blank" rel="noopener noreferrer">Github</a>
        </div>
      </div>
    </footer>
  )
}
