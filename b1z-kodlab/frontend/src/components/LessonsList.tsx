import { useState, useEffect } from 'react'
import axios from 'axios'

interface Lesson {
  id: number
  title: string
  description: string
  language: string
  difficulty: number
  exercises: string[]
  points: number
}

interface LessonsListProps {
  onSelectLesson: (lesson: Lesson) => void
}

export default function LessonsList({ onSelectLesson }: LessonsListProps) {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<'all' | string>('all')

  useEffect(() => {
    fetchLessons()
  }, [])

  const fetchLessons = async () => {
    try {
      const response = await axios.get('/api/lessons/')
      setLessons(response.data)
      setLoading(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      setLoading(false)
    }
  }

  const filteredLessons = filter === 'all'
    ? lessons
    : lessons.filter(l => l.language === filter)

  const getDifficultyStars = (difficulty: number) => {
    return '⭐'.repeat(Math.min(difficulty, 11))
  }

  const getLanguageColor = (lang: string) => {
    const colors: Record<string, string> = {
      python: 'text-blue-400',
      javascript: 'text-yellow-400',
      typescript: 'text-blue-500',
      rust: 'text-orange-400',
      go: 'text-cyan-400',
      cpp: 'text-purple-400',
    }
    return colors[lang.toLowerCase()] || 'text-b1z-accent'
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <p className="text-2xl text-b1z-accent animate-pulse">
          📚 Dersler yükleniyor...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card-b1z bg-red-900 border-red-700">
        <p className="text-white">❌ Hata: {error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-b1z">
        <h2 className="text-3xl font-bold mb-4 text-b1z-accent glow-b1z">
          📚 B1Z KODLAB - 11 Ders Modülü
        </h2>
        <p className="text-b1z-gray-500 mb-4">
          Her ders tamamlandığında <span className="points-111">111 puan</span> kazanırsın!
          Son ders <span className="points-1111">1111 puan</span> değerinde! 🎉
        </p>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded ${
              filter === 'all' ? 'btn-b1z' : 'btn-b1z-secondary'
            }`}
          >
            Tümü ({lessons.length})
          </button>
          {['python', 'javascript', 'rust', 'go'].map(lang => (
            <button
              key={lang}
              onClick={() => setFilter(lang)}
              className={`px-4 py-2 rounded ${
                filter === lang ? 'btn-b1z' : 'btn-b1z-secondary'
              }`}
            >
              {lang.charAt(0).toUpperCase() + lang.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Lessons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredLessons.map((lesson) => (
          <div
            key={lesson.id}
            className="card-b1z hover:border-b1z-accent cursor-pointer transition-all duration-300"
            onClick={() => onSelectLesson(lesson)}
          >
            {/* Lesson Header */}
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-b1z-white mb-1">
                  {lesson.id}. {lesson.title}
                </h3>
                <p className={`text-sm font-mono ${getLanguageColor(lesson.language)}`}>
                  {lesson.language.toUpperCase()}
                </p>
              </div>
              <div className={`text-2xl font-bold ${
                lesson.points === 1111 ? 'points-1111' : 'points-111'
              }`}>
                {lesson.points}
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-b1z-gray-500 mb-3">
              {lesson.description}
            </p>

            {/* Difficulty */}
            <div className="mb-3">
              <p className="text-xs text-b1z-gray-500 mb-1">Zorluk:</p>
              <p className="text-sm">{getDifficultyStars(lesson.difficulty)}</p>
            </div>

            {/* Exercises */}
            <div>
              <p className="text-xs text-b1z-gray-500 mb-1">Alıştırmalar:</p>
              <ul className="text-xs space-y-1">
                {lesson.exercises.slice(0, 2).map((ex, idx) => (
                  <li key={idx} className="text-b1z-accent">
                    • {ex}
                  </li>
                ))}
                {lesson.exercises.length > 2 && (
                  <li className="text-b1z-gray-500">
                    +{lesson.exercises.length - 2} daha...
                  </li>
                )}
              </ul>
            </div>

            {/* Start Button */}
            <button className="w-full mt-4 btn-b1z text-sm">
              🚀 Başla
            </button>
          </div>
        ))}
      </div>

      {/* Stats Footer */}
      <div className="card-b1z bg-b1z-gray-900">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-b1z-gray-500 text-sm mb-1">Toplam Ders</p>
            <p className="text-3xl font-bold text-b1z-accent">11</p>
          </div>
          <div>
            <p className="text-b1z-gray-500 text-sm mb-1">Toplam Puan</p>
            <p className="points-1111">{lessons.reduce((sum, l) => sum + l.points, 0)}</p>
          </div>
          <div>
            <p className="text-b1z-gray-500 text-sm mb-1">Tamamlanan</p>
            <p className="text-3xl font-bold text-b1z-white">0/11</p>
          </div>
        </div>
      </div>
    </div>
  )
}
