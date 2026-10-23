
import { useState } from 'react'
import './App.css'

function App() {
  const [result, setResult] = useState(null)

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <h1>Real Estate Finance Assistant</h1>
          <p>Monitor invoices, payments, and project budgets.</p>
        </div>

        <span className="status">Finance Dashboard</span>
      </header>

      <section>
        <h2 className="section-title">Financial Operations</h2>

        <div className="cards">
          <article className="card">
            <h3>Invoice Comparison</h3>
            <p>Compare an invoice amount against its purchase order.</p>

            <label htmlFor="comparison-invoice">Invoice ID</label>
            <input
              id="comparison-invoice"
              type="text"
              placeholder="e.g. INV5001"
            />

            <button
              type="button"
              onClick={async () => {
                const invoiceId = document
                  .getElementById('comparison-invoice')
                  .value
                  .trim()

                if (!invoiceId) {
                  setResult({ error: 'Please enter an invoice ID.' })
                  return
                }

                try {
                  const response = await fetch(
                    `http://127.0.0.1:8000/invoices/${encodeURIComponent(invoiceId)}/comparison`
                  )

                  const data = await response.json()

                  if (!response.ok) {
                    setResult({ error: data.detail || 'Request failed.' })
                    return
                  }

                  setResult(data)
                } catch (error) {
                  setResult({ error: 'Could not connect to the backend.' })
                }
              }}
            >
              Compare Invoice
            </button>
          </article>

          <article className="card">
            <h3>Outstanding Balance</h3>
            <p>Find the unpaid amount remaining on an invoice.</p>

            <label htmlFor="outstanding-invoice">Invoice ID</label>
            <input
              id="outstanding-invoice"
              type="text"
              placeholder="e.g. INV5002"
            />

            <button
              type="button"

              onClick={async () => {
                const invoiceId = document
                  .getElementById('outstanding-invoice')
                  .value
                  .trim()

                if (!invoiceId) {
                  setResult({ error: 'Please enter an invoice ID.' })
                  return
                }

                try {
                  const response = await fetch(
                    `http://127.0.0.1:8000/invoices/${encodeURIComponent(invoiceId)}/outstanding`
                  )

                  const data = await response.json()

                  if (!response.ok) {
                    setResult({ error: data.detail || 'Request failed.' })
                    return
                  }

                  setResult(data)
                } catch {
                  setResult({ error: 'Could not connect to the backend.' })
                }
              }}

            >
              Check Balance
            </button>
          </article>

          <article className="card">
            <h3>Payment Reconciliation</h3>
            <p>Check whether recorded payments match completed transactions.</p>

            <label htmlFor="reconciliation-invoice">Invoice ID</label>
            <input
              id="reconciliation-invoice"
              type="text"
              placeholder="e.g. INV5002"
            />

            <button
              type="button"

              onClick={async () => {
                const invoiceId = document
                  .getElementById('reconciliation-invoice')
                  .value
                  .trim()

                if (!invoiceId) {
                  setResult({ error: 'Please enter an invoice ID.' })
                  return
                }

                try {
                  const response = await fetch(
                    `http://127.0.0.1:8000/invoices/${encodeURIComponent(invoiceId)}/reconciliation`
                  )

                  const data = await response.json()

                  if (!response.ok) {
                    setResult({ error: data.detail || 'Request failed.' })
                    return
                  }

                  setResult(data)
                } catch {
                  setResult({ error: 'Could not connect to the backend.' })
                }
              }}

            >
              Reconcile Payments
            </button>
          </article>
        </div>
      </section>

      <section className="results">
        <h2 className="section-title">Results</h2>

        {result ? (
          <pre>{JSON.stringify(result, null, 2)}</pre>
        ) : (
          <p className="placeholder">
            Select a financial operation to see its result here.
          </p>
        )}
      </section>
    </main>
  )
}

export default App
