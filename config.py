import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'attendance.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24).hex()
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
