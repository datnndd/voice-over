from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app_core.util import tools


@dataclass(frozen=True)
class SpeakerReference:
    speaker: str
    ref_wav: str
    ref_text: str
    duration_ms: int
    lines: list[int]


def _speaker_name(value: Any) -> str:
    text = str(value or 'spk0').strip()
    match = re.search(r'spk\d+', text, flags=re.IGNORECASE)
    return match.group(0).lower() if match else 'spk0'


def _line_duration(item: Any) -> int:
    try:
        return max(0, int(item['end_time']) - int(item['start_time']))
    except Exception:
        return 0


def _concat_segments(segment_files: list[Path], out_file: Path) -> None:
    concat_file = out_file.with_suffix('.txt')
    concat_file.write_text('\n'.join(f"file '{item.as_posix()}'" for item in segment_files), encoding='utf-8')
    tools.runffmpeg(['-y', '-f', 'concat', '-safe', '0', '-i', concat_file.as_posix(), '-c:a', 'pcm_s16le', out_file.as_posix()])
    concat_file.unlink(missing_ok=True)


def build_speaker_references(
    *,
    audio_file: str,
    source_subs: list[Any],
    speaker_file: str,
    output_dir: str,
    min_seconds: int = 10,
    max_seconds: int = 15,
) -> dict[str, SpeakerReference]:
    path = Path(speaker_file)
    if not path.exists() or not source_subs:
        return {}

    speakers = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(speakers, list):
        return {}

    max_ms = max(1000, int(max_seconds * 1000))
    min_ms = max(0, int(min_seconds * 1000))
    ref_root = Path(output_dir) / 'speaker_refs'
    ref_root.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[tuple[int, Any]]] = {}
    for index, item in enumerate(source_subs):
        if index >= len(speakers):
            continue
        speaker = _speaker_name(speakers[index])
        if _line_duration(item) <= 0:
            continue
        grouped.setdefault(speaker, []).append((index, item))

    references: dict[str, SpeakerReference] = {}
    for speaker, items in grouped.items():
        selected: list[tuple[int, Any]] = []
        total_ms = 0
        for index, item in items:
            if total_ms >= min_ms:
                break
            duration = _line_duration(item)
            if total_ms + duration > max_ms and selected:
                continue
            selected.append((index, item))
            total_ms += duration

        if not selected:
            continue

        segment_files: list[Path] = []
        for segment_index, (_, item) in enumerate(selected):
            segment_file = ref_root / f'{speaker}-{segment_index}.wav'
            tools.cut_from_audio(audio_file=audio_file, ss=item['startraw'], to=item['endraw'], out_file=segment_file.as_posix())
            segment_files.append(segment_file)

        ref_wav = ref_root / f'{speaker}.wav'
        if len(segment_files) == 1:
            segment_files[0].replace(ref_wav)
        else:
            _concat_segments(segment_files, ref_wav)
            for segment_file in segment_files:
                segment_file.unlink(missing_ok=True)

        ref_text = ' '.join(str(item['text']).strip() for _, item in selected if str(item['text']).strip())
        references[speaker] = SpeakerReference(
            speaker=speaker,
            ref_wav=ref_wav.as_posix(),
            ref_text=ref_text,
            duration_ms=total_ms,
            lines=[int(item['line']) for _, item in selected],
        )

    (ref_root / 'speakers.json').write_text(
        json.dumps({key: asdict(value) for key, value in references.items()}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    return references
