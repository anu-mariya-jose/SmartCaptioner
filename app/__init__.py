from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "..", "uploads")
    app.config["PROCESSED_FOLDER"] = os.path.join(BASE_DIR, "..", "processed")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["PROCESSED_FOLDER"], exist_ok=True)

    from app.routes import bp
    app.register_blueprint(bp)

    return app

