from flask import Flask
from .routes import bp as main_bp

app = Flask(__name__)
app.register_blueprint(main_bp)
