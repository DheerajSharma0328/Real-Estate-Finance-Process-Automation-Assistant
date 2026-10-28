
import { useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  // State for existing financial operations.
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // State for Day 3 document search.
  const [documentQuery, setDocumentQuery] = useState(
    'Why is invoice INV5004 on hold?'
  )
  const [projectId, setProjectId] = useState('PR204')
  const [documentResults, setDocumentResults] = useState(null)
  const [documentLoading, setDocumentLoading] = useState(false)
  const [documentError, setDocumentError] = useState('')
  // Day 4: property-linked financial evidence.
  const [evidencePropertyId, setEvidencePropertyId] = useState('P204')
  const [evidenceInvoiceId, setEvidenceInvoiceId] = useState('INV5004')
  const [evidenceQuery, setEvidenceQuery] = useState(
    'Why is invoice INV5004 on hold?'
  )
  const [propertyEvidence, setPropertyEvidence] = useState(null)
  const [propertyEvidenceLoading, setPropertyEvidenceLoading] = useState(false)
  const [propertyEvidenceError, setPropertyEvidenceError] = useState('')

  // Fetch results from existing financial endpoints.
  async function fetchResult(url) {
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}${url}`)
      const data = await response.json()

      if (!response.ok) {
        setResult({
          error:
            typeof data.detail === 'string'
              ? data.detail
              : 'Request failed.',
        })
        return
      }

      setResult(data)
    } catch {
      setResult({
        error: 'Could not connect to the backend.',
      })
    } finally {
      setLoading(false)
    }
  }

  // Handle individual invoice operations.
  async function fetchInvoiceOperation(inputId, operation) {
    const input = document.getElementById(inputId)
    const invoiceId = input ? input.value.trim() : ''

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

  // Search documents using the Day 3 semantic-search API.
  async function searchDocuments(event) {
    event.preventDefault()

    if (!documentQuery.trim()) {
      setDocumentError('Please enter a question.')
      setDocumentResults(null)
      return
    }

    if (documentQuery.trim().length > 1000) {
      setDocumentError('Your question must be 1000 characters or fewer.')
      setDocumentResults(null)
      return
    }

    setDocumentLoading(true)
    setDocumentError('')
    setDocumentResults(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/search`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: documentQuery.trim(),
            project_id: projectId.trim() || null,
            top_k: 3,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        setDocumentError(
          typeof data.detail === 'string'
            ? data.detail
            : 'Document search failed.'
        )
        return
      }

      setDocumentResults(data)
    } catch {
      setDocumentError(
        'Could not connect to the backend. Check that FastAPI is running.'
      )
    } finally {
      setDocumentLoading(false)
    }
  }

  async function searchPropertyEvidence(event) {
  event.preventDefault()

  setPropertyEvidenceLoading(true)
  setPropertyEvidenceError('')
  setPropertyEvidence(null)

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/properties/${encodeURIComponent(
        evidencePropertyId.trim()
      )}/evidence`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: evidenceQuery.trim(),
          invoice_id: evidenceInvoiceId.trim() || null,
          top_k: 3,
        }),
      }
    )

    const data = await response.json()

    if (!response.ok) {
      setPropertyEvidenceError(
        typeof data.detail === 'string'
          ? data.detail
          : 'Property evidence search failed.'
      )
      return
    }

    setPropertyEvidence(data)
  } catch {
    setPropertyEvidenceError(
      'Could not connect to the backend. Check that FastAPI is running.'
    )
  } finally {
    setPropertyEvidenceLoading(false)
  }
}

  // Display results from existing financial operations.
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

    // Display PostgreSQL invoice-to-purchase-order comparisons.
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

    // Keep other existing API responses readable.
    return <pre>{JSON.stringify(result, null, 2)}</pre>
  }

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <h1>Real Estate Finance Assistant</h1>
          <p>Monitor invoices, payments, and project budgets.</p>
        </div>

        <span className="status">Finance Dashboard · V0.3</span>
      </header>

      {/* Existing Day 1 and Day 2 financial operations. */}
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
              onClick={() =>
                fetchInvoiceOperation('comparison-invoice', 'comparison')
              }
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
              onClick={() =>
                fetchInvoiceOperation('outstanding-invoice', 'outstanding')
              }
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
              onClick={() =>
                fetchInvoiceOperation(
                  'reconciliation-invoice',
                  'reconciliation'
                )
              }
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

      {/* New Day 3 document search section. */}
      <section className="document-search">
        <h2 className="section-title">Document Search</h2>

        <p className="document-description">
          Search project documents by meaning and inspect the supporting
          evidence returned by the document retrieval system.
        </p>

        <form
          onSubmit={searchDocuments}
          className="document-search-form"
        >
          <label htmlFor="document-query">Your question</label>

          <textarea
            id="document-query"
            value={documentQuery}
            onChange={(event) => setDocumentQuery(event.target.value)}
            placeholder="e.g. Why is invoice INV5004 on hold?"
            maxLength={1000}
            rows={3}
            required
          />

          <label htmlFor="document-project">Project ID</label>

          <input
            id="document-project"
            type="text"
            value={projectId}
            onChange={(event) => setProjectId(event.target.value)}
            placeholder="e.g. PR204"
          />

          <button type="submit" disabled={documentLoading}>
            {documentLoading ? 'Searching documents...' : 'Search Documents'}
          </button>
        </form>

        {documentError && (
          <p className="error-message" role="alert">
            {documentError}
          </p>
        )}

        {documentResults && (

<div className="document-search-results">
  <h3>Evidence Found: {documentResults.result_count}</h3>

  {documentResults.answer && (
    <article className="grounded-answer">
      <h3>Grounded Answer</h3>
      <p>{documentResults.answer}</p>

      {documentResults.status === 'no_evidence' && (
        <p className="placeholder">
          No sufficiently relevant evidence was found.
        </p>
      )}
    </article>
  )}

  {documentResults.sources?.length > 0 && (
    <section className="answer-sources">
      <h3>Sources Supporting This Answer</h3>

      {documentResults.sources.map((source) => (
        <article
          className="source-card"
          key={source.chunk_id}
        >
          <h4>{source.source}</h4>

          <p>
            Project: {source.project_id || 'Not specified'}
            {' · '}
            Invoice: {source.invoice_id || 'Not specified'}
          </p>

          <p>
            Chunk ID: {source.chunk_id}
            {' · '}
            Similarity:{' '}
            {Number(source.similarity_score).toFixed(3)}
          </p>
        </article>
      ))}
    </section>
  )}

  {documentResults.results.length === 0 ? (
    <p className="placeholder">
      No matching documents were found for this project.
    </p>
  ) : (
    <>
      <h3>Retrieved Evidence</h3>

      {documentResults.results.map((item) => (
        <article className="evidence-card" key={item.chunk_id}>
          <div className="evidence-heading">
            <h4>{item.source}</h4>

            <span className="similarity-score">
              Similarity:{' '}
              {Number(item.similarity_score).toFixed(3)}
            </span>
          </div>

          <p className="evidence-text">{item.text}</p>

          <p className="evidence-metadata">
            Project: {item.metadata.project_id || 'Not specified'}
            {' · '}
            Invoice: {item.metadata.invoice_id || 'Not specified'}
            {' · '}
            Chunk: {item.metadata.chunk_number ?? 'Not specified'}
          </p>
        </article>
      ))}
    </>
  )}
</div>

        )}

      {/* Day 4: connect property records to document evidence. */}
      <section className="document-search">
        <h2 className="section-title">Property Evidence</h2>

        <p className="document-description">
          Combine PostgreSQL property and invoice records with
          document evidence verified against property and project IDs.
        </p>

        <form
          className="document-search-form"
          onSubmit={searchPropertyEvidence}
        >
          <label htmlFor="evidence-property-id">Property ID</label>
          <input
            id="evidence-property-id"
            value={evidencePropertyId}
            onChange={(event) => setEvidencePropertyId(event.target.value)}
            placeholder="e.g. P204"
            required
          />

          <label htmlFor="evidence-invoice-id">
            Invoice ID (optional)
          </label>
          <input
            id="evidence-invoice-id"
            value={evidenceInvoiceId}
            onChange={(event) => setEvidenceInvoiceId(event.target.value)}
            placeholder="e.g. INV5004"
          />

          <label htmlFor="evidence-query">Your question</label>
          <textarea
            id="evidence-query"
            value={evidenceQuery}
            onChange={(event) => setEvidenceQuery(event.target.value)}
            rows={3}
            maxLength={1000}
            required
          />

          <button type="submit" disabled={propertyEvidenceLoading}>
            {propertyEvidenceLoading
              ? 'Retrieving evidence...'
              : 'Find Property Evidence'}
          </button>
        </form>

        {propertyEvidenceError && (
          <p className="error-message" role="alert">
            {propertyEvidenceError}
          </p>
        )}

        {propertyEvidence && (
          <div className="document-search-results">
            <article className="grounded-answer">
              <h3>Property</h3>
              <p>
                <strong>{propertyEvidence.property.property_name}</strong>
                {' · '}
                Property ID: {propertyEvidence.property.property_id}
                {' · '}
                Project ID: {propertyEvidence.property.project_id}
              </p>
              <p>
                {propertyEvidence.property.city}
                {' · '}
                Status: {propertyEvidence.property.status}
              </p>

              <h3>Evidence-Based Answer</h3>
              <p>{propertyEvidence.answer}</p>
              <p>
                Evidence status: {propertyEvidence.status}
              </p>
            </article>

            <h3>Structured Financial Records</h3>
            {propertyEvidence.invoices.length === 0 ? (
              <p className="placeholder">No matching invoices found.</p>
            ) : (
              propertyEvidence.invoices.map((invoice) => (
                <article className="evidence-card" key={invoice.invoice_id}>
                  <h4>
                    {invoice.invoice_id}
                    {' · '}
                    {invoice.status}
                  </h4>
                  <p>
                    Property: {invoice.property_id}
                    {' · '}
                    Project: {invoice.project_id}
                  </p>
                  <p>
                    Invoice amount: {formatAmount(invoice.invoice_amount)}
                    {' · '}
                    PO amount:{' '}
                    {invoice.po_total == null
                      ? 'Not available'
                      : formatAmount(invoice.po_total)}
                  </p>
                  <p>
                    Variance:{' '}
                    {invoice.variance == null
                      ? 'Not available'
                      : formatAmount(invoice.variance)}
                  </p>
                </article>
              ))
            )}

            <h3>Verified Document Sources</h3>
            {propertyEvidence.sources.length === 0 ? (
              <p className="placeholder">
                No sufficiently relevant supporting evidence was found.
              </p>
            ) : (
              propertyEvidence.sources.map((source) => (
                <article className="source-card" key={source.chunk_id}>
                  <h4>{source.source}</h4>
                  <p>
                    Property: {source.property_id || 'Not specified'}
                    {' · '}
                    Project: {source.project_id || 'Not specified'}
                    {' · '}
                    Invoice: {source.invoice_id || 'Not specified'}
                  </p>
                </article>
              ))
            )}

            <h3>Retrieved Evidence Passages</h3>
            {propertyEvidence.results.map((item) => (
              <article className="evidence-card" key={item.chunk_id}>
                <h4>{item.source}</h4>
                <p className="evidence-text">{item.text}</p>
                <p className="evidence-metadata">
                  Property: {item.metadata.property_id || 'Not specified'}
                  {' · '}
                  Project: {item.metadata.project_id || 'Not specified'}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>



      </section>

      {/* Existing results panel for financial operations. */}
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
