import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { api, type JobDetail, type JobParams, type OutputFile, type ProviderInfo, type ProviderList, type RuntimeCheck, type VoiceInfo } from './api'

type JobPreset = 'hosted' | 'local-qwen' | 'local-funasr'
type WorkflowMode = 'single' | 'multi-speaker'
type LanguageChoice = string

type SelectOption = { value: string; label: string }

const languageOptions: SelectOption[] = [
  { value: 'en', label: 'English - en' },
  { value: 'ko', label: 'Korean - ko' },
  { value: 'ja', label: 'Japanese - ja' },
  { value: 'zh', label: 'Chinese Mandarin Simplified - zh' },
  { value: 'zh-TW', label: 'Chinese Mandarin Traditional - zh-TW' },
  { value: 'zh-HK', label: 'Chinese Cantonese Traditional - zh-HK' },
  { value: 'vi', label: 'Vietnamese - vi' },
  { value: 'other', label: 'Kh\u00e1c' },
]

const sttModelOptions: Record<number, SelectOption[]> = {
  2: [
    { value: '1.7B', label: 'Qwen3-ASR 1.7B Local' },
    { value: '0.6B', label: 'Qwen3-ASR 0.6B Local' },
  ],
  3: [
    { value: 'Fun-ASR-Nano-2512', label: 'Fun-ASR Nano 2512' },
    { value: 'Fun-ASR-MLT-Nano-2512', label: 'Fun-ASR MLT Nano 2512' },
    { value: 'SenseVoiceSmall', label: 'SenseVoice Small' },
    { value: 'paraformer-zh', label: 'Paraformer zh' },
  ],
  7: [
    { value: 'qwen3-asr-flash', label: 'Qwen3-ASR Flash API' },
  ],
  10: [
    { value: 'nova-3', label: 'Deepgram Nova 3' },
  ],
}

const uvrModelOptions: SelectOption[] = [
  { value: 'spleeter', label: 'Spleeter (nhẹ, mặc định)' },
  { value: 'UVR-MDX-NET-Inst_HQ_4', label: 'UVR-MDX-NET Inst HQ 4' },
  { value: 'UVR-MDX-NET-Inst_HQ_1', label: 'UVR-MDX-NET Inst HQ 1' },
  { value: 'UVR-MDX-NET-Inst_HQ_2', label: 'UVR-MDX-NET Inst HQ 2' },
  { value: 'UVR-MDX-NET-Inst_HQ_3', label: 'UVR-MDX-NET Inst HQ 3' },
  { value: 'UVR-MDX-NET-Inst_HQ_5', label: 'UVR-MDX-NET Inst HQ 5' },
  { value: 'UVR-MDX-NET-Inst_Main', label: 'UVR-MDX-NET Inst Main' },
  { value: 'UVR-MDX-NET-Inst_1', label: 'UVR-MDX-NET Inst 1' },
  { value: 'UVR-MDX-NET-Inst_2', label: 'UVR-MDX-NET Inst 2' },
  { value: 'UVR-MDX-NET-Inst_3', label: 'UVR-MDX-NET Inst 3' },
]

function getSttModelOptions(recognType: number) {
  return sttModelOptions[recognType] ?? []
}

function defaultSttModel(recognType: number) {
  return getSttModelOptions(recognType)[0]?.value ?? ''
}

const nova3Languages: SelectOption[] = [
  { value: 'multi', label: 'Multilingual - multi' },
  { value: 'ar', label: 'Arabic - ar' },
  { value: 'be', label: 'Belarusian - be' },
  { value: 'bn', label: 'Bengali - bn' },
  { value: 'bs', label: 'Bosnian - bs' },
  { value: 'bg', label: 'Bulgarian - bg' },
  { value: 'ca', label: 'Catalan - ca' },
  { value: 'zh-HK', label: 'Chinese Cantonese Traditional - zh-HK' },
  { value: 'zh', label: 'Chinese Mandarin Simplified - zh' },
  { value: 'zh-CN', label: 'Chinese Mandarin Simplified - zh-CN' },
  { value: 'zh-Hans', label: 'Chinese Mandarin Simplified - zh-Hans' },
  { value: 'zh-TW', label: 'Chinese Mandarin Traditional - zh-TW' },
  { value: 'zh-Hant', label: 'Chinese Mandarin Traditional - zh-Hant' },
  { value: 'hr', label: 'Croatian - hr' },
  { value: 'cs', label: 'Czech - cs' },
  { value: 'da', label: 'Danish - da' },
  { value: 'nl', label: 'Dutch - nl' },
  { value: 'en', label: 'English - en' },
  { value: 'en-US', label: 'English US - en-US' },
  { value: 'en-AU', label: 'English AU - en-AU' },
  { value: 'en-GB', label: 'English GB - en-GB' },
  { value: 'en-IN', label: 'English IN - en-IN' },
  { value: 'en-NZ', label: 'English NZ - en-NZ' },
  { value: 'et', label: 'Estonian - et' },
  { value: 'fi', label: 'Finnish - fi' },
  { value: 'nl-BE', label: 'Flemish - nl-BE' },
  { value: 'fr', label: 'French - fr' },
  { value: 'fr-CA', label: 'French Canada - fr-CA' },
  { value: 'de', label: 'German - de' },
  { value: 'de-CH', label: 'German Switzerland - de-CH' },
  { value: 'el', label: 'Greek - el' },
  { value: 'gu', label: 'Gujarati - gu' },
  { value: 'he', label: 'Hebrew - he' },
  { value: 'hi', label: 'Hindi - hi' },
  { value: 'hu', label: 'Hungarian - hu' },
  { value: 'id', label: 'Indonesian - id' },
  { value: 'it', label: 'Italian - it' },
  { value: 'ja', label: 'Japanese - ja' },
  { value: 'kn', label: 'Kannada - kn' },
  { value: 'ko', label: 'Korean - ko' },
  { value: 'lv', label: 'Latvian - lv' },
  { value: 'lt', label: 'Lithuanian - lt' },
  { value: 'mk', label: 'Macedonian - mk' },
  { value: 'ms', label: 'Malay - ms' },
  { value: 'mr', label: 'Marathi - mr' },
  { value: 'no', label: 'Norwegian - no' },
  { value: 'fa', label: 'Persian - fa' },
  { value: 'pl', label: 'Polish - pl' },
  { value: 'pt', label: 'Portuguese - pt' },
  { value: 'pt-BR', label: 'Portuguese Brazil - pt-BR' },
  { value: 'pt-PT', label: 'Portuguese Portugal - pt-PT' },
  { value: 'ro', label: 'Romanian - ro' },
  { value: 'ru', label: 'Russian - ru' },
  { value: 'sr', label: 'Serbian - sr' },
  { value: 'sk', label: 'Slovak - sk' },
  { value: 'sl', label: 'Slovenian - sl' },
  { value: 'es', label: 'Spanish - es' },
  { value: 'es-419', label: 'Spanish Latin America - es-419' },
  { value: 'sv', label: 'Swedish - sv' },
  { value: 'tl', label: 'Tagalog - tl' },
  { value: 'ta', label: 'Tamil - ta' },
  { value: 'te', label: 'Telugu - te' },
  { value: 'th', label: 'Thai - th' },
  { value: 'tr', label: 'Turkish - tr' },
  { value: 'uk', label: 'Ukrainian - uk' },
  { value: 'ur', label: 'Urdu - ur' },
  { value: 'vi', label: 'Vietnamese - vi' },
]


const deepgramLanguageLabelByCode = new Map(nova3Languages.map((option) => [option.value, option.label]))

function deepgramOption(value: string): SelectOption {
  return { value, label: deepgramLanguageLabelByCode.get(value) ?? value }
}

function deepgramOptions(values: string[]): SelectOption[] {
  return values.map(deepgramOption)
}

const deepgramNova3Languages = deepgramOptions([
  'ar', 'be', 'bn', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'de', 'el', 'gu',
  'he', 'hi', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'no', 'fa', 'pl', 'pt',
  'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sv', 'tl', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi',
])

const qwenAsrLanguages: SelectOption[] = [
  { value: 'auto', label: 'Auto detect' },
  { value: 'zh', label: 'Chinese Mandarin - zh' },
  { value: 'yue', label: 'Chinese Cantonese - yue' },
  { value: 'en', label: 'English - en' },
  { value: 'ja', label: 'Japanese - ja' },
  { value: 'ko', label: 'Korean - ko' },
]
const funAsrNanoLanguages: SelectOption[] = [
  { value: 'zh', label: 'Chinese Mandarin - zh' },
  { value: 'yue', label: 'Chinese Cantonese - yue' },
  { value: 'en', label: 'English - en' },
  { value: 'ja', label: 'Japanese - ja' },
]
const funAsrMltLanguages: SelectOption[] = [
  { value: 'auto', label: 'Auto detect' },
  ...nova3Languages.filter((option) => ['zh', 'yue', 'en', 'ja', 'ko', 'vi', 'th', 'id', 'ms', 'hi', 'ar', 'ru', 'fr', 'de', 'es', 'pt', 'it', 'tr'].includes(option.value)),
]
const senseVoiceLanguages: SelectOption[] = [
  { value: 'auto', label: 'Auto detect' },
  ...funAsrMltLanguages.filter((option) => option.value !== 'auto'),
]
const paraformerZhLanguages: SelectOption[] = [
  { value: 'zh', label: 'Chinese Mandarin - zh' },
]

function getDeepgramLanguageOptions() {
  return deepgramNova3Languages
}

function getFunAsrLanguageOptions(modelName: string): SelectOption[] {
  if (modelName === 'paraformer-zh') return paraformerZhLanguages
  if (modelName === 'Fun-ASR-Nano-2512') return funAsrNanoLanguages
  if (modelName === 'SenseVoiceSmall') return senseVoiceLanguages
  return funAsrMltLanguages
}

function getSourceLanguageOptions(recognType: number, modelName: string) {
  if (recognType === 10) return getDeepgramLanguageOptions()
  if (recognType === 7) return qwenAsrLanguages
  if (recognType === 2) return qwenAsrLanguages
  if (recognType === 3) return getFunAsrLanguageOptions(modelName)
  return languageOptions
}

function defaultSourceLanguage(options: SelectOption[]) {
  return options.find((option) => option.value === 'en')?.value ?? options.find((option) => option.value === 'auto')?.value ?? options[0]?.value ?? 'other'
}

function formWithValidSource(form: FormState, updates: Partial<FormState>): FormState {
  const next = { ...form, ...updates }
  const nextSourceOptions = getSourceLanguageOptions(next.recogn_type, next.model_name)
  return {
    ...next,
    source_language_choice: isLanguageAllowed(next.source_language_choice, nextSourceOptions) ? next.source_language_choice : defaultSourceLanguage(nextSourceOptions),
  }
}

function isLanguageAllowed(value: string, options: SelectOption[]) {
  return options.some((option) => option.value === value)
}

type FormState = {
  name: string
  source_language_choice: LanguageChoice
  target_language_choice: LanguageChoice
  source_custom_code: string
  target_custom_code: string
  recogn_type: number
  model_name: string
  translate_type: number
  tts_type: number
  voice_role: string
  preset: JobPreset
  workflow_mode: WorkflowMode
  is_separate: boolean
  embed_bgm: boolean
  uvr_models: string
  nums_diariz: number
  speaker_ref_min_seconds: number
  speaker_ref_max_seconds: number
}

const initialForm: FormState = {
  name: 'C:/Users/ddat2/Downloads/voice-over/test.mp4',
  source_language_choice: 'en',
  target_language_choice: 'vi',
  source_custom_code: '',
  target_custom_code: '',
  recogn_type: 10,
  model_name: 'nova-3',
  translate_type: 3,
  tts_type: 28,
  voice_role: 'HoaiMy(Female)',
  preset: 'hosted',
  workflow_mode: 'single',
  is_separate: false,
  embed_bgm: true,
  uvr_models: 'spleeter',
  nums_diariz: 0,
  speaker_ref_min_seconds: 10,
  speaker_ref_max_seconds: 15,
}

function readinessKey(kind: string, id: number | null) {
  return `${kind}:${id ?? 'system'}`
}

function getProviderStatus(provider: ProviderInfo, checks: RuntimeCheck[]) {
  return checks.find((check) => check.provider_kind === provider.kind && check.provider_id === provider.id)
}

function applyPreset(preset: JobPreset, current: FormState): FormState {
  if (preset === 'local-qwen') {
    return formWithValidSource(current, { preset, recogn_type: 2, model_name: defaultSttModel(2) })
  }
  if (preset === 'local-funasr') {
    return formWithValidSource(current, { preset, recogn_type: 3, model_name: defaultSttModel(3) })
  }
  return formWithValidSource(current, { preset, recogn_type: 10, model_name: defaultSttModel(10), translate_type: 3, tts_type: 28 })
}

function resolveLanguageCode(choice: LanguageChoice, customCode: string) {
  return choice === 'other' ? customCode.trim().toLowerCase() : choice
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / 1024 / 1024).toFixed(1)} MB`
}

function buildParams(form: FormState): JobParams {
  const sourceOptions = getSourceLanguageOptions(form.recogn_type, form.model_name)
  const safeSourceChoice = isLanguageAllowed(form.source_language_choice, sourceOptions) ? form.source_language_choice : defaultSourceLanguage(sourceOptions)
  const sourceLanguageCode = resolveLanguageCode(safeSourceChoice, form.source_custom_code)
  const targetLanguageCode = resolveLanguageCode(form.target_language_choice, form.target_custom_code)
  const multiSpeaker = form.workflow_mode === 'multi-speaker'
  return {
    name: form.name.trim(),
    source_language: sourceLanguageCode,
    source_language_code: sourceLanguageCode,
    target_language: targetLanguageCode,
    target_language_code: targetLanguageCode,
    detect_language: sourceLanguageCode,
    subtitle_language: targetLanguageCode,
    recogn_type: Number(form.recogn_type),
    model_name: form.model_name.trim(),
    translate_type: Number(form.translate_type),
    tts_type: Number(form.tts_type),
    voice_role: multiSpeaker ? 'clone' : form.voice_role.trim(),
    app_mode: 'biaozhun',
    subtitle_type: 0,
    output_srt: 0,
    recogn2pass: false,
    is_separate: form.is_separate,
    embed_bgm: form.is_separate ? form.embed_bgm : false,
    uvr_models: form.uvr_models,
    enable_diariz: multiSpeaker,
    nums_diariz: multiSpeaker ? form.nums_diariz : 0,
    speaker_clone_mode: multiSpeaker ? 'auto' : 'off',
    speaker_ref_min_seconds: form.speaker_ref_min_seconds,
    speaker_ref_max_seconds: form.speaker_ref_max_seconds,
  }
}

function LanguageSelect({
  label,
  value,
  customValue,
  options = languageOptions,
  onValueChange,
  onCustomChange,
}: {
  label: string
  value: LanguageChoice
  customValue: string
  options?: SelectOption[]
  onValueChange: (value: LanguageChoice) => void
  onCustomChange: (value: string) => void
}) {
  return (
    <div className="field language-field">
      <label>
        <span>{label}</span>
        <select value={value} onChange={(event) => onValueChange(event.target.value as LanguageChoice)}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      {value === 'other' && (
        <label>
          <span>M\u00e3 ng\u00f4n ng\u1eef</span>
          <input
            placeholder="vd: fr, de, th"
            value={customValue}
            onChange={(event) => onCustomChange(event.target.value)}
          />
        </label>
      )}
    </div>
  )
}

function VoiceSelect({
  value,
  voices,
  onChange,
}: {
  value: string
  voices: VoiceInfo[]
  onChange: (value: string) => void
}) {
  return (
    <label className="field full">
      <span>Voice role</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {voices.map((voice) => (
          <option key={voice.value} value={voice.value}>
            {voice.name}{voice.gender ? ` ? ${voice.gender}` : ''}
          </option>
        ))}
      </select>
    </label>
  )
}

function SttModelSelect({
  recognType,
  value,
  onChange,
}: {
  recognType: number
  value: string
  onChange: (value: string) => void
}) {
  const options = getSttModelOptions(recognType)
  if (options.length === 0) {
    return (
      <label className="field">
        <span>STT model</span>
        <select disabled value="">
          <option value="">{'C\u1ed1 \u0111\u1ecbnh b\u1edfi c\u1ea5u h\u00ecnh provider'}</option>
        </select>
      </label>
    )
  }

  return (
    <label className="field">
      <span>STT model</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} disabled={options.length === 1}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

function ProviderSelect({
  label,
  value,
  providers,
  checks,
  onChange,
}: {
  label: string
  value: number
  providers: ProviderInfo[]
  checks: RuntimeCheck[]
  onChange: (value: number) => void
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(Number(event.target.value))}>
        {providers.map((provider) => {
          const check = getProviderStatus(provider, checks)
          const disabled = check?.status === 'missing'
          return (
            <option key={provider.id} value={provider.id} disabled={disabled}>
              {provider.name} · {provider.runtime}{disabled ? ` · thiếu ${check?.missing.join(', ')}` : ''}
            </option>
          )
        })}
      </select>
    </label>
  )
}

function ProviderBoard({ providers, checks }: { providers: ProviderList | null; checks: RuntimeCheck[] }) {
  const allProviders = providers ? [...providers.stt, ...providers.tts, ...providers.translators] : []
  return (
    <section className="panel provider-panel">
      <div className="panel-title">
        <p>Provider readiness</p>
        <span>{api.baseUrl}</span>
      </div>
      <div className="provider-grid">
        {allProviders.map((provider) => {
          const check = getProviderStatus(provider, checks)
          const ready = check?.status === 'ready'
          return (
            <div className="provider-card" key={`${provider.kind}-${provider.id}`}>
              <div>
                <strong>{provider.name}</strong>
                <small>{provider.kind} · {provider.runtime}</small>
              </div>
              <span className={ready ? 'badge ready' : 'badge missing'}>{ready ? 'ready' : 'missing'}</span>
              {!ready && <em>{check?.missing.join(', ') || 'not checked'}</em>}
            </div>
          )
        })}
      </div>
    </section>
  )
}

function JobProgress({ job, outputs, onCancel }: { job: JobDetail | null; outputs: OutputFile[]; onCancel: () => void }) {
  if (!job) {
    return (
      <section className="panel empty-state">
        <p>Chưa có job.</p>
        <span>Tạo job để xem tiến trình, log, và output.</span>
      </section>
    )
  }

  const progressPercent = Math.max(0, Math.min(100, job.progress_percent ?? (job.status === 'succeeded' ? 100 : 0)))
  const progressLabel = job.status === 'queued' ? '\u0110ang ch\u1edd x\u1eed l\u00fd' : job.status === 'running' ? '\u0110ang x\u1eed l\u00fd' : job.status === 'succeeded' ? 'Ho\u00e0n t\u1ea5t' : job.status === 'failed' ? 'Th\u1ea5t b\u1ea1i' : '\u0110\u00e3 h\u1ee7y'

  return (
    <section className="panel job-panel">
      <div className="job-header">
        <div>
          <p>Job hiện tại</p>
          <strong>{job.id}</strong>
        </div>
        <span className={`status ${job.status}`}>{job.status}</span>
      </div>
      {job.error && <div className="error-box">{job.error}</div>}
      <div className="progress-card">
        <div className="progress-summary">
          <strong>{progressLabel}</strong>
          <span>{progressPercent}%</span>
        </div>
        <div className="progress-track" aria-label={`Job progress ${progressPercent}%`}>
          <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>
      <dl className="meta-grid">
        <div><dt>Input</dt><dd>{job.params.basename ?? job.params.name}</dd></div>
        <div><dt>Output dir</dt><dd>{job.target_dir}</dd></div>
        <div><dt>Updated</dt><dd>{job.updated_at}</dd></div>
      </dl>
      {job.status === 'running' || job.status === 'queued' ? (
        <button className="secondary danger" type="button" onClick={onCancel}>Hủy job</button>
      ) : null}
      <h3>Outputs</h3>
      <div className="output-list">
        {outputs.length === 0 ? <span>Chưa có file output.</span> : outputs.map((output) => (
          <div className="output-row" key={output.path}>
            <span className={`kind ${output.kind}`}>{output.kind}</span>
            <div>
              <strong>{output.filename}</strong>
              <small>{output.path}</small>
            </div>
            <em>{formatBytes(output.size_bytes)}</em>
          </div>
        ))}
      </div>
      <h3>Events</h3>
      <div className="event-list">
        {job.events.slice().reverse().slice(0, 12).map((event) => (
          <div className="event-row" key={event.id}>
            <span>{event.type}</span>
            <p>{event.text}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function App() {
  const [providers, setProviders] = useState<ProviderList | null>(null)
  const [checks, setChecks] = useState<RuntimeCheck[]>([])
  const [form, setForm] = useState<FormState>(initialForm)
  const [job, setJob] = useState<JobDetail | null>(null)
  const [outputs, setOutputs] = useState<OutputFile[]>([])
  const [voices, setVoices] = useState<VoiceInfo[]>([])
  const [cloneFile, setCloneFile] = useState<File | null>(null)
  const [cloneRefText, setCloneRefText] = useState('')
  const [uploadingClone, setUploadingClone] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checksByKey = useMemo(() => new Map(checks.map((check) => [readinessKey(check.provider_kind, check.provider_id), check])), [checks])
  const selectedSttReady = checksByKey.get(readinessKey('stt', form.recogn_type))?.status !== 'missing'
  const selectedTtsReady = checksByKey.get(readinessKey('tts', form.tts_type))?.status !== 'missing'
  const selectedTranslatorReady = checksByKey.get(readinessKey('translator', form.translate_type))?.status !== 'missing'
  const sourceOptions = getSourceLanguageOptions(form.recogn_type, form.model_name)
  const sourceLanguageCode = resolveLanguageCode(form.source_language_choice, form.source_custom_code)
  const targetLanguageCode = resolveLanguageCode(form.target_language_choice, form.target_custom_code)
  const languagesReady = Boolean(sourceLanguageCode && targetLanguageCode)
  const canSubmit = Boolean(form.name.trim()) && languagesReady && selectedSttReady && selectedTtsReady && selectedTranslatorReady && !loading

  async function refreshMetadata() {
    const [providerPayload, checkPayload] = await Promise.all([api.getProviders(), api.getRuntimeChecks()])
    setProviders(providerPayload)
    setChecks(checkPayload)
  }

  async function refreshJob(jobId: string) {
    const [jobPayload, outputPayload] = await Promise.all([api.getJob(jobId), api.getOutputs(jobId)])
    setJob(jobPayload)
    setOutputs(outputPayload.outputs)
  }

  useEffect(() => {
    let active = true
    void Promise.resolve().then(async () => {
      try {
        const [providerPayload, checkPayload] = await Promise.all([api.getProviders(), api.getRuntimeChecks()])
        if (!active) return
        setProviders(providerPayload)
        setChecks(checkPayload)
      } catch (caught) {
        if (!active) return
        setError(caught instanceof Error ? caught.message : String(caught))
      }
    })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!job || !['queued', 'running'].includes(job.status)) return
    const timer = window.setInterval(() => {
      refreshJob(job.id).catch((caught: unknown) => setError(caught instanceof Error ? caught.message : String(caught)))
    }, 2000)
    return () => window.clearInterval(timer)
  }, [job])

  useEffect(() => {
    let active = true
    void api.getVoices(form.tts_type, targetLanguageCode).then((payload) => {
      if (!active) return
      setVoices(payload.voices)
      if (payload.voices.length > 0 && !payload.voices.some((voice) => voice.value === form.voice_role)) {
        const preferred = payload.voices.find((voice) => voice.value === 'HoaiMy(Female)') ?? payload.voices.find((voice) => voice.value !== 'No') ?? payload.voices[0]
        setForm((current) => ({ ...current, voice_role: preferred.value }))
      }
    }).catch((caught: unknown) => {
      if (!active) return
      setError(caught instanceof Error ? caught.message : String(caught))
    })
    return () => {
      active = false
    }
  }, [form.tts_type, form.voice_role, targetLanguageCode])

  async function submitJob() {
    setLoading(true)
    setError(null)
    try {
      const safeForm = formWithValidSource(form, {})
      if (safeForm.source_language_choice !== form.source_language_choice) {
        setForm(safeForm)
      }
      const created = await api.createJob({ type: 'video_translate', params: buildParams(safeForm) })
      const detail = await api.getJob(created.id)
      setJob(detail)
      setOutputs([])
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setLoading(false)
    }
  }

  async function cancelJob() {
    if (!job) return
    setLoading(true)
    try {
      await api.cancelJob(job.id)
      await refreshJob(job.id)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setLoading(false)
    }
  }

  async function uploadCloneReference() {
    if (!cloneFile || !cloneRefText.trim()) return
    setUploadingClone(true)
    setError(null)
    try {
      const uploaded = await api.uploadCloneReference(cloneFile, cloneRefText)
      const payload = await api.getVoices(form.tts_type, targetLanguageCode)
      setVoices(payload.voices)
      setForm((current) => ({ ...current, voice_role: uploaded.name }))
      setCloneFile(null)
      setCloneRefText('')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setUploadingClone(false)
    }
  }

  const allProviders = providers ? [...providers.stt, ...providers.tts, ...providers.translators] : []
  const readyProviderCount = allProviders.filter((provider) => getProviderStatus(provider, checks)?.status === 'ready').length
  const jobStatusLabel = job ? job.status : 'idle'

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Dashboard navigation">
        <div className="brand-block">
          <span className="brand-mark">VO</span>
          <div>
            <strong>Voice-over</strong>
            <small>Studio dashboard</small>
          </div>
        </div>
        <nav className="nav-list">
          <a href="#overview">Tổng quan</a>
          <a href="#create-job">Tạo job</a>
          <a href="#providers">Provider</a>
          <a href="#progress">Tiến trình</a>
        </nav>
        <div className="sidebar-card">
          <span>API</span>
          <strong>{api.baseUrl}</strong>
        </div>
      </aside>

      <div className="dashboard-main">
        <header className="topbar" id="overview">
          <div>
            <span className="eyebrow">Voice-over studio</span>
            <h1>Dịch video, tạo phụ đề, lồng tiếng.</h1>
            <p>Luồng rõ: input → ngôn ngữ → provider → giọng đọc → job/output.</p>
          </div>
          <button className="secondary" type="button" onClick={() => refreshMetadata()}>Refresh readiness</button>
        </header>

        <section className="stat-grid" aria-label="Dashboard summary">
          <div className="stat-card">
            <span>Providers ready</span>
            <strong>{readyProviderCount}/{allProviders.length}</strong>
          </div>
          <div className="stat-card">
            <span>Workflow</span>
            <strong>{form.workflow_mode === 'multi-speaker' ? 'Auto clone' : 'Single voice'}</strong>
          </div>
          <div className="stat-card">
            <span>Job status</span>
            <strong>{jobStatusLabel}</strong>
          </div>
        </section>

        {error && <div className="error-box">{error}</div>}

        <div className="workspace-grid">
          <section className="panel form-panel" id="create-job">
            <div className="panel-title">
              <div>
                <p>Tạo video_translate job</p>
                <span>Không auth · local single-user</span>
              </div>
            </div>

            <div className="form-section">
              <div className="section-heading">
                <span>01</span>
                <div>
                  <strong>Chọn chế độ</strong>
                  <small>Một giọng đọc hoặc tự clone theo speaker.</small>
                </div>
              </div>
              <div className="preset-row">
                <button type="button" className={form.workflow_mode === 'single' ? 'preset active' : 'preset'} onClick={() => setForm({ ...form, workflow_mode: 'single' })}>
                  {'1 gi\u1ecdng \u0111\u1ecdc'}
                </button>
                <button type="button" className={form.workflow_mode === 'multi-speaker' ? 'preset active' : 'preset'} onClick={() => setForm({ ...form, workflow_mode: 'multi-speaker', tts_type: 2, voice_role: 'clone' })}>
                  {'Nhi\u1ec1u ng\u01b0\u1eddi n\u00f3i \u00b7 auto clone'}
                </button>
              </div>
              <div className="preset-row">
                {(['hosted', 'local-qwen', 'local-funasr'] as const).map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    className={form.preset === preset ? 'preset active' : 'preset'}
                    onClick={() => setForm((current) => applyPreset(preset, current))}
                  >
                    {preset === 'hosted' ? 'Deepgram + OpenAI + Azure' : preset === 'local-qwen' ? 'Qwen local STT' : 'FunASR local STT'}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-section">
              <div className="section-heading">
                <span>02</span>
                <div>
                  <strong>Input và ngôn ngữ</strong>
                  <small>Path file local, source language, target language.</small>
                </div>
              </div>
              <label className="field full">
                <span>Video path</span>
                <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
              </label>
              <div className="field-grid">
                <LanguageSelect
                  label="Source"
                  value={form.source_language_choice}
                  customValue={form.source_custom_code}
                  options={sourceOptions}
                  onValueChange={(source_language_choice) => setForm({ ...form, source_language_choice })}
                  onCustomChange={(source_custom_code) => setForm({ ...form, source_custom_code })}
                />
                <LanguageSelect
                  label="Target"
                  value={form.target_language_choice}
                  customValue={form.target_custom_code}
                  onValueChange={(target_language_choice) => setForm({ ...form, target_language_choice })}
                  onCustomChange={(target_custom_code) => setForm({ ...form, target_custom_code })}
                />
              </div>
            </div>

            <div className="form-section">
              <div className="section-heading">
                <span>03</span>
                <div>
                  <strong>Provider pipeline</strong>
                  <small>STT → translate → TTS.</small>
                </div>
              </div>
              <div className="field-grid">
                <ProviderSelect label="STT" value={form.recogn_type} providers={providers?.stt ?? []} checks={checks} onChange={(recogn_type) => {
                const model_name = defaultSttModel(recogn_type)
                setForm(formWithValidSource(form, { recogn_type, model_name }))
              }} />
                <SttModelSelect recognType={form.recogn_type} value={form.model_name} onChange={(model_name) => {
                setForm(formWithValidSource(form, { model_name }))
              }} />
                <ProviderSelect label="Translator" value={form.translate_type} providers={providers?.translators ?? []} checks={checks} onChange={(translate_type) => setForm({ ...form, translate_type })} />
                <ProviderSelect label="TTS" value={form.tts_type} providers={providers?.tts ?? []} checks={checks} onChange={(tts_type) => setForm({ ...form, tts_type, voice_role: form.workflow_mode === 'multi-speaker' ? 'clone' : form.voice_role })} />
              </div>
            </div>

            <div className="form-section">
              <div className="section-heading">
                <span>04</span>
                <div>
                  <strong>Giọng đọc và xử lý audio</strong>
                  <small>Clone voice, speaker split, vocal/background handling.</small>
                </div>
              </div>
              <div className="clone-box">
              <div>
                <strong>{'Lọc giọng nói / tách vocal'}</strong>
                <small>{'Tách vocal + background trước STT; nếu bật ghép BGM, backend nhúng lại nền sau khi lồng tiếng.'}</small>
              </div>
              <label className="check-field">
                <input type="checkbox" checked={form.is_separate} onChange={(event) => setForm({ ...form, is_separate: event.target.checked })} />
                <span>{'Bật tách vocal trước STT'}</span>
              </label>
              <label className="field">
                <span>{'Model tách âm'}</span>
                <select value={form.uvr_models} disabled={!form.is_separate} onChange={(event) => setForm({ ...form, uvr_models: event.target.value })}>
                  {uvrModelOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>
              <label className="check-field">
                <input type="checkbox" checked={form.embed_bgm} disabled={!form.is_separate} onChange={(event) => setForm({ ...form, embed_bgm: event.target.checked })} />
                <span>{'Ghép lại nhạc nền đã tách'}</span>
              </label>
            </div>
            {form.workflow_mode === 'multi-speaker' && (
              <div className="clone-box">
                <div>
                  <strong>{'T\u1ef1 t\u00e1ch ng\u01b0\u1eddi n\u00f3i v\u00e0 clone gi\u1ecdng'}</strong>
                  <small>{'Backend s\u1ebd diarize, gom 10\u201315s audio cho t\u1eebng spk, r\u1ed3i d\u00f9ng OmniVoice clone theo t\u1eebng d\u00f2ng ph\u1ee5 \u0111\u1ec1.'}</small>
                </div>
                <label className="field">
                  <span>{'S\u1ed1 ng\u01b0\u1eddi n\u00f3i'}</span>
                  <select value={form.nums_diariz} onChange={(event) => setForm({ ...form, nums_diariz: Number(event.target.value) })}>
                    <option value={0}>{'T\u1ef1 \u0111\u1ed9ng'}</option>
                    {[2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => <option key={value} value={value}>{value}</option>)}
                  </select>
                </label>
                <div className="field-grid compact">
                  <label className="field">
                    <span>Ref min seconds</span>
                    <input type="number" min={3} max={30} value={form.speaker_ref_min_seconds} onChange={(event) => setForm({ ...form, speaker_ref_min_seconds: Number(event.target.value) })} />
                  </label>
                  <label className="field">
                    <span>Ref max seconds</span>
                    <input type="number" min={5} max={45} value={form.speaker_ref_max_seconds} onChange={(event) => setForm({ ...form, speaker_ref_max_seconds: Number(event.target.value) })} />
                  </label>
                </div>
              </div>
            )}
            {form.workflow_mode === 'single' && <VoiceSelect
              value={form.voice_role}
              voices={voices.length > 0 ? voices : [{ name: form.voice_role || 'No', value: form.voice_role || 'No', language: targetLanguageCode, gender: null }]}
              onChange={(voice_role) => setForm({ ...form, voice_role })}
            />}
            {form.workflow_mode === 'single' && form.tts_type === 2 && (
              <div className="clone-box">
                <div>
                  <strong>{'Clone gi\u1ecdng OmniVoice'}</strong>
                  <small>{'Upload audio m\u1eabu v\u00e0 nh\u1eadp \u0111\u00fang c\u00e2u n\u00f3i trong audio. Role m\u1edbi s\u1ebd xu\u1ea5t hi\u1ec7n trong dropdown gi\u1ecdng \u0111\u1ecdc.'}</small>
                </div>
                <label className="field full">
                  <span>Reference audio</span>
                  <input type="file" accept="audio/*,.wav,.mp3,.m4a,.flac,.ogg" onChange={(event) => setCloneFile(event.target.files?.[0] ?? null)} />
                </label>
                <label className="field full">
                  <span>Reference text</span>
                  <input value={cloneRefText} placeholder={'C\u00e2u n\u00f3i trong audio m\u1eabu'} onChange={(event) => setCloneRefText(event.target.value)} />
                </label>
                <button className="secondary" type="button" disabled={!cloneFile || !cloneRefText.trim() || uploadingClone} onClick={uploadCloneReference}>
                  {uploadingClone ? '\u0110ang upload...' : 'Upload clone voice'}
                </button>
              </div>
            )}
            </div>
            <div className="submit-bar">
              <button className="primary" type="button" disabled={!canSubmit} onClick={submitJob}>
                {loading ? 'Đang xử lý...' : 'Tạo job'}
              </button>
              {!canSubmit && <small className="hint">Điền video path và chọn provider ready để chạy.</small>}
            </div>
          </section>

          <div className="side-stack">
            <div id="providers">
              <ProviderBoard providers={providers} checks={checks} />
            </div>
            <div id="progress">
              <JobProgress job={job} outputs={outputs} onCancel={cancelJob} />
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default App
