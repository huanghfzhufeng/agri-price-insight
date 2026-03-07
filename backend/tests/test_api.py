def test_login_and_profile(client):
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123456"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]

    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"


def test_price_query_pagination_and_export(client, auth_headers):
    response = client.get("/api/v1/prices?page=1&page_size=5", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 5
    assert len(payload["items"]) <= 5

    export_response = client.get("/api/v1/prices/export?product=大蒜", headers=auth_headers)
    assert export_response.status_code == 200
    assert "日期,品名,分类" in export_response.text


def test_analysis_endpoints(client, auth_headers):
    overview = client.get("/api/v1/analysis/overview?product=大蒜&market=全国均价", headers=auth_headers)
    trend = client.get("/api/v1/analysis/trend?product=大蒜&days=90", headers=auth_headers)
    monthly = client.get("/api/v1/analysis/monthly?product=大蒜&market=全国均价", headers=auth_headers)
    regions = client.get("/api/v1/analysis/regions?product=大蒜", headers=auth_headers)
    volatility = client.get("/api/v1/analysis/volatility?window_days=30", headers=auth_headers)
    anomalies = client.get("/api/v1/analysis/anomalies?product=大蒜&market=全国均价", headers=auth_headers)

    assert overview.status_code == 200
    assert trend.status_code == 200
    assert monthly.status_code == 200
    assert regions.status_code == 200
    assert volatility.status_code == 200
    assert anomalies.status_code == 200
    assert overview.json()["metrics"]
    assert trend.json()["series"]
    assert volatility.json()["items"]


def test_forecast_endpoint(client, auth_headers):
    response = client.get("/api/v1/alerts/forecast?product=大蒜&days=30", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["history"]
    assert payload["forecast"]
    assert payload["available_models"]
    assert "mape" in payload
    assert "rmse" in payload
    assert "mae" in payload


def test_system_management_endpoints(client, auth_headers):
    task_logs = client.get("/api/v1/system/task-logs", headers=auth_headers)
    raw_records = client.get("/api/v1/system/raw-records", headers=auth_headers)
    data_sources = client.get("/api/v1/system/data-sources", headers=auth_headers)
    thresholds = client.get("/api/v1/system/thresholds", headers=auth_headers)
    report_assets = client.get("/api/v1/system/report-assets", headers=auth_headers)

    assert task_logs.status_code == 200
    assert raw_records.status_code == 200
    assert data_sources.status_code == 200
    assert thresholds.status_code == 200
    assert report_assets.status_code == 200

    threshold_item = thresholds.json()["items"][0]
    update_payload = {
        "warning_ratio": threshold_item["warning_ratio"],
        "critical_ratio": threshold_item["critical_ratio"],
        "std_multiplier": threshold_item["std_multiplier"],
    }
    update_response = client.put(
        f"/api/v1/system/thresholds/{threshold_item['id']}",
        headers=auth_headers,
        json=update_payload,
    )
    assert update_response.status_code == 200
