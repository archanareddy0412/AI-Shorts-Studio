"""Local video downloader.

Supports:
1. YouTube URLs -> downloaded with yt-dlp
2. Local video files -> returned directly
"""

import os
from pathlib import Path

import yt_dlp


def download_youtube_local(video_url: str, fmt: str = "720") -> str:

    # ---------------------------------------------------------
    # 1. LOCAL VIDEO
    # ---------------------------------------------------------
    if os.path.isfile(video_url):
        print(
            f"[download/local] using local file: {video_url}",
            flush=True,
        )
        return video_url

    # ---------------------------------------------------------
    # 2. YOUTUBE VIDEO
    # ---------------------------------------------------------

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"[download/local] {video_url} @ {fmt}p",
        flush=True,
    )

    format_string = (
        f"bv*[height<={fmt}]+ba/"
        f"b[height<={fmt}]"
    )

    options = {
        "format": format_string,

        "outtmpl": str(
            output_dir / "source_%(id)s.%(ext)s"
        ),

        "merge_output_format": "mp4",

        "noplaylist": True,

        # IMPORTANT:
        # Use the same FFmpeg location that worked in your test.
        "ffmpeg_location": r"C:\ffmpeg\bin",

        "quiet": False,
        "no_warnings": False,

        "retries": 5,
        "fragment_retries": 5,

        "continuedl": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                video_url,
                download=True,
            )

            video_id = info.get("id")

            if not video_id:
                raise RuntimeError(
                    "yt-dlp could not determine the YouTube video ID."
                )

            # Expected final file
            mp4_path = (
                output_dir /
                f"source_{video_id}.mp4"
            )

            if mp4_path.exists():

                final_path = mp4_path

            else:

                prepared_path = Path(
                    ydl.prepare_filename(info)
                )

                if prepared_path.exists():

                    final_path = prepared_path

                else:

                    matches = list(
                        output_dir.glob(
                            f"source_{video_id}.*"
                        )
                    )

                    if not matches:
                        raise RuntimeError(
                            "yt-dlp finished, but the "
                            "downloaded video file "
                            "could not be found."
                        )

                    final_path = matches[0]

            print(
                f"[download/local] ready: {final_path}",
                flush=True,
            )

            return str(final_path)

    except Exception as e:

        print(
            f"[download/local] failed: {e}",
            flush=True,
        )

        raise