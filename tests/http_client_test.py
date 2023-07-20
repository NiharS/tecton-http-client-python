from typing import Final
from urllib.parse import urljoin

import pytest
from aioresponses import aioresponses

from tecton_client.exceptions import InvalidParameterError
from tecton_client.exceptions import InvalidURLError
from tecton_client.exceptions import TectonServerException
from tecton_client.exceptions import UnauthorizedError
from tecton_client.http_client import HTTPRequest
from tecton_client.http_client import TectonHttpClient
from tecton_client.tecton_client import TectonClientOptions


@pytest.fixture
def mocked() -> aioresponses:
    with aioresponses() as mock:
        yield mock


class TestHttpClient:
    URL: Final[str] = "https://thisisaurl.ai"
    API_KEY: Final[str] = "abcd1234"
    client_options = TectonClientOptions()

    endpoint: Final[str] = "api/v1/feature-service/get-features"
    full_url: Final[str] = urljoin(URL, endpoint)
    params = {
        "feature_service_name": "fraud_detection_feature_service",
        "join_key_map": {"user_id": "user_205125746682"},
        "request_context_map": {"merch_long": 35.0, "amt": 500.0, "merch_lat": 30.0},
        "workspace_name": "tecton-fundamentals-tutorial-live",
        "metadata_options": None,
    }
    request = {"params": params}
    http_client = TectonHttpClient(
        url=URL,
        api_key=API_KEY,
        client_options=client_options,
    )

    def test_http_client(self) -> None:
        assert not self.http_client.is_closed

    @pytest.mark.asyncio
    async def test_perform_http_request_success(self, mocked: aioresponses) -> None:
        mocked.post(
            url=self.full_url,
            payload={"result": {"features": ["1", 11292.571748310578, "other", 35.6336, -99.2427, None, "5", "25"]}},
        )
        http_request = HTTPRequest(endpoint=self.endpoint, request_body=self.request)
        response = await self.http_client.execute_request(request=http_request)
        assert isinstance(response.result, dict)

    @pytest.mark.asyncio
    async def test_perform_http_request_failure(self, mocked: aioresponses) -> None:
        mocked.post(
            url=self.full_url,
            status=401,
            payload={
                "error": "invalid 'Tecton-key' authorization header. Newly created credentials "
                "may take up to 60 seconds to be usable.",
                "message": "invalid 'Tecton-key' authorization header. Newly created credentials "
                "may take up to 60 seconds to be usable.",
                "code": 16,
            },
        )
        try:
            http_request = HTTPRequest(endpoint=self.endpoint, request_body=self.request)
            await self.http_client.execute_request(request=http_request)
        except Exception as e:
            # Confirm that a child error of :class:`TectonServerException` is raised
            assert isinstance(e, TectonServerException)

    @pytest.mark.parametrize("url", ["", None, "###", "somesite"])
    def test_invalid_url(self, url: object) -> None:
        with pytest.raises(InvalidURLError):
            TectonHttpClient(
                url=url,
                api_key="1234",
                client_options=self.client_options,
            )

    @pytest.mark.parametrize("key", ["", None])
    def test_empty_or_none_key(self, key: object) -> None:
        with pytest.raises(InvalidParameterError):
            TectonHttpClient(
                url=self.URL,
                api_key=key,
                client_options=self.client_options,
            )

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, mocked: aioresponses) -> None:
        mocked.post(
            url=self.full_url,
            status=401,
            reason="Unauthorized: invalid 'Tecton-key' authorization header. "
            "Newly created credentials may take up to 60 seconds to be usable.",
            payload={
                "error": "invalid 'Tecton-key' authorization header. Note that newly created credentials may "
                "take up to 60 seconds to be usable.",
                "message": "invalid 'Tecton-key' authorization header. Note that newly created credentials may "
                "take up to 60 seconds to be usable.",
                "code": 16,
            },
        )
        try:
            http_request = HTTPRequest(endpoint=self.endpoint, request_body=self.request)
            await self.http_client.execute_request(request=http_request)
        except TectonServerException as e:
            assert isinstance(e, UnauthorizedError)

    @pytest.mark.asyncio
    async def test_default_client_options(self) -> None:
        assert self.http_client._client.timeout.connect == 2
        assert self.http_client._client.timeout.total == 2

    @pytest.mark.asyncio
    async def pytest_sessionfinish(self) -> None:
        await self.http_client.close()
