"""Local AI Shorts generation pipeline.

Supports:
1. YouTube URLs -> downloaded locally with yt-dlp
2. Local video files -> processed directly

Pipeline:
download -> transcribe -> find highlights -> crop clips
"""

from typing import Dict, List, Optional


def _run_local(
    youtube_url: str,
    num_clips: int,
    aspect_ratio: str,
    download_format: str,
    language: Optional[str],
) -> Dict:

    # Local processing modules
    from .local.downloader import download_youtube_local
    from .local.transcriber import transcribe_local
    from .local.llm import call_local_llm
    from .local.clipper import crop_highlights_local
    from .highlights import get_highlights

    # ---------------------------------------------------------
    # 1. DOWNLOAD / LOCATE SOURCE VIDEO
    # ---------------------------------------------------------

    print("\n===== STEP 1: DOWNLOAD =====", flush=True)

    source_path = download_youtube_local(
        youtube_url,
        fmt=download_format,
    )

    print(
        f"[pipeline/local] source: {source_path}",
        flush=True,
    )

    # ---------------------------------------------------------
    # 2. TRANSCRIBE
    # ---------------------------------------------------------

    print("\n===== STEP 2: TRANSCRIBE =====", flush=True)

    transcript = transcribe_local(
        source_path,
        language=language,
    )

    if not transcript.get("segments"):
        raise RuntimeError(
            "Whisper produced no segments. "
            "The video may have no detectable speech."
        )

    # ---------------------------------------------------------
    # 3. FIND HIGHLIGHTS
    # ---------------------------------------------------------

    print("\n===== STEP 3: FIND HIGHLIGHTS =====", flush=True)

    highlights_result = get_highlights(
        transcript,
        num_clips=num_clips,
        llm_fn=call_local_llm,
    )

    all_highlights: List[Dict] = (
        highlights_result.get("highlights", [])
    )

    if not all_highlights:
        raise RuntimeError(
            "Highlight generator returned zero clips."
        )

    # Sort by score and keep requested number
    top = sorted(
        all_highlights,
        key=lambda h: int(h.get("score", 0)),
        reverse=True,
    )[:num_clips]

    print(
        f"[pipeline/local] cropping "
        f"{len(top)} of {len(all_highlights)} candidates",
        flush=True,
    )

    # ---------------------------------------------------------
    # 4. CROP / CREATE SHORTS
    # ---------------------------------------------------------

    print("\n===== STEP 4: CREATE SHORTS =====", flush=True)

    shorts = crop_highlights_local(
        source_path,
        top,
        aspect_ratio=aspect_ratio,
    )

    # ---------------------------------------------------------
    # 5. RETURN RESULT
    # ---------------------------------------------------------

    return {
        "mode": "local",
        "source_video_url": source_path,
        "transcript": transcript,
        "highlights": all_highlights,
        "shorts": shorts,
    }


def generate_shorts(
    youtube_url: str,
    num_clips: int = 3,
    aspect_ratio: str = "9:16",
    download_format: str = "720",
    language: Optional[str] = None,
    mode: str = "local",
) -> Dict:
    """Run the local AI Shorts pipeline."""

    mode = (mode or "local").lower()

    if mode != "local":
        raise ValueError(
            "This version is configured for local mode only."
        )

    return _run_local(
        youtube_url=youtube_url,
        num_clips=num_clips,
        aspect_ratio=aspect_ratio,
        download_format=download_format,
        language=language,
    )