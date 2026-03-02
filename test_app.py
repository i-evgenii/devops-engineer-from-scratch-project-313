import pytest
from sqlmodel import SQLModel

from main import app, engine


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.get_json() == {"result": "pong"}


def test_create_link(client):
    payload = {"original_url": "https://hexlet.io/longpath", "short_name": "shortpath"}
    response = client.post("/api/links", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["original_url"] == "https://hexlet.io/longpath"
    assert data["short_url"] == "https://short.io/shortpath"
    assert "id" in data


def test_get_all_links(client):
    client.post(
        "/api/links",
        json={"original_url": "https://hexlet.io/longpath", "short_name": "shortpath"},
    )

    response = client.get("/api/links")
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_get_link_by_id(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://hexlet.io/longpath", "short_name": "shortpath"},
    ).get_json()
    link_id = created["id"]

    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200
    assert response.get_json()["short_name"] == "shortpath"


def test_update_link(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://hexlet.io/longpath", "short_name": "shortpath"},
    ).get_json()

    response = client.put(f"/api/links/{created['id']}", json={"short_name": "newpath"})
    assert response.status_code == 200
    assert response.get_json()["short_name"] == "newpath"


def test_delete_link(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://hexlet.io/longpath", "short_name": "shortpath"},
    ).get_json()

    del_res = client.delete(f"/api/links/{created['id']}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/links/{created['id']}")
    assert get_res.status_code == 404


def test_get_links_pagination(client):
    for i in range(15):
        client.post(
            "/api/links",
            json={
                "original_url": f"https://hexlet.io/long_{i}",
                "short_name": f"short_{i}",
            },
        )

    response = client.get("/api/links?range=[5,10]")

    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 5
    assert "Content-Range" in response.headers
    assert response.headers["Content-Range"].startswith("links 5-10/")
