import { useState, useRef } from 'react'
import './ImageUploader.css'

interface ImageUploaderProps {
  onImageSelect?: (file: File | null) => void
}

function ImageUploader({ onImageSelect }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFileName(file.name)
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      onImageSelect?.(file)
    }
  }

  const handleRemove = () => {
    setPreview(null)
    setFileName('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    onImageSelect?.(null)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="image-uploader">
      <h3>上传参考图</h3>
      <p className="hint">可选 - 上传一张图片作为像素画参考</p>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {preview ? (
        <div className="preview-container">
          <img src={preview} alt="预览" className="preview-image" />
          <div className="preview-actions">
            <span className="file-name">{fileName}</span>
            <button onClick={handleRemove} className="remove-btn">
              移除
            </button>
          </div>
        </div>
      ) : (
        <div className="upload-area" onClick={handleClick}>
          <div className="upload-icon">+</div>
          <p>点击上传图片</p>
          <p className="upload-formats">支持 PNG, JPG, WEBP</p>
        </div>
      )}
    </div>
  )
}

export default ImageUploader
