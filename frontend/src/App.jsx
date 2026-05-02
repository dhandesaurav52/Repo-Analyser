import React, { useState } from 'react'
import { analyzeRepo } from './services/api'
import TreeView from './components/TreeView'

export default function App() {
  const [url, setUrl] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dark, setDark] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!/^https?:\/\/github\.com\/[^/]+\/[^/]+\/?$/.test(url)) return setError('Invalid GitHub URL')
    setLoading(true); setError(''); setData(null)
    try { setData(await analyzeRepo(url)) } catch (e) { setError(e.response?.data?.detail || 'Failed to analyze repository') } finally { setLoading(false) }
  }

  return (
    <div className={dark ? 'app dark' : 'app'}>
      <h1>RepoInsight</h1>
      <button onClick={() => setDark(!dark)}>Toggle {dark ? 'Light' : 'Dark'}</button>
      <form onSubmit={onSubmit}><input value={url} onChange={(e) => setUrl(e.target.value)} placeholder='https://github.com/user/repo' /><button>Analyze</button></form>
      {loading && <p>Loading...</p>}
      {error && <p className='error'>{error}</p>}
      {data && <div className='grid'>
        <section><h3>Metadata</h3><pre>{JSON.stringify(data.metadata, null, 2)}</pre></section>
        <section><h3>Languages</h3><p>Primary: {data.languages.primary}</p><pre>{JSON.stringify(data.languages.breakdown, null, 2)}</pre></section>
        <section><h3>Repo Structure</h3><p>Important: {data.repository_structure.important_files.join(', ') || 'None'}</p><TreeView tree={data.repository_structure.tree} /></section>
        <section><h3>Backend Detection</h3><p>{data.backend_detection.join(', ') || 'Not detected'}</p></section>
        <section><h3>CI/CD</h3><pre>{JSON.stringify(data.cicd, null, 2)}</pre></section>
        <section><h3>DevOps</h3><pre>{JSON.stringify(data.devops, null, 2)}</pre></section>
        <section><h3>Activity</h3><pre>{JSON.stringify(data.activity, null, 2)}</pre></section>
      </div>}
    </div>
  )
}
