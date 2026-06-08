import { motion } from 'framer-motion'
import styles from './BentoGrid.module.css'

const features = [
  {
    title: '6D cognitive profile',
    desc: 'Prompt complexity is broken into reasoning, precision, structure, creativity, domain, and code signals.',
    span: 2,
  },
  {
    title: 'Tiered routing',
    desc: 'Model selection stays explainable with compact tier and budget metadata.',
  },
  {
    title: 'Cost aware',
    desc: 'Simple work stays light while complex prompts earn larger model budgets.',
  },
  {
    title: 'Provider modules',
    desc: 'Clean adapters keep routing portable across available model endpoints.',
    span: 2,
  },
  {
    title: 'Reflection loop',
    desc: 'History and telemetry create a feedback path for better future allocation.',
    span: 2,
  },
  {
    title: 'Confidence visible',
    desc: 'Every response keeps the classification confidence and top factors close by.',
  },
]

export default function BentoGrid() {
  return (
    <section id="architecture" className={styles.section}>
      <motion.div
        className={styles.header}
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2>Designed like a showcase. Built like a configurator.</h2>
        <p>Broad quiet sections for learning the system, denser panels for actually routing work.</p>
      </motion.div>
      <div className={styles.grid}>
        {features.map((feature, index) => (
          <motion.article
            key={feature.title}
            className={`${styles.card} ${feature.span === 2 ? styles.span2 : ''}`}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-30px' }}
            transition={{ delay: index * 0.05, duration: 0.4 }}
          >
            <div className={styles.media}>
              <span className={styles.number}>{String(index + 1).padStart(2, '0')}</span>
              <h3>{feature.title}</h3>
            </div>
            <p>{feature.desc}</p>
          </motion.article>
        ))}
      </div>
    </section>
  )
}
