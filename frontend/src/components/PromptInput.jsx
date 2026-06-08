import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import PromptOptimizer from './PromptOptimizer'
import { optimizePrompt } from '../services/api'
import {
  Brain,
  ChartBar,
  Lightning,
  Crosshair,
  Rocket,
  Sparkle,
  PaperPlaneRight,
} from '@phosphor-icons/react'
import styles from './PromptInput.module.css'

const ROUTING_PHASES = [
  { text: 'Analyzing cognitive complexity…', Icon: Brain, color: '#7c4dff', duration: 1200 },
  { text: 'Extracting 6D feature vector…', Icon: ChartBar, color: '#00e5ff', duration: 1000 },
  { text: 'Computing budget score…', Icon: Lightning, color: '#ffab00', duration: 800 },
  { text: 'Selecting optimal tier…', Icon: Crosshair, color: '#00e676', duration: 900 },
  { text: 'Routing to optimized model…', Icon: Rocket, color: '#ff006e', duration: 1100 },
  { text: 'Generating response…', Icon: Sparkle, color: '#00e5ff', duration: 2000 },
]

export default function PromptInput({ onSubmit, isProcessing }) {
  const [prompt, setPrompt] = useState('')
  const [phase, setPhase] = useState(0)
  const phaseTimer = useRef(null)

  const [isOptimizing, setIsOptimizing] = useState(false)
  const [optError, setOptError] = useState(null)
  const [optData, setOptData] = useState(null)

  const handleOptimize = async () => {
    if (!prompt.trim() || isProcessing) return
    setIsOptimizing(true)
    setOptError(null)
    try {
      const data = await optimizePrompt(prompt.trim())
      setOptData(data)
    } catch (err) {
      setOptError(err.message || 'Optimization failed')
    } finally {
      setIsOptimizing(false)
    }
  }

  const handleSelectPrompt = (selectedText) => {
    setPrompt(selectedText)
    setOptData(null) // close modal
    // Auto-submit after selection
    onSubmit(selectedText)
  }

  useEffect(() => {
    if (isProcessing) {
      setPhase(0)
      let current = 0
      const advance = () => {
        current += 1
        if (current < ROUTING_PHASES.length) {
          setPhase(current)
          phaseTimer.current = setTimeout(advance, ROUTING_PHASES[current].duration)
        }
      }
      phaseTimer.current = setTimeout(advance, ROUTING_PHASES[0].duration)
    } else {
      clearTimeout(phaseTimer.current)
      setPhase(0)
    }
    return () => clearTimeout(phaseTimer.current)
  }, [isProcessing])

  const handleSubmit = () => {
    if (!prompt.trim() || isProcessing || isOptimizing) return
    // Auto-intercept standard send action and trigger DeepSeek optimization
    handleOptimize()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit()
  }

  const currentPhase = ROUTING_PHASES[phase]
  const PhaseIcon = currentPhase.Icon

  return (
    <motion.section
      className={styles.section}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <textarea
        className={styles.textarea}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='Enter the prompt. e.g. "Explain how transformers work" or "Debug this recursive function"'
        rows={4}
      />
      <div className={styles.footer}>
        <span className={styles.hint}>
          Press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to send
        </span>
        <div className={styles.buttonGroup}>
          <motion.button
          className={styles.sendBtn}
          onClick={handleSubmit}
          disabled={isProcessing || !prompt.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isProcessing || isOptimizing ? (
            <span className={styles.processingWrap}>
              <span className={styles.orbContainer}>
                <span className={styles.orb} />
                <span className={styles.orbRing} />
              </span>
              <AnimatePresence mode="wait">
                <motion.span
                  key={isOptimizing ? 'opt' : phase}
                  className={styles.phaseText}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.25 }}
                >
                  {isOptimizing ? (
                    <>
                      <Sparkle size={16} weight="duotone" style={{ color: '#00e5ff' }} />
                      AI Analyzing...
                    </>
                  ) : (
                    <>
                      <PhaseIcon size={16} weight="duotone" style={{ color: currentPhase.color }} />
                      {currentPhase.text}
                    </>
                  )}
                </motion.span>
              </AnimatePresence>
            </span>
          ) : (
            <>
              <PaperPlaneRight size={16} weight="fill" />
              Send to CORA
            </>
          )}
          </motion.button>
        </div>
      </div>

      {/* Animated progress track while processing */}
      <AnimatePresence>
        {isProcessing && (
          <motion.div
            className={styles.progressTrack}
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{ opacity: 1, scaleX: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <motion.div
              className={styles.progressFill}
              initial={{ width: '0%' }}
              animate={{ width: `${((phase + 1) / ROUTING_PHASES.length) * 100}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
            <div className={styles.progressNodes}>
              {ROUTING_PHASES.map((p, i) => {
                const NodeIcon = p.Icon
                return (
                  <div
                    key={i}
                    className={`${styles.progressNode} ${i <= phase ? styles.progressNodeActive : ''}`}
                    title={p.text}
                    style={i <= phase ? { borderColor: p.color, boxShadow: `0 0 8px ${p.color}44` } : {}}
                  >
                    <NodeIcon
                      size={12}
                      weight={i <= phase ? 'fill' : 'regular'}
                      className={styles.progressNodeIcon}
                      style={i <= phase ? { color: p.color } : {}}
                    />
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {(isOptimizing || optError || optData) && (
          <PromptOptimizer 
            isOptimizing={isOptimizing}
            error={optError}
            rawPrompt={prompt}
            optimizationData={optData}
            onSelectPrompt={handleSelectPrompt}
            onBack={() => { setOptData(null); setOptError(null); setIsOptimizing(false) }}
          />
        )}
      </AnimatePresence>
    </motion.section>
  )
}
