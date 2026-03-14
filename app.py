from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.database.db import init_db
from backend.routes.auth import auth_bp
from backend.routes.pronunciation import pronun_bp
from backend.routes.ai_tutor import ai_tutor_bp 
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
print("FLASK APP STARTING...")

CORS(app)

init_db(app)

jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(pronun_bp, url_prefix="/api")
app.register_blueprint(ai_tutor_bp, url_prefix="/api/tutor") 

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/ai-tutor")  
def ai_tutor_page():
    return render_template("ai_tutor.html")

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
