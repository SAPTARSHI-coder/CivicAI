import './Header.css'

export default function Header() {
  return (
    <header className="header">
      <div className="wrap header-row">
        <a href="#top" className="brand">
          <span className="brand-seal" aria-hidden="true">
            <svg viewBox="0 0 40 40" width="30" height="30">
              <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" strokeWidth="1.5" />
              <circle cx="20" cy="20" r="13" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="2 3" />
              <text x="20" y="25" textAnchor="middle" fontFamily="IBM Plex Mono" fontSize="13" fill="currentColor">C</text>
            </svg>
          </span>
          <span className="brand-name">CivicAI</span>
        </a>

        <nav className="nav" aria-label="Primary">
          <a href="#how">How it works</a>
          <a href="#features">What it does</a>
          <a href="#demo">See it in action</a>
          <a href="#impact">Who it's for</a>
        </nav>

        <a href="#demo" className="btn btn-primary header-cta">Try the demo</a>
      </div>
    </header>
  )
}
