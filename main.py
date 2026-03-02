import json
import os
from typing import Optional

import sentry_sdk
from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlmodel import Field, Session, SQLModel, create_engine, func, select

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
)


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str
    short_name: str
    short_url: str


database_url = os.getenv("DATABASE_URL", "sqlite:///database.db").replace(
    "postgres://", "postgresql://", 1
)
engine = create_engine(database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = Flask(__name__)

CORS(app, expose_headers=["Content-Range"])

with app.app_context():
    create_db_and_tables()


def get_short_url(short_name):
    return f"https://short.io/{short_name}"


@app.route("/ping")
def pong():
    return jsonify({"result": "pong"})


@app.route("/api/links", methods=["GET"])
def get_links():
    range_param = request.args.get("range")

    with Session(engine) as session:
        total_count = session.exec(select(func.count()).select_from(Link)).one()

        statement = select(Link)

        start, end = 0, total_count
        if range_param:
            try:
                range_list = json.loads(range_param)
                start = range_list[0]
                end = range_list[1]

                limit = end - start
                statement = statement.offset(start).limit(limit)
            except (ValueError, IndexError, TypeError):
                abort(400, description="Invalid range format. Use [start, end]")

        links = session.exec(statement).all()

        response_data = [link.model_dump() for link in links]
        response = make_response(jsonify(response_data))

        actual_end = start + len(links)
        response.headers["Content-Range"] = f"links {start}-{actual_end}/{total_count}"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range"  # Для CORS

        return response, 200


@app.route("/api/links", methods=["POST"])
def create_link():
    data = request.get_json() or {}
    if "original_url" not in data or "short_name" not in data:
        abort(400, description="Missing fields")

    new_link = Link(
        original_url=data["original_url"],
        short_name=data["short_name"],
        short_url=get_short_url(data["short_name"]),
    )
    with Session(engine) as session:
        session.add(new_link)
        session.commit()
        session.refresh(new_link)
        return jsonify(new_link.model_dump()), 201


@app.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)
        return jsonify(link.model_dump()), 200


@app.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id):
    data = request.get_json() or {}
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)

        link.original_url = data.get("original_url", link.original_url)
        link.short_name = data.get("short_name", link.short_name)
        link.short_url = get_short_url(link.short_name)

        session.add(link)
        session.commit()
        session.refresh(link)
        return jsonify(link.model_dump()), 200


@app.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)
        session.delete(link)
        session.commit()
        return "", 204


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


def main():
    print("Hello from devops-engineer-from-scratch-project-313!")
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
