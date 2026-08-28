import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 分钟超时
})

export interface GenerateParams {
  reference_image?: File
  action_prompt: string
  frame_count?: number
  canvas_size?: string
  animation_type?: string
  style?: string
}

export interface TaskResponse {
  task_id: string
  status: string
  message: string
}

export interface AnimationParams {
  frame_count: number
  frame_size: string
  recommended_interval_ms: number
  is_loop: boolean
}

export interface TaskResult {
  task_id: string
  status: string
  frames: string[]
  sprite_sheet: string
  palette: string[]
  animation_params?: AnimationParams
}

export async function generateAnimation(params: GenerateParams): Promise<TaskResponse> {
  const formData = new FormData()

  if (params.reference_image) {
    formData.append('reference_image', params.reference_image)
  }
  formData.append('action_prompt', params.action_prompt)
  formData.append('frame_count', String(params.frame_count || 4))
  formData.append('canvas_size', params.canvas_size || '64x64')
  formData.append('animation_type', params.animation_type || 'loop')
  formData.append('style', params.style || 'cute')

  // 注意：不要手动设置 Content-Type，浏览器会自动设置带 boundary 的 multipart/form-data
  const response = await api.post<TaskResponse>('/generate', formData, {
    transformRequest: [(data, headers) => {
      delete headers['Content-Type']
      return data
    }],
  })

  return response.data
}

export async function getTaskStatus(taskId: string): Promise<TaskResult> {
  const response = await api.get<TaskResult>(`/task/${taskId}`)
  return response.data
}

export function getSpriteSheetUrl(taskId: string): string {
  return `${API_BASE_URL}/download/sprite/${taskId}`
}

export function getFrameUrl(taskId: string, index: number): string {
  return `${API_BASE_URL}/download/frame/${taskId}/${index}`
}

export function getFramesDownloadUrl(taskId: string): string {
  return `${API_BASE_URL}/download/frames/${taskId}`
}

export interface Palette {
  name: string
  colors: string[]
}

export async function getPalettes(): Promise<Palette[]> {
  const response = await api.get('/palettes')
  return response.data.palettes
}
