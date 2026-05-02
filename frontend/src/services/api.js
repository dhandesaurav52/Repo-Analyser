import axios from 'axios'

export const analyzeRepo = async (repoUrl) => {
  const { data } = await axios.get('http://localhost:8000/analyze', { params: { repo_url: repoUrl } })
  return data
}
