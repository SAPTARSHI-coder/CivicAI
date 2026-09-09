import './Features.css'

const FEATURES = [
  {
    tag: 'Explain',
    title: 'Plain-language explanations',
    body: '"You need to submit your income certificate before 15 August." No clause numbers, no legalese.',
  },
  {
    tag: 'Check',
    title: 'Eligibility checker',
    body: 'CivicAI reads your documents and profile, then tells you which schemes you likely qualify for — and which you don\u2019t, and why.',
  },
  {
    tag: 'Plan',
    title: 'A personalised action plan',
    body: 'Not just a summary — a step-by-step checklist with a deadline attached to each step.',
  },
  {
    tag: 'Detect',
    title: 'Missing document detection',
    body: 'Catches gaps before you submit, so applications aren\u2019t rejected over a form you didn\u2019t know you needed.',
  },
  {
    tag: 'Follow up',
    title: 'Conversational follow-up',
    body: 'Ask "why am I not eligible?" or "what if my income changes?" and get an answer that remembers your documents.',
  },
  {
    tag: 'Translate',
    title: 'Multilingual by default',
    body: 'Simple English, Hindi, Bengali, Odia, and more — so language is never the barrier to a benefit you\u2019re owed.',
  },
]

export default function Features() {
  return (
    <section className="features" id="features">
      <div className="wrap">
        <p className="eyebrow">Capabilities</p>
        <h2 className="features-title">What CivicAI actually does</h2>
        <p className="features-sub">
          Not a chatbot that waits for the right question — an officer that
          reads the document first and tells you what matters.
        </p>

        <div className="features-grid">
          {FEATURES.map((f) => (
            <article className="feature-card" key={f.tag}>
              <span className="feature-tag">{f.tag}</span>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
