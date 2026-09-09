import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ChatPanel from './ChatPanel.jsx'
import './DemoPanel.css'

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.2 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
}

export default function DemoPanel() {
  const [file, setFile] = useState(null)
  const [language, setLanguage] = useState('English')
  const [provider, setProvider] = useState('gemini')
  const [status, setStatus] = useState('idle') // idle | reading | done | error
  const [errorMsg, setErrorMsg] = useState('')
  const [docResult, setDocResult] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [samples, setSamples] = useState([])
  const [activeSampleId, setActiveSampleId] = useState(null)
  const [loadingSample, setLoadingSample] = useState(false)
  
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetch('/api/v1/samples')
      .then(res => res.ok ? res.json() : [])
      .then(data => setSamples(data))
      .catch(err => console.warn('Could not load sample list:', err))
  }, [])

  const handleSelectSample = async (sample) => {
    try {
      setActiveSampleId(sample.id)
      setLoadingSample(true)
      const res = await fetch(`/api/v1/samples/${sample.id}/download`)
      if (!res.ok) throw new Error('Failed to load sample document')
      const blob = await res.blob()
      const sampleFile = new File([blob], sample.filename, { type: 'application/pdf' })
      setFile(sampleFile)
      setErrorMsg('')
    } catch (err) {
      console.error(err)
      setErrorMsg('Failed to load sample document')
    } finally {
      setLoadingSample(false)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setStatus('reading')
    setErrorMsg('')
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)
    formData.append('provider', provider)

    try {
      const res = await fetch('/api/v1/analyze', {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) {
        const errData = await res.json()
        const errorMsg = errData?.error?.message || errData?.detail || 'Analysis failed'
        throw new Error(errorMsg)
      }
      
      const data = await res.json()
      setDocResult(data)
      setStatus('done')
    } catch (err) {
      console.error(err)
      setErrorMsg(err.message)
      setStatus('error')
    }
  }

  return (
    <section className="demo" id="demo">
      <div className="wrap">
        <p className="eyebrow">Try it</p>
        <h2 className="demo-title">Upload a document</h2>
        <p className="demo-sub">Upload a PDF or image of an official notice or card to see CivicAI in action.</p>

        <div className="demo-body" style={{ display: 'flex', flexDirection: 'column' }}>
          
          <form className="demo-upload-form" onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
            <div className="provider-toggle">
              <span className="toggle-label">AI Provider:</span>
              <div className="toggle-buttons">
                <button type="button" className={`toggle-btn ${provider === 'gemma-local' ? 'active' : ''}`} onClick={() => setProvider('gemma-local')}>
                  Local (Gemma 4)
                </button>
                <button type="button" className={`toggle-btn ${provider === 'gemini' ? 'active' : ''}`} onClick={() => setProvider('gemini')}>
                  Gemini API
                </button>
              </div>
              <span className="toggle-disclaimer">
                {provider === 'gemma-local' ? 'Private & offline, but may be slower.' : 'Requires internet and API key. Sends data to Google.'}
              </span>
            </div>

            {samples.length > 0 && (
              <div className="sample-presets-bar" style={{ marginBottom: '1.25rem' }}>
                <span className="toggle-label" style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: '#94a3b8' }}>
                  Quick Demo Pre-sets (1-Click Sample Schemes):
                </span>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {samples.map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      className={`sample-pill-btn ${activeSampleId === s.id ? 'active' : ''}`}
                      onClick={() => handleSelectSample(s)}
                      disabled={loadingSample || status === 'reading'}
                      style={{
                        padding: '7px 14px',
                        borderRadius: '20px',
                        fontSize: '13px',
                        cursor: 'pointer',
                        border: activeSampleId === s.id ? '1px solid var(--saffron-500)' : '1px solid rgba(255,255,255,0.18)',
                        background: activeSampleId === s.id ? 'rgba(226, 147, 46, 0.18)' : 'rgba(255,255,255,0.06)',
                        color: activeSampleId === s.id ? 'var(--saffron-500)' : '#e2e8f0',
                        fontWeight: activeSampleId === s.id ? 600 : 400,
                        transition: 'all 0.15s ease',
                      }}
                    >
                      🏛️ {s.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="controls-row">
              <div 
                className={`drag-zone ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  accept=".pdf,.png,.jpg,.jpeg" 
                  onChange={handleFileChange} 
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                />
                <p>{file ? file.name : "Drag & drop a file here, or click to select"}</p>
              </div>
              
              <div className="select-wrapper">
                <select value={language} onChange={e => setLanguage(e.target.value)}>
                  <option value="English">English</option>
                  <option value="Hindi">Hindi</option>
                  <option value="Bengali">Bengali</option>
                  <option value="Odia">Odia</option>
                </select>
              </div>
              
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit" 
                className="analyze-btn"
                disabled={!file || status === 'reading'}
              >
                Analyze
              </motion.button>
            </div>
          </form>

          <div className="demo-output" style={{ width: '100%' }}>
            {status === 'idle' && (
              <div className="demo-empty">
                <p>Upload a document above to see CivicAI's explanation, eligibility check, and checklist.</p>
              </div>
            )}

            {status === 'reading' && (
              <div className="demo-loading-skeleton">
                <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5 }} className="skeleton-line" style={{ width: '40%' }} />
                <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }} className="skeleton-line" />
                <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }} className="skeleton-line" style={{ width: '80%' }} />
                <p>Analyzing document...</p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="demo-empty" style={{ color: '#ef4444' }}>
                <p>Error: {errorMsg}</p>
              </div>
            )}

            {status === 'done' && docResult && (
              <div className="demo-result" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                  <motion.div variants={containerVariants} initial="hidden" animate="show" style={{ flex: '1 1 300px' }}>
                    {docResult.document_url && (
                      <motion.div variants={itemVariants} className="doc-link-container">
                        <a 
                          href={docResult.document_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="doc-link"
                        >
                          <svg className="doc-link-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                            <polyline points="15 3 21 3 21 9" />
                            <line x1="10" y1="14" x2="21" y2="3" />
                          </svg>
                          <span>View original document</span>
                        </a>
                      </motion.div>
                    )}
                    <motion.div variants={itemVariants} className="result-block">
                      <span className="result-label">In plain language</span>
                      <p>{docResult.explanation}</p>
                    </motion.div>

                    <motion.div variants={itemVariants} className={`result-block eligibility eligibility-${docResult.eligibility.status}`}>
                      <span className="result-label">Eligibility</span>
                      <p>{docResult.eligibility.text}</p>
                    </motion.div>

                    <motion.div variants={itemVariants} className="result-block">
                      <span className="result-label">Your checklist</span>
                      <ul className="checklist">
                        {docResult.checklist.map((item, idx) => (
                          <li key={idx}>
                            <span className="checklist-box" aria-hidden="true" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                    
                    {docResult.missing_documents && docResult.missing_documents.length > 0 && (
                      <motion.div variants={itemVariants} className="result-block" style={{ borderLeftColor: '#ef4444' }}>
                        <span className="result-label" style={{ color: '#ef4444' }}>Missing Documents</span>
                        <ul className="checklist">
                          {docResult.missing_documents.map((item, idx) => (
                            <li key={idx} style={{ color: '#991b1b' }}>
                              <span className="checklist-box" aria-hidden="true" style={{ borderColor: '#ef4444' }} />
                              {item}
                            </li>
                          ))}
                        </ul>
                      </motion.div>
                    )}
                  </motion.div>
                  
                  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }} style={{ flex: '1 1 300px', background: '#f8fafc', padding: '1.5rem', borderRadius: '8px' }}>
                    <ChatPanel sessionId={docResult.session_id} provider={provider} currentLanguage={language} />
                  </motion.div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
