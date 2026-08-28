import { useState } from 'react'
import './ActionInput.css'

interface ActionInputProps {
  onGenerate: (taskId: string) => void
  isGenerating: boolean
  referenceImage?: File | null
}

function ActionInput({ onGenerate, isGenerating, referenceImage }: ActionInputProps) {
  const [actionPrompt, setActionPrompt] = useState('')
  const [frameCount, setFrameCount] = useState(4)
  const [animationType, setAnimationType] = useState('loop')
  const [style, setStyle] = useState('cute')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!actionPrompt.trim() || isGenerating) return

    try {
      const { generateAnimation } = await import('../services/api')
      const response = await generateAnimation({
        action_prompt: actionPrompt,
        frame_count: frameCount,
        animation_type: animationType,
        style: style,
        reference_image: referenceImage || undefined,
      })
      onGenerate(response.task_id)
    } catch (error) {
      console.error('生成失败:', error)
      alert('生成失败，请检查网络连接或 API Key 配置')
    }
  }

  const presetActions = [
    '害羞地低头捏裙摆',
    '像 RPG 游戏一样走路',
    '待机呼吸，轻微起伏',
    '跳跃，然后落地',
    '挥手打招呼',
    '双手叉腰，得意地笑',
  ]

  return (
    <div className="action-input">
      <h3>动作描述</h3>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            value={actionPrompt}
            onChange={(e) => setActionPrompt(e.target.value)}
            placeholder="描述你想要的动作，例如：害羞地低头捏裙摆"
            rows={3}
            disabled={isGenerating}
          />
        </div>

        <div className="presets">
          <span className="presets-label">快捷动作:</span>
          {presetActions.map((action) => (
            <button
              key={action}
              type="button"
              className="preset-btn"
              onClick={() => setActionPrompt(action)}
              disabled={isGenerating}
            >
              {action}
            </button>
          ))}
        </div>

        <div className="options-row">
          <div className="option-group">
            <label>帧数</label>
            <select
              value={frameCount}
              onChange={(e) => setFrameCount(Number(e.target.value))}
              disabled={isGenerating}
            >
              <option value={4}>4 帧</option>
              <option value={5}>5 帧</option>
              <option value={6}>6 帧</option>
            </select>
          </div>

          <div className="option-group">
            <label>动画类型</label>
            <select
              value={animationType}
              onChange={(e) => setAnimationType(e.target.value)}
              disabled={isGenerating}
            >
              <option value="loop">循环</option>
              <option value="oneshot">单次</option>
            </select>
          </div>

          <div className="option-group">
            <label>风格</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              disabled={isGenerating}
            >
              <option value="cute">可爱</option>
              <option value="cool">酷炫</option>
              <option value="retro">复古</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="generate-btn"
          disabled={!actionPrompt.trim() || isGenerating}
        >
          {isGenerating ? '生成中...' : '生成像素动画'}
        </button>
      </form>
    </div>
  )
}

export default ActionInput
