import React, { useState } from 'react'
import NFAInput from './components/NFAInput'
import DiagramViewer from './components/DiagramViewer'
import './App.css'

function App() {
  const [nfaData, setNfaData] = useState(null)
  const [dfaData, setDfaData] = useState(null)
  const [dfaMinimizedData, setDfaMinimizedData] = useState(null)
  const [nfaImage, setNfaImage] = useState(null)
  const [dfaImage, setDfaImage] = useState(null)
  const [dfaMinimizedImage, setDfaMinimizedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // API URL - detect environment automatically
  // In development (localhost), use Vite proxy
  // In production, use the actual backend URL
  const API_URL = window.location.hostname === 'localhost' 
    ? '/api/convert' 
    : import.meta.env.VITE_API_URL || 'https://nfa-dfa-api.onrender.com/api/convert'

  const handleConvert = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      
      if (!response.ok) {
        throw new Error('Conversion failed')
      }
      
      const result = await response.json()
      
      setNfaData(result.nfa)
      setDfaData(result.dfa)
      setDfaMinimizedData(result.dfaMinimized)
      setNfaImage(result.nfaImage)
      setDfaImage(result.dfaImage)
      setDfaMinimizedImage(result.dfaMinimizedImage)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>NFA to DFA Converter</h1>
        <p>Convert Non-Deterministic Finite Automata to Deterministic Finite Automata with visual diagrams</p>
      </header>
      
      <main className="app-main">
        <NFAInput onConvert={handleConvert} loading={loading} />
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {nfaData && dfaData && (
          <div className="results">
            <DiagramViewer 
              title="NFA"
              subtitle="(Non-Deterministic Finite Automaton)"
              svgContent={nfaImage}
              jsonData={nfaData}
            />
            <DiagramViewer 
              title="DFA"
              subtitle="(Deterministic Finite Automaton)"
              svgContent={dfaImage}
              jsonData={dfaData}
            />
            <DiagramViewer 
              title="Minimized DFA"
              subtitle="(Optimized)"
              svgContent={dfaMinimizedImage}
              jsonData={dfaMinimizedData}
            />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
