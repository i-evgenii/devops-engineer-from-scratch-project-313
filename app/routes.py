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

from app.database import with_session
from app.models import Link

api_bp = Blueprint("api", __name__)


def get_short_url(short_name: str) -> str:
    return f"https://short.io/r/{short_name}"


def get_paginated_links_db(
    session: Session, range_param: Optional[str]
) -> Tuple[List[Link], int, int]:
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


def get_link_db(session: Session, link_id: int) -> Optional[Link]:
    return session.get(Link, link_id)


def create_link_db(session: Session, data: dict) -> Link:
    new_link = Link(
        original_url=data["original_url"],
        short_name=data["short_name"],
        short_url=get_short_url(data["short_name"]),
    )
    session.add(new_link)
    session.commit()
    session.refresh(new_link)
    return new_link


def update_link_db(session: Session, link_id: int, data: dict) -> Optional[Link]:
    link = session.get(Link, link_id)
    if not link:
        return None
    if "original_url" in data:
        link.original_url = data["original_url"]
    if "short_name" in data:
        link.short_name = data["short_name"]
        link.short_url = get_short_url(link.short_name)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def delete_link_db(session: Session, link_id: int) -> bool:
    link = session.get(Link, link_id)
    if not link:
        return False
    session.delete(link)
    session.commit()
    return True


@api_bp.route("/links", methods=["GET"])
@with_session
def get_links(session: Session):
    range_param = request.args.get("range")
    links, start, total_count = get_paginated_links_db(session, range_param)

    response_data = [link.model_dump() for link in links]
    response = make_response(jsonify(response_data))

    actual_end = start + len(links)
    response.headers["Content-Range"] = f"links {start}-{actual_end}/{total_count}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return response, 200


@api_bp.route("/links", methods=["POST"])
@with_session
def create_link(session: Session):
    data = request.get_json() or {}
    if "original_url" not in data or "short_name" not in data:
        abort(422, description="Missing fields")

    new_link = create_link_db(session, data)
    return jsonify(new_link.model_dump()), 201


@api_bp.route("/links/<int:link_id>", methods=["GET"])
@with_session
def get_link(session: Session, link_id: int):
    link = get_link_db(session, link_id)
    if not link:
        abort(404)
    return jsonify(link.model_dump()), 200


@api_bp.route("/links/<int:link_id>", methods=["PUT"])
@with_session
def update_link(session: Session, link_id: int):
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"detail": {"error": "Invalid JSON body"}}), 422

    if data is None:
        return jsonify({"detail": {"error": "Request body must be valid JSON"}}), 422
    if not isinstance(data, dict):
        return jsonify({"detail": {"error": "JSON body must be an object"}}), 422
    if not data:
        return jsonify(
            {"detail": {"error": "At least one field to update is required"}}
        ), 422

    if "original_url" in data:
        if (
            not isinstance(data["original_url"], str)
            or not data["original_url"].strip()
        ):
            return jsonify(
                {"detail": {"error": "original_url must be a non-empty string"}}
            ), 422
    if "short_name" in data:
        if not isinstance(data["short_name"], str) or not data["short_name"].strip():
            return jsonify(
                {"detail": {"error": "short_name must be a non-empty string"}}
            ), 422

    updated_link = update_link_db(session, link_id, data)
    if not updated_link:
        abort(404)
    return jsonify(updated_link.model_dump()), 200


@api_bp.route("/links/<int:link_id>", methods=["DELETE"])
@with_session
def delete_link(session: Session, link_id: int):
    deleted = delete_link_db(session, link_id)
    if not deleted:
        abort(404)
    return "", 204
