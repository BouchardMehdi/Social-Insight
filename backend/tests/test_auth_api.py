from fastapi.testclient import TestClient


def register(client: TestClient, email: str, workspace_name: str = "Acme") -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "strong-password-123",
            "display_name": "Ada Lovelace",
            "workspace_name": workspace_name,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_register_login_and_session(anonymous_client: TestClient) -> None:
    registered = register(anonymous_client, "ada@example.com")

    assert registered["token_type"] == "bearer"
    assert registered["user"]["email"] == "ada@example.com"
    assert registered["workspaces"][0]["role"] == "owner"

    login = anonymous_client.post(
        "/api/auth/login",
        json={"email": "ADA@example.com", "password": "strong-password-123"},
    )
    assert login.status_code == 200

    session = anonymous_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert session.status_code == 200
    assert session.json()["active_workspace_id"] == registered["active_workspace_id"]


def test_duplicate_email_and_invalid_password_are_rejected(
    anonymous_client: TestClient,
) -> None:
    register(anonymous_client, "ada@example.com")

    duplicate = anonymous_client.post(
        "/api/auth/register",
        json={
            "email": "ada@example.com",
            "password": "another-password",
            "display_name": "Another Ada",
        },
    )
    invalid_login = anonymous_client.post(
        "/api/auth/login",
        json={"email": "ada@example.com", "password": "wrong-password"},
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "email_already_registered"
    assert invalid_login.status_code == 401


def test_protected_routes_require_authentication(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/api/posts", headers={"X-Workspace-ID": "unknown"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"


def test_workspaces_are_isolated(anonymous_client: TestClient) -> None:
    first = register(anonymous_client, "first@example.com", "First workspace")
    second = register(anonymous_client, "second@example.com", "Second workspace")

    first_headers = {
        "Authorization": f"Bearer {first['access_token']}",
        "X-Workspace-ID": first["active_workspace_id"],
    }
    second_headers = {
        "Authorization": f"Bearer {second['access_token']}",
        "X-Workspace-ID": second["active_workspace_id"],
    }
    created = anonymous_client.post(
        "/api/posts",
        headers=first_headers,
        json={"platform": "twitter", "author": "ada", "content": "Une innovation utile."},
    )

    assert created.status_code == 202
    assert anonymous_client.get("/api/posts", headers=first_headers).json()["total"] == 1
    assert anonymous_client.get("/api/posts", headers=second_headers).json()["total"] == 0

    forbidden = anonymous_client.get(
        "/api/posts",
        headers={
            "Authorization": f"Bearer {second['access_token']}",
            "X-Workspace-ID": first["active_workspace_id"],
        },
    )
    assert forbidden.status_code == 403


def test_user_can_create_and_list_workspaces(anonymous_client: TestClient) -> None:
    auth = register(anonymous_client, "owner@example.com")
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    created = anonymous_client.post(
        "/api/workspaces", headers=headers, json={"name": "Second workspace"}
    )
    listed = anonymous_client.get("/api/workspaces", headers=headers)

    assert created.status_code == 201
    assert created.json()["role"] == "owner"
    assert listed.status_code == 200
    assert [workspace["name"] for workspace in listed.json()] == ["Acme", "Second workspace"]


def test_owner_can_add_an_existing_user_to_a_workspace(anonymous_client: TestClient) -> None:
    owner = register(anonymous_client, "owner@example.com", "Shared workspace")
    member = register(anonymous_client, "member@example.com", "Member workspace")
    workspace_id = owner["active_workspace_id"]
    owner_headers = {
        "Authorization": f"Bearer {owner['access_token']}",
        "X-Workspace-ID": workspace_id,
    }

    added = anonymous_client.post(
        f"/api/workspaces/{workspace_id}/members",
        headers=owner_headers,
        json={"email": "member@example.com", "role": "member"},
    )
    listed = anonymous_client.get(
        f"/api/workspaces/{workspace_id}/members", headers=owner_headers
    )

    assert added.status_code == 201
    assert added.json()["role"] == "member"
    assert len(listed.json()) == 2

    member_session = anonymous_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {member['access_token']}"},
    )
    assert workspace_id in {
        workspace["id"] for workspace in member_session.json()["workspaces"]
    }
