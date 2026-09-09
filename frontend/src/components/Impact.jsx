import './Impact.css'

const AUDIENCES = [
  'Rural populations',
  'Senior citizens',
  'First-time applicants',
  'Students',
  'Small business owners',
  'Anyone unfamiliar with legal or government terminology',
]

export default function Impact() {
  return (
    <section className="impact" id="impact">
      <div className="wrap impact-row">
        <div>
          <p className="eyebrow">Why this matters</p>
          <h2 className="impact-title">
            People don't lose benefits because information is unavailable.
            They lose them because it's hard to understand.
          </h2>
          <p className="impact-body">
            CivicAI exists to close that gap — reading the document once, so
            the person on the other side of it doesn't have to decode it
            alone.
          </p>
        </div>

        <ul className="audience-list">
          {AUDIENCES.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      </div>
    </section>
  )
}
