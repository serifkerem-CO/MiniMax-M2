import { useState } from 'react'
import CodeEditor from './components/CodeEditor'
import AIFeedback from './components/AIFeedback'
import Header from './components/Header'
import LessonsList from './components/LessonsList'

function App() {
  const [activeTab, setActiveTab] = useState<'kodla' | 'kodlat' | 'b1z'>('kodla')
  const [showLessons, setShowLessons] = useState(false)

  return (
    <div className="min-h-screen bg-b1z-gray-900">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="container mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="flex gap-4 mb-8 border-b-2 border-b1z-gray-700 pb-4">
          <button
            onClick={() => setActiveTab('kodla')}
            className={`px-6 py-3 font-bold text-lg transition-all ${
              activeTab === 'kodla'
                ? 'text-b1z-accent border-b-4 border-b1z-accent'
                : 'text-b1z-gray-500 hover:text-b1z-white'
            }`}
          >
            KODLA
          </button>
          <button
            onClick={() => setActiveTab('kodlat')}
            className={`px-6 py-3 font-bold text-lg transition-all ${
              activeTab === 'kodlat'
                ? 'text-b1z-accent border-b-4 border-b1z-accent'
                : 'text-b1z-gray-500 hover:text-b1z-white'
            }`}
          >
            KODLAT
          </button>
          <button
            onClick={() => setActiveTab('b1z')}
            className={`px-6 py-3 font-bold text-lg transition-all ${
              activeTab === 'b1z'
                ? 'text-b1z-accent border-b-4 border-b1z-accent'
                : 'text-b1z-gray-500 hover:text-b1z-white'
            }`}
          >
            B1Z
          </button>

          <button
            onClick={() => setShowLessons(!showLessons)}
            className="ml-auto btn-b1z-secondary"
          >
            {showLessons ? 'Editöre Dön' : '11 Ders 📚'}
          </button>
        </div>

        {/* Content */}
        {showLessons ? (
          <LessonsList onSelectLesson={() => setShowLessons(false)} />
        ) : (
          <>
            {activeTab === 'kodla' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card-b1z">
                  <h2 className="text-2xl font-bold mb-4 text-b1z-accent">
                    🚀 Canlı Kod Editörü
                  </h2>
                  <CodeEditor />
                </div>

                <div className="card-b1z">
                  <h2 className="text-2xl font-bold mb-4 text-b1z-accent">
                    🤖 AI Feedback (MiniMax-M2)
                  </h2>
                  <AIFeedback />
                </div>
              </div>
            )}

            {activeTab === 'kodlat' && (
              <div className="card-b1z">
                <h2 className="text-3xl font-bold mb-4 text-b1z-accent glow-b1z">
                  🎓 KODLAT - AI Öğretmeni
                </h2>
                <p className="text-lg mb-6">
                  "Bana X'i Öğret" diyerek adım adım öğrenmeye başla!
                </p>
                <div className="bg-b1z-gray-900 border-2 border-b1z-accent rounded-lg p-8 text-center">
                  <p className="text-2xl mb-4">🔜 Çok Yakında!</p>
                  <p className="text-b1z-gray-500">
                    AI öğretmeni modülü geliştiriliyor...
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'b1z' && (
              <div className="card-b1z">
                <h2 className="text-3xl font-bold mb-4 text-b1z-accent glow-b1z">
                  👥 B1Z - Topluluk
                </h2>
                <p className="text-lg mb-6">
                  Kodlama topluluğuyla birlikte öğren, paylaş, geliştir!
                </p>
                <div className="bg-b1z-gray-900 border-2 border-b1z-accent rounded-lg p-8 text-center">
                  <p className="text-2xl mb-4">🔜 Çok Yakında!</p>
                  <p className="text-b1z-gray-500">
                    Topluluk özellikleri geliştiriliyor...
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-b1z-gray-700 mt-16 py-8 text-center text-b1z-gray-500">
        <p className="text-sm">
          Powered by <span className="text-b1z-accent font-bold">MiniMax-M2</span>
        </p>
        <p className="text-xs mt-2">
          Built with <span className="glow-b1z">11111111111111111111 Energy</span> ⚡
        </p>
      </footer>
    </div>
  )
}

export default App
