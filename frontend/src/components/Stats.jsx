import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { fetchStats } from '../services/api'
import styles from './Stats.module.css'

const icons = {
  queries: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
  tokens: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>,
  score: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
}

export default function Stats() {
  const [data, setData] = useState({ total_queries: 0, total_tokens_saved: 0, average_budget_score: 0 })

  useEffect(() => {
    const load = () => fetchStats().then(setData).catch(() => {})
    load()
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [])

  const cards = [
    { key: 'queries', label: 'Queries Processed', value: data.total_queries, icon: icons.queries },
    { key: 'tokens', label: 'Tokens Saved', value: data.total_tokens_saved, icon: icons.tokens },
    { key: 'score', label: 'Avg Budget Score', value: data.average_budget_score?.toFixed?.(1) || '0', icon: icons.score },
  ]

  return (
    <section className={styles.grid}>
      {cards.map((c, i) => (
        <motion.div
          key={c.key}
          className={styles.card}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-40px' }}
          transition={{ delay: i * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
        >
          <div className={styles.iconWrap}>{c.icon}</div>
          <div className={styles.label}>{c.label}</div>
          <div className={styles.value}>{c.value}</div>
          <div className={styles.glowLine} />
        </motion.div>
      ))}
    </section>
  )
}
