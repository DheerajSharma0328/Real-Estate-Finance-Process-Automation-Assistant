import { useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function fetchResult(url) {
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}${url}`)
      const data = await response.json()

      if (!response.ok) {
        setResult({ error: data.detail || 'Request failed.' })
        return
      }

      setResult(data)
    } catch {
      setResult({ error: 'Could not connect to the backend.' })
    } finally {
      setLoading(false)
    }
  }


async function fetchInvoiceOperation(inputId, operation) {
  const invoiceId = document.getElementById(inputId).value.trim()

  if (!invoiceId) {
    setResult({ error: 'Please enter an invoice ID.' })
    return
  }

  const routes = {
    comparison: `/invoices/${encodeURIComponent(invoiceId)}/comparison`,
    outstanding: `/invoices/${encodeURIComponent(invoiceId)}/outstanding`,
    reconciliation: `/invoices/${encodeURIComponent(invoiceId)}/reconciliation`,
  }

  await fetchResult(routes[operation])
}


  function renderResults() {
    if (loading) {
      return <p className="placeholder">Loading data...</p>
    }

    if (!result) {
      return (
        <p className="placeholder">
          Select a financial operation to see its result here.
        </p>
      )
    }

    if (result.error) {
      return <p className="error-message">{result.error}</p>
    }

    if (Array.isArray(result) && result.length === 0) {
      return <p className="placeholder">No records found.</p>
    }

    // Display PostgreSQL invoice balances in a table.
    if (
      Array.isArray(result) &&
      result.length > 0 &&
      'outstanding_balance' in result[0]
    ) {
      return (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Invoice Amount</th>
                <th>Paid Amount</th>
                <th>Outstanding</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {result.map((invoice) => (
                <tr key={invoice.invoice_id}>
                  <td>{invoice.invoice_id}</td>
                  <td>{formatAmount(invoice.invoice_amount)}</td>
                  <td>{formatAmount(invoice.paid_amount)}</td>
                  <td>{formatAmount(invoice.outstanding_balance)}</td>
                  <td>{invoice.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    // Display PostgreSQL invoice-to-PO comparisons in a table.
    if (
      Array.isArray(result) &&
      result.length > 0 &&
      'comparison_result' in result[0]
    ) {
      return (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>PO ID</th>
                <th>Vendor</th>
                <th>Invoice Amount</th>
                <th>PO Total</th>
                <th>Variance</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {result.map((invoice) => (
                <tr key={invoice.invoice_id}>
                  <td>{invoice.invoice_id}</td>
                  <td>{invoice.po_id}</td>
                  <td>{invoice.vendor_id}</td>
                  <td>{formatAmount(invoice.invoice_amount)}</td>
                  <td>{formatAmount(invoice.po_total)}</td>
                  <td>{formatAmount(invoice.variance)}</td>
                  <td>
                    <span
                      className={
                        invoice.variance > 0
                          ? 'result-warning'
                          : 'result-success'
                      }
                    >
                      {invoice.comparison_result}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    // Preserve a readable display for the existing single-invoice endpoints.
    return <pre>{JSON.stringify(result, null, 2)}</pre>
  }

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <h1>Real Estate Finance Assistant</h1>
          <p>Monitor invoices, payments, and project budgets.</p>
        </div>

        <span className="status">Finance Dashboard · V0.2</span>
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
              disabled={loading}
              onClick={() =>fetchInvoiceOperation('comparison-invoice', 'comparison')}
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
              disabled={loading}
              onClick={() => fetchInvoiceOperation('outstanding-invoice', 'outstanding')}
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
              disabled={loading}
              onClick={() =>fetchInvoiceOperation('reconciliation-invoice', 'reconciliation')}
            >
              Reconcile Payments
            </button>
          </article>

          <article className="card">
            <h3>All Outstanding Balances</h3>
            <p>View unpaid balances for every invoice stored in PostgreSQL.</p>

            <button
              type="button"
              disabled={loading}
              onClick={() => fetchResult('/api/invoices/outstanding')}
            >
              Load All Balances
            </button>
          </article>

          <article className="card">
            <h3>Invoice vs Purchase Order</h3>
            <p>Identify invoices whose amounts exceed their PO totals.</p>

            <button
              type="button"
              disabled={loading}
              onClick={() => fetchResult('/api/invoices/po-comparison')}
            >
              Compare All Invoices
            </button>
          </article>
        </div>
      </section>

      <section className="results">
        <h2 className="section-title">Results</h2>
        {renderResults()}
      </section>
    </main>
  )
}

function formatAmount(value) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(value)
}

export default App
