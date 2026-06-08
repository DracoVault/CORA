import { motion } from 'framer-motion'
import styles from './Hero.module.css'

export default function Hero() {
  return (
    <section className={styles.hero}>
      <motion.div
        className={styles.content}
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className={styles.eyebrow}>Cognitive routing, beautifully allocated.</div>
        <h1 className={styles.title}>CORA</h1>
        <p className={styles.subtitle}>Cognitive Orchestration &amp; Reasoning Allocator</p>
        <p className={styles.desc}>
          A calm routing surface that studies prompt complexity, selects the right model tier,
          and keeps the decision trail visible without turning the interface into a cockpit.
        </p>
        <div className={styles.actions}>
          <a href="#prompt" className={styles.primaryAction}>Start routing</a>
          <a href="#architecture" className={styles.secondaryAction}>View architecture</a>
        </div>
      </motion.div>
      <motion.div
        className={styles.stage}
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.15, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className={styles.device}>
          <div className={styles.deviceScreen}>
            <span />
            <strong>Tier 1</strong>
            <small>Routing Identity: Tier 1</small>
          </div>
        </div>
      </motion.div>
    </section>
  )
}
