from typing import Any, cast

from app.main import app


def response_schema(path: str) -> dict[str, Any]:
    schema = app.openapi()
    response = schema["paths"][path]["get"]["responses"]["200"]
    return cast(dict[str, Any], response["content"]["application/json"]["schema"])


def test_list_complaints_has_an_explicit_openapi_response_model() -> None:
    assert response_schema("/api/complaints") == {"$ref": "#/components/schemas/ComplaintListRead"}


def test_statistics_has_an_explicit_openapi_response_model() -> None:
    assert response_schema("/api/stats") == {"$ref": "#/components/schemas/ComplaintStatsRead"}
