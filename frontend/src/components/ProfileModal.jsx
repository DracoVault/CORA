import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { updateProfile } from '../services/api'
import styles from './ProfileModal.module.css'

export default function ProfileModal({ isOpen, onClose, username }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!email && !password) {
      setError('Please provide at least an email or password to update.')
      return
    }

    setLoading(true)
    try {
      await updateProfile(email, password)
      setSuccess('Profile updated successfully!')
      setEmail('')
      setPassword('')
      setTimeout(() => {
        setSuccess('')
        onClose()
      }, 1500)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        className={styles.overlay}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className={styles.modal}
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 30, scale: 0.95 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className={styles.close} onClick={onClose}>✕</button>
          <h2 className={styles.title}>Edit Profile: {username}</h2>

          <form onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label>Update Email</label>
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="new_email@example.com" 
              />
            </div>
            <div className={styles.field}>
              <label>Update Password</label>
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="New strong password" 
                minLength={6}
              />
            </div>
            {error && <div className={styles.error}>{error}</div>}
            {success && <div className={styles.success}>{success}</div>}
            <button className={styles.submit} type="submit" disabled={loading || (!email && !password)}>
              {loading ? 'Updating…' : 'Save Changes'}
            </button>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
