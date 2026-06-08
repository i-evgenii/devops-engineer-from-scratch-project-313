import json
from typing import List, Optional, Tuple

from flask import (
    Blueprint,
    abort,
    jsonify,
    make_response,
    request,
)
from sqlmodel import Session, func, select

from app.database import engine
from app.models import Link

api_bp = Blueprint("api", __name__)


def get_short_url(short_name):
    return f"https://short.io/r/{short_name}"


def get_paginated_links(range_param: Optional[str]) -> Tuple[List[Link], int, int]:
    with Session(engine) as session:
        total_count = session.exec(select(func.count()).select_from(Link)).one()
        statement = select(Link)

        start = 0
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
        return links, start, total_count


@api_bp.route("/links", methods=["GET"])
def get_links():
    range_param = request.args.get("range")

    links, start, total_count = get_paginated_links(range_param)

    response_data = [link.model_dump() for link in links]
    response = make_response(jsonify(response_data))

    actual_end = start + len(links)
    response.headers["Content-Range"] = f"links {start}-{actual_end}/{total_count}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return response, 200


@api_bp.route("/links", methods=["POST"])
def create_link():
    data = request.get_json() or {}
    if "original_url" not in data or "short_name" not in data:
        abort(422, description="Missing fields")

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
    try:
        data = request.get_json()
    except Exception:
        abort(422, description={"detail": "Invalid JSON body"})

    if data is None:
        abort(422, description={"detail": "Request body must be valid JSON"})
    if not isinstance(data, dict):
        abort(422, description={"detail": "JSON body must be an object"})
    if not data:
        abort(422, description={"detail": "At least one field to update is required"})

    if "original_url" in data:
        if (
            not isinstance(data["original_url"], str)
            or not data["original_url"].strip()
        ):
            abort(
                422, description={"detail": "original_url must be a non-empty string"}
            )
    if "short_name" in data:
        if not isinstance(data["short_name"], str) or not data["short_name"].strip():
            abort(422, description={"detail": "short_name must be a non-empty string"})

    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            abort(404)

        if "original_url" in data:
            link.original_url = data["original_url"]
        if "short_name" in data:
            link.short_name = data["short_name"]
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
