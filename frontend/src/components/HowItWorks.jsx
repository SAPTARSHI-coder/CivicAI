import './HowItWorks.css'

const STEPS = [
  {
    n: '01',
    title: 'Upload your document',
    body: 'A photo, scan, or PDF — a scheme notice, ration card, pension letter, tax notice, insurance policy, or land record.',
  },
  {
    n: '02',
    title: 'CivicAI reads and explains it',
    body: 'The jargon is translated into plain language, in English or your preferred regional language.',
  },
  {
    n: '03',
    title: 'You find out where you stand',
    body: 'CivicAI checks your eligibility against relevant schemes and flags anything missing from your application.',
  },
  {
    n: '04',
    title: 'You get a checklist and a deadline',
    body: 'A short, ordered list of what to do next — and by when — plus follow-up questions any time you need them.',
  },
]

export default function HowItWorks() {
  return (
    <section className="how" id="how">
      <div className="wrap">
        <p className="eyebrow">Procedure</p>
        <h2 className="how-title">Four steps, start to finish</h2>

        <ol className="how-steps">
          {STEPS.map((s) => (
            <li className="how-step" key={s.n}>
              <span className="how-n">{s.n}</span>
              <div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
