import json

from flask import (
    Blueprint,
    abort,
    jsonify,
    make_response,
    request,
)
from sqlmodel import Session, func, select  # Добавлен func

from app.database import engine
from app.models import Link

api_bp = Blueprint('api', __name__)

def get_short_url(short_name):
    return f"https://short.io/{short_name}"

@api_bp.route("/links", methods=["GET"])
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


@api_bp.route("/links", methods=["POST"])
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


@api_bp.route("/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)
        return jsonify(link.model_dump()), 200


@api_bp.route("/links/<int:link_id>", methods=["PUT"])
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


@api_bp.route("/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)
        session.delete(link)
        session.commit()
        return "", 204
