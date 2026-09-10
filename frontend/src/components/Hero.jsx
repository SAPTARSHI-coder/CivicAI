import { useState } from 'react'
import './Hero.css'

const JARGON = `Applicant is hereby notified that, pursuant to Clause 7(iii) of the Pradhan Mantri Awas Yojana guidelines, submission of a duly attested income certificate, not exceeding ninety (90) days from date of issue, is a mandatory precondition for continued processing of the above-referenced application, failing which the same shall stand summarily rejected without further notice.`

const PLAIN = `You need to submit a fresh income certificate — one issued in the last 90 days — for your PMAY housing application. If it's late, your application will be rejected automatically.`

export default function Hero() {
  const [showPlain, setShowPlain] = useState(true)

  return (
    <section className="hero" id="top">
      <div className="wrap hero-row">
        <div className="hero-copy">
          <p className="eyebrow">Ref. No. CIVIC/AI/2026 — Public Notice</p>
          <h1 className="hero-title">
            An officer who reads<br />the fine print<span className="hero-dot">,</span><br />
            so you don't have to.
          </h1>
          <p className="hero-sub">
            Upload any government notice, scheme letter, tax form, or insurance
            policy. CivicAI explains what it means, tells you if you qualify,
            and gives you a checklist — in your own language.
          </p>
          <div className="hero-actions">
            <a href="#demo" className="btn btn-primary">Upload a document</a>
            <a href="#how" className="btn btn-ghost">See how it works</a>
          </div>
          <div className="hero-stats">
            <div><strong>9</strong><span>document types supported</span></div>
            <div><strong>5+</strong><span>languages, more on the way</span></div>
            <div><strong>24/7</strong><span>no office hours, no queue</span></div>
          </div>
        </div>

        <div className="hero-doc">
          <div className="doc-card">
            <div className="doc-card-head">
              <span className="doc-stamp">OFFICIAL NOTICE</span>
              <span className="doc-ref">No. 4471-B</span>
            </div>
            <p className={`doc-text ${showPlain ? 'is-plain' : ''}`}>
              {showPlain ? PLAIN : JARGON}
            </p>
            <button
              className="doc-toggle"
              onClick={() => setShowPlain((v) => !v)}
              aria-pressed={showPlain}
            >
              {showPlain ? 'Show original wording' : 'Explain in plain language'}
            </button>
          </div>
          <div className="doc-seal" aria-hidden="true">
            <svg viewBox="0 0 100 100" width="86" height="86">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" strokeWidth="2" />
              <circle cx="50" cy="50" r="38" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="3 4" />
              <text x="50" y="46" textAnchor="middle" fontFamily="IBM Plex Mono" fontSize="10" fill="currentColor">VERIFIED</text>
              <text x="50" y="60" textAnchor="middle" fontFamily="IBM Plex Mono" fontSize="10" fill="currentColor">BY CIVICAI</text>
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}
