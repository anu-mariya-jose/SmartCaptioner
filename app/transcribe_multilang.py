import os
import subprocess
import whisper
from moviepy import VideoFileClip
from datetime import timedelta

# ===============================
# PATH SETUP
# ===============================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "..", "processed")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# ===============================
# TIME FORMATTER (SRT)
# ===============================

def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((seconds - total_seconds) * 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def write_srt(segments, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(
                f"{format_timestamp(segment['start'])} --> "
                f"{format_timestamp(segment['end'])}\n"
            )
            f.write(segment["text"].strip() + "\n\n")

# ===============================
# MAIN TRANSCRIPTION FUNCTION
# ===============================

def transcribe_audio(video_filename, target_language="en"):
    """
    1. Extract audio from video
    2. Transcribe with Whisper
    3. Generate SRT
    4. Burn subtitles into video using FFmpeg
    """

    # If full path is passed, use it directly
    if os.path.isabs(video_filename):
        video_path = video_filename
    else:
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    print("Processing video:", video_path)

    audio_path = os.path.join(PROCESSED_FOLDER, "temp_audio.wav")
    srt_path = os.path.join(PROCESSED_FOLDER, "output_en.srt")
    output_video_path = os.path.join(PROCESSED_FOLDER, "output_video.mp4")

    # ===============================
    # AUDIO EXTRACTION
    # ===============================
    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(
            audio_path,
            codec="pcm_s16le",
            fps=16000,
            logger=None
        )
        clip.close()
    except Exception as e:
        raise RuntimeError(f"Audio extraction failed: {e}")

    # ===============================
    # WHISPER TRANSCRIPTION
    # ===============================
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Transcribing...")
    result = model.transcribe(
        audio_path,
        task="translate",
        language=target_language
    )

    # ===============================
    # WRITE SRT FILE
    # ===============================
    print("Writing subtitles...")
    write_srt(result["segments"], srt_path)

    # ===============================
    # BURN SUBTITLES USING FFMPEG
    # ===============================
    print("Burning subtitles into video...")

    # Windows-safe SRT path for FFmpeg
    safe_srt = srt_path.replace("\\", "/").replace(":", "\\:")

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"subtitles='{safe_srt}'",
        "-c:a", "copy",
        output_video_path
    ]

    subprocess.run(ffmpeg_command, check=True)

    # ===============================
    # CLEANUP
    # ===============================
    if os.path.exists(audio_path):
        os.remove(audio_path)

    print("SRT exists:", os.path.exists(srt_path))
    print("VIDEO exists:", os.path.exists(output_video_path))
    print("Done! Captioned video saved at:", output_video_path)

    return {
        "srt": srt_path,
        "video": output_video_path
    }
