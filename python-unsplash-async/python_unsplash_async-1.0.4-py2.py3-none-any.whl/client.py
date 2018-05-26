import aiohttp

from unsplash.errors import (
    UnsplashError,
    UnsplashRateLimitError,
    UnsplashConnectionError,
)


class Client(object):
    """
    Unsplash Client

    HTTP connections to and communication with the Unsplash API.
    """

    def __init__(self, api, **kwargs):
        self.api = api
        self.rate_limit_error = "Rate Limit Exceeded"

    async def _request(self, url, method, params=None, data=None, **kwargs):
        if not url.startswith("http"):
            url = "%s%s" % (self.api.base_url, url)
        headers = self.get_auth_header()
        headers.update(self.get_version_header())
        headers.update(kwargs.pop("headers", {}))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, params=params, data=data, headers=headers, **kwargs
                ) as response:
                    if not self._is_2xx(response.status):
                        text = await response.text()
                        if text == self.rate_limit_error:
                            raise UnsplashRateLimitError(self.rate_limit_error)
                        else:
                            json = await response.json()
                            errors = json.get("errors")
                            raise UnsplashError(
                                " ".join(str(e) for e in errors)
                                if errors
                                else "Unknown error"
                            )
                    if response.headers.get("Content-Type") == "application/json":
                        result = await response.json()
                    else:
                        result = await response.read()
        except ValueError as e:
            result = None
        except (UnsplashRateLimitError, UnsplashError) as e:
            raise e
        except Exception as e:
            raise UnsplashConnectionError(*e.args)

        return result

    async def _get(self, url, params=None, **kwargs):
        return await self._request(url, "get", params=params, **kwargs)

    async def _post(self, url, data=None, **kwargs):
        return await self._request(url, "post", data=data, **kwargs)

    async def _delete(self, url, **kwargs):
        return await self._request(url, "delete", **kwargs)

    async def _put(self, url, data=None, **kwargs):
        return await self._request(url, "put", data=data, **kwargs)

    def get_auth_header(self):
        """
        Getting the authorization header according to the authentication procedure

        :return [dict]: Authorization header
        """
        if self.api.is_authenticated:
            return {"Authorization": "Bearer %s" % self.api.access_token}
        return {"Authorization": "Client-ID %s" % self.api.client_id}

    def get_version_header(self):
        """
        Getting Version header

        :return [dict]: Accept-Version header
        """
        return {"Accept-Version": self.api.api_version}

    @staticmethod
    def _is_1xx(status_code):
        return 100 <= status_code <= 199

    @staticmethod
    def _is_2xx(status_code):
        return 200 <= status_code <= 299

    @staticmethod
    def _is_3xx(status_code):
        return 300 <= status_code <= 399

    @staticmethod
    def _is_4xx(status_code):
        return 400 <= status_code <= 499

    @staticmethod
    def _is_5xx(status_code):
        return 500 <= status_code <= 599
