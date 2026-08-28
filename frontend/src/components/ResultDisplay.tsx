import { useState, useEffect } from 'react'
import { getTaskStatus, getSpriteSheetUrl, getFrameUrl, getFramesDownloadUrl } from '../services/api'
import './ResultDisplay.css'

interface ResultDisplayProps {
  taskId: string | null
  onComplete: () => void
}

function ResultDisplay({ taskId, onComplete }: ResultDisplayProps) {
  const [status, setStatus] = useState<string>('idle')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    if (!taskId) {
      setStatus('idle')
      setResult(null)
      setError('')
      return
    }

    setStatus('polling')
    const pollInterval = setInterval(async () => {
      try {
        const data = await getTaskStatus(taskId)
        setStatus(data.status)

        if (data.status === 'completed') {
          setResult(data)
          clearInterval(pollInterval)
          onComplete()
        } else if (data.status === 'failed') {
          setError('生成失败，请重试')
          clearInterval(pollInterval)
          onComplete()
        }
      } catch (err) {
        setError('查询任务状态失败')
        clearInterval(pollInterval)
        onComplete()
      }
    }, 3000) // 每 3 秒轮询一次

    return () => clearInterval(pollInterval)
  }, [taskId, onComplete])

  if (status === 'idle') {
    return (
      <div className="result-display empty">
        <div className="placeholder">
          <div className="placeholder-icon">🎨</div>
          <p>上传图片并描述动作，开始生成像素动画</p>
        </div>
      </div>
    )
  }

  if (status === 'polling' || status === 'processing') {
    return (
      <div className="result-display loading">
        <div className="loading-spinner"></div>
        <p>正在生成像素动画，请稍候...</p>
        <p className="loading-hint">AI 正在绘制每一帧</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result-display error">
        <p className="error-message">{error}</p>
      </div>
    )
  }

  if (status === 'completed' && result) {
    return (
      <div className="result-display completed">
        <h3>生成完成!</h3>

        {result.sprite_sheet && (
          <div className="result-section">
            <h4>Sprite Sheet</h4>
            <div className="sprite-preview">
              <img
                src={getSpriteSheetUrl(result.task_id)}
                alt="Sprite Sheet"
                className="sprite-image"
              />
            </div>
          </div>
        )}

        {result.frames && result.frames.length > 0 && (
          <div className="result-section">
            <h4>逐帧预览</h4>
            <div className="frames-grid">
              {result.frames.map((_: any, index: number) => (
                <div key={index} className="frame-item">
                  <img
                    src={getFrameUrl(result.task_id, index)}
                    alt={`Frame ${index + 1}`}
                    className="frame-image"
                  />
                  <span className="frame-label">Frame {index + 1}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.palette && result.palette.length > 0 && (
          <div className="result-section">
            <h4>调色板</h4>
            <div className="palette">
              {result.palette.map((color: string, index: number) => (
                <div
                  key={index}
                  className="color-swatch"
                  style={{ backgroundColor: color }}
                  title={color}
                >
                  <span className="color-hex">{color}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.animation_params && (
          <div className="result-section">
            <h4>动画参数</h4>
            <div className="params">
              <div className="param">
                <span className="param-label">帧数:</span>
                <span className="param-value">{result.animation_params.frame_count}</span>
              </div>
              <div className="param">
                <span className="param-label">帧尺寸:</span>
                <span className="param-value">{result.animation_params.frame_size}</span>
              </div>
              <div className="param">
                <span className="param-label">推荐帧间隔:</span>
                <span className="param-value">{result.animation_params.recommended_interval_ms}ms</span>
              </div>
              <div className="param">
                <span className="param-label">循环:</span>
                <span className="param-value">{result.animation_params.is_loop ? '是' : '否'}</span>
              </div>
            </div>
          </div>
        )}

        <div className="download-actions">
          <a
            href={getSpriteSheetUrl(result.task_id)}
            download={`sprite_${result.task_id}.png`}
            className="download-btn"
          >
            下载 Sprite Sheet
          </a>
          <a
            href={getFramesDownloadUrl(result.task_id)}
            download={`frames_${result.task_id}.zip`}
            className="download-btn secondary"
          >
            下载逐帧 PNG (ZIP)
          </a>
        </div>
      </div>
    )
  }

  return null
}

export default ResultDisplay
