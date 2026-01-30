from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    current_app
)
import os
from app.transcribe_multilang import transcribe_audio

bp = Blueprint("main", __name__)

# ===============================
# UPLOAD PAGE
# ===============================
@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        language = request.form.get("language", "en")  # Get selected language

        if not file or file.filename == "":
            return "No file selected", 400

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        upload_path = os.path.join(upload_folder, file.filename)
        file.save(upload_path)

        # Pass language in query params to processing
        return redirect(url_for("main.processing", filename=file.filename, lang=language))

    return render_template("upload.html")


# ===============================
# PROCESSING PAGE (UI ONLY)
# ===============================
@bp.route("/processing/<filename>")
def processing(filename):
    """
    Show processing page with loading info.
    Auto-redirect to /run/<filename>?lang=XX
    """
    language = request.args.get("lang", "en")  # Get language from query
    return render_template("processing.html", filename=filename, language=language)


# ===============================
# RUN TRANSCRIPTION (ACTUAL WORK)
# ===============================
@bp.route("/run/<filename>")
def run_processing(filename):
    """
    Run Whisper transcription + FFmpeg embedding.
    After processing, redirect to download page.
    """
    language = request.args.get("lang", "en")  # Get selected language

    try:
        transcribe_audio(filename, target_language=language)
    except Exception as e:
        return f"Error during processing: {e}", 500

    return redirect(url_for("main.download"))


# ===============================
# DOWNLOAD PAGE
# ===============================
@bp.route("/download")
def download():
    """
    Show final download page with video + subtitle file links.
    """
    return render_template(
        "download.html",
        video_file="output_video.mp4",
        subtitle_file="output_en.srt"
    )


# ===============================
# SERVE UPLOADED FILES
# ===============================
@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=False
    )


# ===============================
# SERVE PROCESSED FILES
# ===============================
@bp.route("/processed/<path:filename>")
def processed_file(filename):
    return send_from_directory(
        current_app.config["PROCESSED_FOLDER"],
        filename,
        as_attachment=False
    )

