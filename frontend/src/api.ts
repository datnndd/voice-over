export type JobType = 'stt' | 'tts' | 'subtitle_translate' | 'video_translate'
export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'canceled'
export type ProviderKind = 'stt' | 'tts' | 'translator'
export type ProviderRuntime = 'local' | 'api'
export type RuntimeStatus = 'ready' | 'missing'
export type OutputKind = 'subtitle' | 'audio' | 'video' | 'other'

export type JobParams = {
  name?: string
  source_language?: string
  source_language_code?: string
  target_language?: string
  target_language_code?: string
  detect_language?: string
  subtitle_language?: string
  recogn_type?: number
  model_name?: string
  translate_type?: number
  tts_type?: number
  voice_role?: string
  app_mode?: string
  subtitle_type?: number
  output_srt?: number
  recogn2pass?: boolean
  is_separate?: boolean
  embed_bgm?: boolean
  uvr_models?: string
  uuid?: string
  target_dir?: string
  dirname?: string
  basename?: string
  noextname?: string
  ext?: string
  targetdir_mp4?: string
  [key: string]: unknown
}

export type JobCreate = {
  type: JobType
  params: JobParams
}

export type JobEvent = {
  id: number
  job_id: string
  type: string
  text: string
  created_at: string
}

export type JobRead = {
  id: string
  type: JobType
  status: JobStatus
  params: JobParams
  error: string | null
  target_dir: string | null
  progress_percent: number
  created_at: string
  updated_at: string
}

export type JobDetail = JobRead & {
  events: JobEvent[]
}

export type OutputFile = {
  path: string
  filename: string
  extension: string
  kind: OutputKind
  size_bytes: number
}

export type OutputList = {
  job_id: string
  outputs: OutputFile[]
}

export type ProviderInfo = {
  id: number
  name: string
  kind: ProviderKind
  runtime: ProviderRuntime
  key_name: string | null
  env_var: string | null
  configured: boolean
  config_mode: 'env' | 'local' | 'provider'
}

export type ProviderList = {
  stt: ProviderInfo[]
  tts: ProviderInfo[]
  translators: ProviderInfo[]
}

export type CloneVoiceRef = {
  name: string
  path: string
  ref_text: string
}

export type VoiceInfo = {
  name: string
  value: string
  language: string | null
  gender: 'female' | 'male' | null
}

export type VoiceList = {
  tts_type: number
  language: string | null
  voices: VoiceInfo[]
}

export type RuntimeCheck = {
  provider_kind: ProviderKind | 'system'
  provider_id: number | null
  provider_name: string
  status: RuntimeStatus
  missing: string[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = init?.body instanceof FormData ? init.headers : { 'Content-Type': 'application/json', ...init?.headers }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export const api = {
  baseUrl: API_BASE_URL,
  getProviders: () => request<ProviderList>('/providers'),
  getRuntimeChecks: () => request<RuntimeCheck[]>('/runtime/checks'),
  uploadCloneReference: (file: File, refText: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('ref_text', refText)
    return request<CloneVoiceRef>('/voices/clone-refs', {
      method: 'POST',
      body: formData,
    })
  },
  getVoices: (ttsType: number, language?: string) => {
    const params = new URLSearchParams({ tts_type: String(ttsType) })
    if (language) params.set('language', language)
    return request<VoiceList>(`/voices?${params.toString()}`)
  },
  createJob: (payload: JobCreate) =>
    request<JobRead>('/jobs', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getJob: (jobId: string) => request<JobDetail>(`/jobs/${jobId}`),
  cancelJob: (jobId: string) => request<JobRead>(`/jobs/${jobId}/cancel`, { method: 'POST' }),
  getOutputs: (jobId: string) => request<OutputList>(`/jobs/${jobId}/outputs`),
}
