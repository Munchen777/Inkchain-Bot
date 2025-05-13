import aiohttp
import asyncio
import orjson
import random
import ssl
import ua_generator

from better_proxy import Proxy
from typing import Any, Dict, List, Literal, Self, Tuple, Type
from yarl import URL

from core.exceptions.base import APIError, HttpStatusError, ServerError, SessionRateLimited
from core.exceptions.api_exceptions import (
    APIRateLimitError,
    APIClientSideError,
    APIServerSideError,
)
from logger import log


class BaseAPIClient:
    RETRYABLE_ERRORS: Tuple[str] = (
        ServerError, 
        SessionRateLimited,
        aiohttp.ClientError, 
        asyncio.TimeoutError,
        HttpStatusError,
    )

    def __init__(self,
                 url: str,
                 proxy: Proxy | None = None,
                 ) -> None:
        self.base_url: str = url
        self.proxy: Proxy | None = proxy
        self.session: aiohttp.ClientSession | None = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._session_active: bool = False
        self._headers: Dict[str, str | List[str] | bool] = self._generate_headers()
        self._ssl_context: ssl.SSLContext = ssl.create_default_context()
        self._connector: aiohttp.TCPConnector = self._create_connector()

    @staticmethod
    def _generate_headers() -> Dict[str, str | bool | List[str]]:
        user_agent = ua_generator.generate(
            device="desktop",
            platform=("windows", "macos", "linux"),
            browser="chrome",
        )
        return {
            'accept-language': 'en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': user_agent.ch.brands,
            'sec-ch-ua-mobile': user_agent.ch.mobile,
            'sec-ch-ua-platform': user_agent.ch.platform,
            'user-agent': user_agent.text
        }

    def _create_connector(self) -> aiohttp.TCPConnector:
        return aiohttp.TCPConnector(
            enable_cleanup_closed=True,
            ssl=self._ssl_context,
            force_close=False,
            limit=10,
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        async with self._lock:
            if not self.session or self.session.closed:
                if not self._connector or self._connector.closed:
                    self._connector = self._create_connector()

                self.session: aiohttp.ClientSession = aiohttp.ClientSession(
                    connector=self._connector,
                    headers=self._headers,
                )
            return self.session

    async def _check_session_valid(self) -> bool:
        if not self.session or self.session.closed:
            return False
        return True

    async def _reset_session_if_needed(self, skip_header_regeneration: bool = False) -> None:
        async with self._lock:
            old_session = None

            if self.session and not self.session.closed:
                old_session = self.session

            if not skip_header_regeneration:
                self._headers = self._generate_headers()

            self.session: aiohttp.ClientSession = aiohttp.ClientSession(
                connector=self._connector,
                timeout=aiohttp.ClientTimeout(total=120),
                headers=self._headers,
            )

            if old_session:
                await self._safely_close_session(old_session)

    async def _safely_close_resource(self, resource: aiohttp.ClientSession | aiohttp.TCPConnector, resource_name: str) -> None:
        if resource and hasattr(resource, "closed") and not resource.closed:
            try:
                await resource.close()
                await asyncio.sleep(0.1)
            except Exception as error:
                pass

    async def __aenter__(self) -> Self:
        if not self._session_active:
            self.session = await self._get_session()
            self._session_active = True
        return self

    async def __aexit__(
            self,
            exc_type,
            exc_value,
            exc_traceback,
        ):
        await self.close()

    async def close(self):
        try:
            if hasattr(self, "session") and self.session:
                await self._safely_close_resource(self.session, "Session")
                self.session = None

            if hasattr(self, "_connector") and self._connector:
                await self._safely_close_resource(self._connector, "Connector")
                self._connector = None

            self._session_active = False

        except Exception as error:
            self.session = None
            self._connector = None
            self._session_active = False
            raise APIError(f"Error during API client cleanup: {error}")

    async def send_request(
        self,
        request_type: Literal["POST", "GET", "PUT", "OPTIONS"] = "POST",
        method: str | None = None,
        json_data: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        url: str | None = None,
        headers: Dict[str, str] | None = None,
        cookies: Dict[str, str] | None = None,
        verify: bool = True,
        allow_redirects: bool = True,
        ssl: bool | ssl.SSLContext = True,
        max_retries: int = 3,
        retry_delay: tuple[float, float] = (1.5, 5.0),
        user_agent: str | None = None
    ) -> Dict[str, Any] | str:

        if not url and not method:
            raise ValueError("Either url or method must be provided")

        if url:
            try:
                parsed_url = URL(url)
                if parsed_url.scheme == 'https' and parsed_url.port == 80:
                    parsed_url = parsed_url.with_port(443)
                elif parsed_url.scheme == 'http' and parsed_url.port == 443:
                    parsed_url = parsed_url.with_port(80)
                target_url = str(parsed_url)
            except:
                target_url = url
        else:
            base: URL = URL(self.base_url)
            method_path: str = method.lstrip('/') if method else ''
            target_url: str = str(base / method_path)

        custom_headers: Dict[str, Any] = dict(headers) if headers else {}
        if user_agent:
            custom_headers['user-agent'] = user_agent

        ssl_param = True
        if isinstance(ssl, bool):
            ssl_param = self._ssl_context if ssl else False
        elif isinstance(ssl, ssl.SSLContext):
            ssl_param = ssl

        for attempt in range(1, max_retries + 1):
            try:
                session: aiohttp.ClientSession = await self._get_session()

                if not await self._check_session_valid():
                    session: aiohttp.ClientSession = await self._get_session()

                merged_headers: dict[str, str | bool | list[str]] = dict(session.headers)
                if custom_headers:
                    merged_headers.update(custom_headers)

                retryable_errors: tuple = self.RETRYABLE_ERRORS

                async with session.request(
                    proxy=self.proxy.as_url if self.proxy else None,
                    method=request_type,
                    url=target_url,
                    json=json_data,
                    data=data,
                    params=params,
                    headers=merged_headers,
                    cookies=cookies,
                    ssl=ssl_param,
                    allow_redirects=allow_redirects,
                    raise_for_status=False,
                ) as response:
                    content_type: str = response.headers.get("Content-Type", "").lower()
                    status_code: int = response.status

                    text: str = await response.text()
                    result: Dict[str, Any] = {
                        "status_code": status_code,
                        "url": str(response.url),
                        "text": "",
                        "data": None,
                    }
                    try:
                        if text and ('application/json' in content_type or 'json' in content_type or text.strip().startswith('{')):
                            result["data"] = orjson.loads(text)
                    except orjson.JSONDecodeError as error:
                        raise error

                    if verify:
                        if status_code == 429:
                            raise APIRateLimitError(f"Too many requests: {status_code}")
                        elif 400 <= status_code < 500:
                            raise APIClientSideError(f"Client error: {status_code}", status_code, result)
                        elif status_code >= 500:
                            raise APIServerSideError(f"Server error: {status_code}", status_code, result)

                    await self.close()
                    return result

            except retryable_errors as error:
                if isinstance(error, HttpStatusError) and getattr(error, "status_code", 0) != 429:
                    raise error

                if attempt < max_retries:
                    delay: float = random.uniform(*retry_delay) * min(2**(attempt - 1), 30)

                    if isinstance(error, (SessionRateLimited, ServerError)):
                        log.debug(f"Server or rate limit error. Retry {attempt}/{max_retries} in {delay:.2f} seconds")

                    elif isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError)):
                        log.debug(f"Network error {type(error).__name__}: {error}. Retry {attempt}/{max_retries} after {delay:.2f} seconds")

                    await asyncio.sleep(delay)
                    continue

                if isinstance(error, (ServerError, SessionRateLimited)):
                    raise error
                else:
                    raise ServerError(
                        f"The request failed after {max_retries} attempts to {target_url}. Error {error}"
                    )

            except Exception as error:
                log.error(f"Unexpected error when querying to {target_url}: {type(error).__name__}: {error}")
                if attempt < max_retries:
                    delay: float = random.uniform(*retry_delay) * min(2 ** (attempt - 1), 30)
                    await asyncio.sleep(delay)
                    continue

                raise ServerError(
                    f"The request failed after {max_retries} attempts to {target_url}"
                )

        raise ServerError(f"Unreachable code: all {max_retries} attempts have been exhausted")
