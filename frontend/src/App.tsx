import { useState, useCallback } from 'react'
import ImageUploader from './components/ImageUploader'
import ActionInput from './components/ActionInput'
import ResultDisplay from './components/ResultDisplay'
import './App.css'

function App() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [referenceImage, setReferenceImage] = useState<File | null>(null)

  const handleImageSelect = useCallback((file: File | null) => {
    setReferenceImage(file)
  }, [])

  const handleGenerate = useCallback((id: string) => {
    setTaskId(id)
    setIsGenerating(true)
  }, [])

  const handleComplete = useCallback(() => {
    setIsGenerating(false)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Pixel Alchemist</h1>
        <p className="subtitle">像素动画精灵图生成器</p>
      </header>

      <main className="app-main">
        <div className="input-section">
          <ImageUploader onImageSelect={handleImageSelect} />
          <ActionInput
            referenceImage={referenceImage}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
        </div>

        <div className="result-section">
          <ResultDisplay
            taskId={taskId}
            onComplete={handleComplete}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by 通义万相 (WanXiang) | 阿里云百炼平台</p>
      </footer>
    </div>
  )
}

export default App
