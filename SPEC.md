# Spec: `web_core_reference` Headless Snapshot

## 1. Mục Tiêu

Tạo `web_core_reference` làm folder tham khảo logic xử lý từ repo `pyvideotrans`, dùng cho app web sau này. Folder này giữ logic dịch, STT, TTS, voice-over, dubbing, subtitle, video pipeline, provider hiện có; bỏ UI WinForm/Qt.

Code chính đã tạo:

- Facade API: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\api.py:51`
- Signal headless: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\signal_hub.py:18`
- Threadpool headless: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\task\simple_runnable_qt.py:8`
- Lazy process exports: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\process\__init__.py:5`
- PySide locale fallback: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\config.py:18`
- Optional provider error fallback: `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\excepts.py:8`

## 2. User Stories

### Story 1: Developer dùng logic gốc không cần WinForm

**As a** web app developer  
**I want** có folder `web_core_reference` chứa logic xử lý core  
**So that** tôi có thể tham khảo hoặc import logic dịch, dubbing, voice-over mà không phụ thuộc WinForm.

**Acceptance Criteria**
- Folder `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference` tồn tại.
- Folder không chứa `winform`, `mainwin`, `ui`, `component` UI-only.
- Import core không yêu cầu mở giao diện desktop.
- `python -m compileall -q web_core_reference` chạy thành công.

### Story 2: Developer gọi STT qua facade

**As a** backend/web developer  
**I want** gọi `run_stt(params)`  
**So that** tôi có thể chạy flow speech-to-text giống CLI cũ.

**Acceptance Criteria**
- Hàm tồn tại tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\api.py:51`.
- Hàm nhận `params: dict`.
- Hàm dùng `TaskCfgSTT`.
- Hàm chạy thứ tự: `prepare()`, `recogn()`, `diariz()`, `task_done()`.
- Hàm trả dict gồm `status`, `target_dir`, `outputs`, `error`.
- Nếu lỗi provider/model/API key, hàm trả `status: "error"` và không crash process cha.

### Story 3: Developer gọi TTS/voice-over qua facade

**As a** backend/web developer  
**I want** gọi `run_tts(params)`  
**So that** tôi có thể chạy text-to-speech/voice-over logic từ repo gốc.

**Acceptance Criteria**
- Hàm tồn tại tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\api.py:64`.
- Hàm nhận `params: dict`.
- Hàm dùng `TaskCfgTTS`.
- Hàm chạy thứ tự: `prepare()`, `dubbing()`, `align()`, `task_done()`.
- Hàm trả output metadata thống nhất.
- Không gọi WinForm hoặc Qt dialog khi thiếu API key.

### Story 4: Developer gọi dịch subtitle qua facade

**As a** backend/web developer  
**I want** gọi `run_subtitle_translate(params)`  
**So that** tôi có thể dịch SRT/subtitle bằng logic translator hiện có.

**Acceptance Criteria**
- Hàm tồn tại tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\api.py:77`.
- Hàm nhận `params: dict`.
- Hàm dùng `TaskCfgSTS`.
- Hàm chạy thứ tự: `prepare()`, `trans()`, `task_done()`.
- Hàm giữ provider translator hiện có.
- Hàm trả `outputs` là danh sách file trong `target_dir` nếu có.

### Story 5: Developer gọi video translate/dubbing pipeline

**As a** backend/web developer  
**I want** gọi `run_video_translate(params)`  
**So that** tôi có thể tham khảo full pipeline video translate + dubbing.

**Acceptance Criteria**
- Hàm tồn tại tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\api.py:89`.
- Hàm nhận `params: dict`.
- Hàm dùng `TaskCfgVTT`.
- Hàm chạy thứ tự: `prepare()`, `recogn()`, `diariz()`, `trans()`, `dubbing()`, `align()`, `recogn2pass()`, `assembling()`, `task_done()`.
- Hàm không cần web framework.
- Hàm giữ logic gốc ở mức tối đa, chỉ vá phần headless.

## 3. Giai Đoạn Triển Khai

### Phase 1: Snapshot Core Logic

**Mục tiêu**  
Copy logic core từ `videotrans` sang `web_core_reference`.

**Included**
- `task`
- `process`
- `translator`
- `recognition`
- `tts`
- `util`
- `configure`
- `prompts`
- `voicejson`
- `language`
- `codes`

**Excluded**
- `winform`
- `mainwin`
- `ui`
- `component`
- Qt worker/UI files trực tiếp: `job.py`, `only_one.py`, `mult_video.py`, `child_win_sign.py`, `separate_worker.py`

**Acceptance Criteria**
- `web_core_reference` tồn tại.
- Core modules tồn tại trong folder mới.
- UI folders không tồn tại trong folder mới.
- Snapshot không sửa logic gốc trong `videotrans`.

### Phase 2: Headless Compatibility

**Mục tiêu**  
Loại dependency UI khỏi import path.

**Implemented**
- `SignalHub` headless no-op/callback tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\signal_hub.py:18`.
- Threadpool thay Qt `QThreadPool` tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\task\simple_runnable_qt.py:8`.
- `QLocale` fallback khi thiếu PySide6 tại `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\config.py:18`.
- Provider API-key checks trả message thay vì mở WinForm.

**Acceptance Criteria**
- Import `web_core_reference.api` không mở UI.
- Không có runtime dependency bắt buộc vào `winform`.
- Không có `QThread`, `QDialog`, `QMessageBox` trong flow import chính.
- Nếu PySide6 không có, config vẫn import được.

### Phase 3: Facade API

**Mục tiêu**  
Tạo API gọi được từ web/backend sau này.

**Public Interface**
```python
from web_core_reference.api import (
    run_stt,
    run_tts,
    run_subtitle_translate,
    run_video_translate,
)
```

**Response Shape**
```python
{
    "status": "success" | "error",
    "target_dir": str | None,
    "outputs": list[str],
    "error": str | None,
}
```

**Acceptance Criteria**
- 4 hàm public tồn tại.
- Input giữ dạng `params: dict`, tương thích CLI config keys.
- Không thêm FastAPI/Flask.
- Không đổi provider protocol.
- Lỗi được đóng gói trong response dict.

### Phase 4: Optional Dependency Tolerance

**Mục tiêu**  
Import snapshot không gãy khi thiếu provider-specific package.

**Implemented**
- `deepgram`, `elevenlabs`, `openai` exception fallback trong `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\configure\excepts.py:8`.
- `ten_vad` fallback trong VAD.
- `soundfile`/`numpy` optional fallback cho import path liên quan alignment.
- Lazy exports trong `C:\Users\ddat2\Downloads\pyvideotrans\web_core_reference\process\__init__.py:5`.

**Acceptance Criteria**
- Import facade không yêu cầu cài toàn bộ provider SDK.
- Khi provider thật được dùng nhưng dependency thiếu, lỗi rõ ràng ở runtime.
- Không mock provider behavior giả.
- Không nuốt lỗi xử lý thật.

### Phase 5: Validation

**Commands**
```powershell
python -m compileall -q web_core_reference
```

Import smoke:
```python
import importlib

mods = [
    "web_core_reference.api",
    "web_core_reference.task.taskcfg",
    "web_core_reference.task.speech2text",
    "web_core_reference.task.translate_srt",
    "web_core_reference.task.dubbing",
    "web_core_reference.task.trans_create",
    "web_core_reference.translator",
    "web_core_reference.recognition",
    "web_core_reference.tts",
]

for mod in mods:
    importlib.import_module(mod)
```

**Acceptance Criteria**
- `compileall` pass.
- Import smoke pass.
- `TaskCfgSTT`, `TaskCfgTTS`, `TaskCfgSTS`, `TaskCfgVTT` khởi tạo được.
- `git status` chỉ thấy folder mới `web_core_reference/` nếu chưa stage.

## 4. Non-Goals

- Không xây web server.
- Không thêm FastAPI/Flask.
- Không rewrite architecture.
- Không bỏ provider hiện có.
- Không thay đổi repo gốc `videotrans`.
- Không đảm bảo mọi provider chạy nếu thiếu API key/model/native dependency.
- Không tạo UI thay thế.

## 5. Definition of Done

- `web_core_reference` có thể dùng làm reference headless.
- Facade API tồn tại và import được.
- Core flow giữ tương đương CLI.
- UI desktop đã tách khỏi import path chính.
- Validation compile/import pass.