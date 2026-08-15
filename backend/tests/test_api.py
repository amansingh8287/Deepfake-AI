from io import BytesIO

from PIL import Image


def _png_bytes() -> bytes:
    image = Image.new("RGB", (128, 128), color=(120, 90, 180))
    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_health_endpoint(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_image_validation_rejects_wrong_extension(client) -> None:
    response = client.post(
        "/api/detect/image",
        files={"file": ("bad.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_image_detection_endpoint(client) -> None:
    response = client.post(
        "/api/detect/image",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in {"REAL", "DEEPFAKE"}
    assert "confidence" in data


def test_history_endpoint(client) -> None:
    client.post("/api/detect/image", files={"file": ("sample.png", _png_bytes(), "image/png")})
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_scans"] >= 1

