import os

import sentry_sdk
from flask import Flask, jsonify
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlmodel import SQLModel

from app.database import engine
from app.routes import api_bp

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix="/api")

CORS(app, expose_headers=["Content-Range"])

with app.app_context():
    create_db_and_tables()


@app.route("/ping")
def pong():
    # return jsonify({"result": "pong"})
    return "pong"


@app.errorhandler(404)
def not_found(e):
    return jsonify({"detail": "Resource not found"}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify(
        {"detail": str(e.description) if hasattr(e, "description") else "Bad request"}
    ), 400


@app.errorhandler(422)
def unprocessable(e):
    return jsonify(
        {
            "detail": str(e.description)
            if hasattr(e, "description")
            else "Unprocessable entity"
        }
    ), 422


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


def main():
    print("Hello from devops-engineer-from-scratch-project-313!")
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
