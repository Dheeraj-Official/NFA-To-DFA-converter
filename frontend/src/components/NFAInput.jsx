import React, { useState } from 'react'
import './NFAInput.css'

function NFAInput({ onConvert, loading }) {
  const [numStates, setNumStates] = useState('')
  const [alphabet, setAlphabet] = useState('')
  const [startState, setStartState] = useState('')
  const [finalStates, setFinalStates] = useState('')
  const [transitions, setTransitions] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const alphabetArray = alphabet.split(',').map(s => s.trim())
    const finalStatesArray = finalStates.split(',').map(s => parseInt(s.trim()))
    const transitionsArray = transitions.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const parts = line.trim().split(/\s+/)
        return {
          from_state: parseInt(parts[0]),
          symbol: parts[1],
          to_state: parseInt(parts[2])
        }
      })

    const formData = {
      numStates: parseInt(numStates),
      alphabet: alphabetArray,
      startState: parseInt(startState),
      finalStates: finalStatesArray,
      transitions: transitionsArray
    }

    onConvert(formData)
  }

  const loadExample = () => {
    setNumStates('5')
    setAlphabet('a, b, c')
    setStartState('0')
    setFinalStates('4')
    setTransitions('0 a 0\n0 b 0\n0 c 0\n0 e 1\n0 e 2\n1 a 3\n2 b 3\n3 c 4\n4 a 4\n4 b 4\n4 c 4')
  }

  return (
    <div className="nfa-input">
      <h2>Enter NFA Data</h2>
      <button onClick={loadExample} className="example-btn">
        Load Example
      </button>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Number of States:</label>
          <input
            type="number"
            value={numStates}
            onChange={(e) => setNumStates(e.target.value)}
            required
            min="1"
          />
        </div>

        <div className="form-group">
          <label>Alphabet (comma separated):</label>
          <input
            type="text"
            value={alphabet}
            onChange={(e) => setAlphabet(e.target.value)}
            required
            placeholder="a, b, c"
          />
        </div>

        <div className="form-group">
          <label>Start State:</label>
          <input
            type="number"
            value={startState}
            onChange={(e) => setStartState(e.target.value)}
            required
            min="0"
          />
        </div>

        <div className="form-group">
          <label>Final States (comma separated):</label>
          <input
            type="text"
            value={finalStates}
            onChange={(e) => setFinalStates(e.target.value)}
            required
            placeholder="2, 3, 4"
          />
        </div>

        <div className="form-group">
          <label>Transitions (one per line: from symbol to):</label>
          <textarea
            value={transitions}
            onChange={(e) => setTransitions(e.target.value)}
            required
            rows="6"
            placeholder="0 a 1&#10;0 b 2&#10;1 a 2"
          />
          <small>Use 'e' for epsilon transitions</small>
        </div>

        <button type="submit" disabled={loading} className="convert-btn">
          {loading ? 'Converting...' : 'Convert to DFA'}
        </button>
      </form>
    </div>
  )
}

export default NFAInput
