import { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

const LANGUAGE_OPTIONS = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'rust', label: 'Rust' },
  { value: 'go', label: 'Go' },
]

const DEFAULT_CODE = {
  python: `# B1Z KODLAB - Python Example
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test
print(f"Fibonacci(10) = {fibonacci(10)}")
`,
  javascript: `// B1Z KODLAB - JavaScript Example
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// Test
console.log(\`Fibonacci(10) = \${fibonacci(10)}\`);
`,
  rust: `// B1Z KODLAB - Rust Example
fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn main() {
    println!("Fibonacci(10) = {}", fibonacci(10));
}
`,
}

export default function CodeEditor() {
  const [code, setCode] = useState(DEFAULT_CODE.python)
  const [language, setLanguage] = useState('python')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang)
    setCode(DEFAULT_CODE[newLang as keyof typeof DEFAULT_CODE] || '')
    setOutput('')
  }

  const handleRunCode = async () => {
    setIsRunning(true)
    setOutput('🚀 Kod çalıştırılıyor...\n\n')

    try {
      const response = await axios.post('/api/execute/run', {
        code,
        language,
        timeout: 5
      })

      if (response.data.success) {
        setOutput(`✅ Başarılı! (${response.data.execution_time.toFixed(3)}s)\n\n${response.data.output}`)
      } else {
        setOutput(`❌ Hata!\n\n${response.data.error}`)
      }
    } catch (error: any) {
      setOutput(`❌ API Hatası:\n\n${error.response?.data?.detail || error.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setOutput('🤖 AI analiz ediyor (MiniMax-M2)...\n\n')

    try {
      const response = await axios.post('/api/ai/analyze', {
        code,
        language,
        context: 'User is learning coding on B1Z KODLAB'
      })

      const feedback = response.data
      let analysisText = `📊 Kod Kalitesi: ${feedback.score}/100\n\n`

      analysisText += `💡 Öneriler:\n${feedback.suggestions.map((s: string, i: number) => `  ${i + 1}. ${s}`).join('\n')}\n\n`

      if (feedback.errors.length > 0) {
        analysisText += `❌ Hatalar:\n${feedback.errors.map((e: string, i: number) => `  ${i + 1}. ${e}`).join('\n')}\n\n`
      }

      if (feedback.optimizations.length > 0) {
        analysisText += `⚡ Optimizasyonlar:\n${feedback.optimizations.map((o: string, i: number) => `  ${i + 1}. ${o}`).join('\n')}\n\n`
      }

      analysisText += `📚 Eğitsel Notlar:\n${feedback.educational_notes}\n`

      if (feedback.perspectives) {
        analysisText += `\n\n🧠 11 Akıl Harmanları:\n`
        feedback.perspectives.forEach((p: any, i: number) => {
          analysisText += `\n${i + 1}. ${p.type.toUpperCase()}:\n${p.feedback.substring(0, 200)}...\n`
        })
      }

      setOutput(analysisText)
    } catch (error: any) {
      setOutput(`❌ AI Analiz Hatası:\n\n${error.response?.data?.detail || error.message}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex gap-4 items-center">
        <select
          value={language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="input-b1z"
        >
          {LANGUAGE_OPTIONS.map(lang => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>

        <button
          onClick={handleRunCode}
          disabled={isRunning}
          className="btn-b1z"
        >
          {isRunning ? '⏳ Çalışıyor...' : '▶️ Çalıştır'}
        </button>

        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="btn-b1z-secondary"
        >
          {isAnalyzing ? '🤖 Analiz Ediliyor...' : '🧠 AI Analiz Et'}
        </button>

        <div className="ml-auto text-sm text-b1z-gray-500">
          <span className="points-111">+111</span> puan kazan
        </div>
      </div>

      {/* Editor */}
      <div className="border-2 border-b1z-gray-700 rounded-lg overflow-hidden">
        <Editor
          height="400px"
          language={language}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
          }}
        />
      </div>

      {/* Output */}
      {output && (
        <div className="bg-b1z-gray-900 border-2 border-b1z-accent rounded-lg p-4">
          <h3 className="text-b1z-accent font-bold mb-2">📤 Çıktı:</h3>
          <pre className="text-sm whitespace-pre-wrap text-b1z-white font-mono">
            {output}
          </pre>
        </div>
      )}
    </div>
  )
}
