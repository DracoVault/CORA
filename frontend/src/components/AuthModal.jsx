import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { login as apiLogin, register as apiRegister } from '../services/api'
import styles from './AuthModal.module.css'

export default function AuthModal({ isOpen, onClose, onAuth, initialMode = 'login' }) {
  const [mode, setMode] = useState(initialMode)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode)
      setError('')
    }
  }, [isOpen, initialMode])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let data
      if (mode === 'register') {
        if (!username || !email || !password) { setError('All fields required.'); setLoading(false); return }
        data = await apiRegister(username, email, password)
      } else {
        if (!username || !password) { setError('Username and password required.'); setLoading(false); return }
        data = await apiLogin(username, password)
      }
      localStorage.setItem('cora_token', data.token)
      localStorage.setItem('cora_user', data.username)
      onAuth(data.username)
      onClose()
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
          <h2 className={styles.title}>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>

          <form onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label>Username</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="your_username" />
            </div>
            {mode === 'register' && (
              <div className={styles.field}>
                <label>Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </div>
            )}
            <div className={styles.field}>
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            {error && <div className={styles.error}>{error}</div>}
            <button className={styles.submit} type="submit" disabled={loading}>
              {loading ? 'Please wait…' : mode === 'login' ? 'Login' : 'Register'}
            </button>
          </form>

          <div className={styles.switchText}>
            {mode === 'login' ? (
              <>No account? <button onClick={() => { setMode('register'); setError('') }}>Register</button></>
            ) : (
              <>Already have one? <button onClick={() => { setMode('login'); setError('') }}>Login</button></>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
