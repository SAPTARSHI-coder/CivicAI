# CivicAI — Frontend

Marketing / product front end for **CivicAI**, an AI public service
assistant that explains government documents, checks scheme eligibility,
and generates a personalised action plan. Built with React + Vite.

## Structure

```
civicai/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx          # React entry point
    ├── index.css         # design tokens + global styles
    ├── App.jsx            # page composition
    └── components/
        ├── Header.jsx / .css
        ├── Hero.jsx / .css        # jargon → plain-language toggle
        ├── HowItWorks.jsx / .css  # 4-step process
        ├── Features.jsx / .css    # capability grid
        ├── DemoPanel.jsx / .css   # interactive sample-document demo
        ├── Impact.jsx / .css      # who it's for
        └── Footer.jsx / .css
```

## Run it

```bash
npm install
npm run dev
```

Then open the local URL Vite prints (usually `http://localhost:5173`).

## Build for production

```bash
npm run build
npm run preview
```

## Notes

- The demo section (`#demo`) is a **simulation** — no file is actually
  uploaded or sent anywhere. It's meant to show what the real product
  experience would feel like: pick a sample document, see CivicAI's
  explanation, eligibility check, and checklist appear.
- To wire this up to a real backend (e.g. calling Gemma for document
  analysis), replace the `SAMPLES` object and `runSample` logic in
  `src/components/DemoPanel.jsx` with an API call that uploads a file
  and returns `{ explanation, eligibility, checklist }`.
- Fonts (Newsreader, IBM Plex Sans, IBM Plex Mono) load from Google
  Fonts in `index.html`. IBM Plex was chosen partly because it has
  matching Devanagari and other Indic-script cuts, which will help
  once the multilingual UI copy is added.
