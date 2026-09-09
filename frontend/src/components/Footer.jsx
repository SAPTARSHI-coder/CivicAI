import './Footer.css'

const LANGUAGES = ['English', 'हिन्दी', 'বাংলা', 'ଓଡ଼ିଆ', '+ more soon']

export default function Footer() {
  return (
    <footer className="footer">
      <div className="perforation" aria-hidden="true" />
      <div className="wrap footer-row">
        <div>
          <span className="brand-name">CivicAI</span>
          <p className="footer-tag">Your AI public service officer.</p>
        </div>

        <div className="footer-langs">
          <span className="eyebrow">Available in</span>
          <div className="lang-pills">
            {LANGUAGES.map((l) => (
              <span className="lang-pill" key={l}>{l}</span>
            ))}
          </div>
        </div>

        <p className="footer-note">
          CivicAI provides guidance, not legal advice. Always confirm
          deadlines and requirements with the issuing office.
        </p>
      </div>
    </footer>
  )
}
