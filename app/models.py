from app import db
from datetime import datetime

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(200))
    audio_path = db.Column(db.String(200))
    srt_path = db.Column(db.String(200))
    output_video_path = db.Column(db.String(200))
    status = db.Column(db.String(50), default='uploaded')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
