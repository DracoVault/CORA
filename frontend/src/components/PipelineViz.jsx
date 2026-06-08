import { Database, MagnifyingGlass, Scales, GitBranch, ShareNetwork, MagicWand, User, CheckCircle } from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import styles from './PipelineViz.module.css'

const modules = [
  { id: 'pil', icon: Database, name: 'Prompt Input Layer', desc: 'Sanitises input, attaches context, emits PromptContext.', color: 'var(--accent)' },
  { id: 'cam', icon: MagnifyingGlass, name: 'Cognition Analysis Module', desc: 'Extracts structural, semantic, and domain vectors.', color: 'var(--accent)' },
  { id: 'tba', icon: Scales, name: 'Thought Budget Allocator', desc: 'Converts features to a budget score via weights.', color: 'var(--accent)' },
  { id: 'ssm', icon: GitBranch, name: 'Strategy Selection Module', desc: 'Maps score to execution strategy & temperatures.', color: 'var(--accent)' },
  { id: 'mrm', icon: ShareNetwork, name: 'Model Routing Module', desc: 'Dispatches to LLM with fallback & fault tolerance.', color: 'var(--accent-secondary)' },
  { id: 'rpp', icon: MagicWand, name: 'Response Post-Processor', desc: 'Formats output, validates, and attaches metadata.', color: 'var(--accent-secondary)' },
]

export default function PipelineViz() {
  return (
    <section className={styles.section}>
      <motion.div
        className={styles.header}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <h2 className={styles.title}>End-to-End Pipeline</h2>
        <p className={styles.subtitle}>6 modular stages from prompt ingestion to intelligent response</p>
      </motion.div>

      <div className={styles.pipeline}>
        {/* User node */}
        <motion.div
          className={styles.userNode}
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
        >
          <User size={24} color="currentColor" />
          <span>User</span>
        </motion.div>

        {modules.map((mod, i) => (
          <motion.div
            key={mod.id}
            className={styles.moduleCard}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-20px' }}
            transition={{ delay: i * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            whileHover={{ y: -3, transition: { duration: 0.2 } }}
          >
            <div className={styles.connector}>
              <svg width="24" height="10" viewBox="0 0 24 10">
                <line x1="0" y1="5" x2="18" y2="5" stroke="var(--accent)" strokeWidth="1" opacity="0.3" />
                <polygon points="18,2 24,5 18,8" fill="var(--accent)" opacity="0.5" />
              </svg>
            </div>
            <div className={styles.moduleInner}>
              <div className={styles.abbr} style={{ borderColor: mod.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <mod.icon size={22} weight="duotone" color={mod.color} />
              </div>
              <div className={styles.moduleInfo}>
                <div className={styles.moduleName}>{mod.name}</div>
                <div className={styles.moduleDesc}>{mod.desc}</div>
              </div>
            </div>
          </motion.div>
        ))}

        {/* Response node */}
        <motion.div
          className={styles.moduleCard}
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6, duration: 0.4 }}
        >
          <div className={styles.connector}>
            <svg width="24" height="10" viewBox="0 0 24 10">
              <line x1="0" y1="5" x2="18" y2="5" stroke="var(--success)" strokeWidth="1" opacity="0.3" />
              <polygon points="18,2 24,5 18,8" fill="var(--success)" opacity="0.5" />
            </svg>
          </div>
          <div className={styles.responseNode}>
            <CheckCircle size={24} weight="fill" color="var(--success)" />
            <span style={{ color: 'var(--success)' }}>Response</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
