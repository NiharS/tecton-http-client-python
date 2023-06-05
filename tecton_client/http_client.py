from enum import Enum
from typing import Optional
from typing import Self
from urllib.parse import urlparse

from tecton_client.exceptions import (
    InvalidParameterException,
    InvalidParameterMessage, INVALID_SERVER_RESPONSE
)
import httpx
from httpx_auth import HeaderApiKey


API_PREFIX = "Tecton-key"


class TectonHttpClient:
    """Basic HTTP Client to send and receive requests to a given URL."""

    class headers(Enum):
        AUTHORIZATION = 'Authorization'
        ACCEPT = 'Accept'
        CONTENT_TYPE = 'Content-Type'

    def __init__(self: Self, url: str, api_key: str,
                 client: Optional[httpx.AsyncClient] = None) -> None:
        """
        Constructor that configures the url, api_key and
        client to make HTTP requests

        :param url: URL to ping
        :param api_key: API Key required as part of header authorization
        :param client: (Optional) HTTPX Asynchronous Client
        """

        self.url = self.validate_url(url)
        self.api_key = self.validate_key(api_key)

        self.auth = HeaderApiKey(header_name=self.headers.AUTHORIZATION.value,
                                 api_key=f"{API_PREFIX} {self.api_key}")

        self.client: httpx.AsyncClient = client or httpx.AsyncClient()
        self.is_client_closed = False

    async def close(self: Self) -> None:
        await self.client.aclose()
        self.is_client_closed = True

    @property
    def is_closed(self: Self) -> bool:
        return self.is_client_closed

    async def execute_request(self: Self, endpoint: str,
                              http_request: dict) -> str:
        """
        This is a method that performs a given HTTP request
        to an endpoint in the method passed by client

        :param http_request: request data to be passed
        :param endpoint: HTTP endpoint to attach to the URL and query
        :type http_request: String in JSON format
        :type endpoint: String
        """
        url = f"{self.url}/{endpoint}"

        response = await self.client.post(url, data=http_request,
                                          auth=self.auth)

        if response.status_code == 200:
            return response.json()
        else:
            INVALID_SERVER_RESPONSE(response)

    @staticmethod
    def validate_url(url: Optional[str]) -> str:
        """
        Validate that a given url string is a valid URL
        """

<<<<<<< HEAD:tecton_client/http_client.py
        if not url or not urlparse(url).netloc:
            raise InvalidParameterException(InvalidParameterMessage.URL.value)
=======
        # If the URL is empty or None, raise an exception
        if not url:
            raise TectonInvalidParameterException(INVALID_URL)
        # Otherwise, try parsing the URL and raise an exception if it fails
        try:
            urlparse(url)
        except Exception:
            raise TectonInvalidParameterException(INVALID_URL)
>>>>>>> feead27 (Refactoring Code):tecton_client/transport/tecton_http_client.py

        return url

    @staticmethod
    def validate_key(api_key: Optional[str]) -> str:
        if not api_key:
<<<<<<< HEAD:tecton_client/http_client.py
            raise InvalidParameterException(InvalidParameterMessage.KEY.value)
=======
            raise TectonInvalidParameterException(INVALID_KEY)
>>>>>>> feead27 (Refactoring Code):tecton_client/transport/tecton_http_client.py

        return api_key
