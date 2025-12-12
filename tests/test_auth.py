def test_create_org(test_app):
    # Depending on whether the DB is mocked or real, this might fail if DB is not running.
    # Assuming the strategy is integration test with a running DB (lifespan in main.py handles connection).
    # Since we are using TestClient(app), the lifespan events (startup) will run.
    
    # We need a unique org name to avoid collision if running multiple times on real DB
    import uuid
    org_name = f"testorg{uuid.uuid4().hex[:8]}"
    
    payload = {
        "organization_name": org_name,
        "email": f"admin@{org_name}.com",
        "password": "strongpassword123"
    }
    
    response = test_app.post("/api/v1/org/create", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["organization_name"] == org_name
    assert "collection_name" in data

def test_admin_login(test_app):
    # We need to create an org first to login, or assume one exists.
    # Ideally tests should be isolated.
    # Let's create one first.
    import uuid
    org_name = f"testorglogin{uuid.uuid4().hex[:8]}"
    email = f"admin@{org_name}.com"
    password = "strongpassword123"
    
    test_app.post("/api/v1/org/create", json={
        "organization_name": org_name,
        "email": email,
        "password": password
    })
    
    # Now try to login
    login_payload = {
        "email": email,
        "password": password
    }
    
    response = test_app.post("/api/v1/admin/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
