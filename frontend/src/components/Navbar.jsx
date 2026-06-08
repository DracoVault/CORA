import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import { Sun, Moon, Monitor, List, ChartBar } from '@phosphor-icons/react'
import styles from './Navbar.module.css'

export default function Navbar({ user, onLogin, onRegister, onLogout, onProfileClick, onToggleSidebar, isSidebarOpen, onToggleDashboard, showDashboard }) {
  const { theme, setTheme } = useTheme()

  const themes = [
    { id: 'dark', icon: Moon, label: 'Dark' },
    { id: 'light', icon: Sun, label: 'Light' },
    { id: 'system', icon: Monitor, label: 'System' },
  ]

  return (
    <motion.nav
      className={styles.nav}
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className={styles.inner}>
        <div className={styles.brand}>
          {user && (
            <button className={styles.iconBtn} onClick={onToggleSidebar} aria-label="Toggle Sidebar">
              <List size={24} weight="bold" color="var(--text-primary)" />
            </button>
          )}
          <div className={styles.logoMark}>
            <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
              <circle cx="13" cy="13" r="10" stroke="var(--text-primary)" strokeWidth="1.6" opacity="0.9" />
              <circle cx="13" cy="13" r="4.2" fill="var(--accent)" />
            </svg>
          </div>
          <span className={styles.logoText}>CORA</span>
        </div>

        <div className={styles.controls}>
          <div className={styles.themeToggle}>
            {themes.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                className={`${styles.themeBtn} ${theme === id ? styles.active : ''}`}
                onClick={() => setTheme(id)}
                title={label}
                aria-label={`${label} theme`}
              >
                <Icon size={16} weight={theme === id ? 'fill' : 'regular'} />
              </button>
            ))}
          </div>

          {user && (
            <button 
              className={`${styles.iconBtn} ${showDashboard ? styles.activeIcon : ''}`} 
              onClick={onToggleDashboard} 
              title="Toggle Dashboard"
            >
              <ChartBar size={20} weight={showDashboard ? 'fill' : 'regular'} />
            </button>
          )}

          {user ? (
            <div className={styles.userArea}>
              <div className={styles.avatar} onClick={onProfileClick} style={{ cursor: 'pointer' }} title="Edit Profile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="16" height="16">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
              <span className={styles.username}>{user}</span>
              <button className={styles.authBtn} onClick={onLogout}>Logout</button>
            </div>
          ) : (
            <div className={styles.authGroup}>
              <button className={styles.authBtn} onClick={onLogin}>
                Login
              </button>
              <button className={styles.authBtnPrimary} onClick={onRegister}>
                Register
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.nav>
  )
}
