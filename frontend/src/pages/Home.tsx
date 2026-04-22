/**
 * Home page — landing page with hero section and feature highlights.
 */

import { useNavigate } from 'react-router-dom'
import UploadZone from '../components/UploadZone'
import { contractsApi } from '../services/api'
import { useState } from 'react'

export default function Home() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const handleUpload = async (file: File) => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/register')
      return
    }

    setIsLoading(true)
    try {
      const { data } = await contractsApi.upload(file)
      navigate(`/analysis/${data.id}`)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      alert(axiosErr.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const features = [
    { icon: '🔍', title: 'Instant Analysis', desc: 'Get results in under 60 seconds for any contract.' },
    { icon: '⚖️', title: 'Expert-level Review', desc: 'AI trained to think like a contract lawyer reviewing your interests.' },
    { icon: '📊', title: 'Risk Scoring', desc: 'Each clause rated Low / Medium / High with a numeric score.' },
    { icon: '📝', title: 'Plain English', desc: 'Complex legalese translated into clear, actionable language.' },
    { icon: '🚩', title: 'Red Flag Detection', desc: 'Automatically surfaces unfair, unusual, or dangerous clauses.' },
    { icon: '📥', title: 'Downloadable Report', desc: 'Export a professional PDF report to share with your team.' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="inline-flex items-center gap-2 bg-brand-50 text-brand-500 rounded-full px-4 py-1.5 text-sm font-semibold mb-6 border border-brand-100">
          🛡️ AI-Powered Contract Review
        </div>
        <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
          Know Your Contract Risks
          <br />
          <span className="text-brand-500">Before You Sign</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
          Upload any PDF or DOCX contract and get an instant AI-powered risk score, red-flag alerts,
          and plain-English clause breakdowns — in seconds.
        </p>

        {/* Upload zone in hero */}
        <div className="max-w-xl mx-auto mb-6">
          <UploadZone onUpload={handleUpload} isLoading={isLoading} />
        </div>
        <p className="text-sm text-gray-400">
          First analysis free · No credit card required · PDF &amp; DOCX supported
        </p>
      </section>

      {/* Feature grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          Everything you need to review a contract confidently
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
              <p className="text-gray-600 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing teaser */}
      <section className="bg-brand-500 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Simple, transparent pricing</h2>
          <p className="text-brand-100 text-lg mb-8">Start free. Pay only when you need more.</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              { plan: 'Free', price: '$0', desc: '1 analysis/month', cta: 'Get started' },
              { plan: 'Pay-as-you-go', price: '$3', desc: 'per contract', cta: 'Buy credits' },
              { plan: 'Pro', price: '$29/mo', desc: '20 analyses/month', cta: 'Subscribe' },
            ].map((p) => (
              <div key={p.plan} className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
                <h3 className="font-bold text-lg mb-1">{p.plan}</h3>
                <div className="text-3xl font-extrabold mb-1">{p.price}</div>
                <p className="text-brand-100 text-sm mb-4">{p.desc}</p>
                <button className="w-full bg-white text-brand-500 font-semibold rounded-lg px-4 py-2 text-sm hover:bg-brand-50 transition-colors">
                  {p.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
