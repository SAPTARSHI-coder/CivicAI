import Header from './components/Header.jsx'
import Hero from './components/Hero.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Features from './components/Features.jsx'
import DemoPanel from './components/DemoPanel.jsx'
import Impact from './components/Impact.jsx'
import Footer from './components/Footer.jsx'

import ErrorBoundary from './components/ErrorBoundary.jsx'

export default function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
        <ErrorBoundary>
          <DemoPanel />
        </ErrorBoundary>
        <Impact />
      </main>
      <Footer />
    </>
  )
}
