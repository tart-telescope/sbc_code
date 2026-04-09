# middleware/client_cache_middleware.py
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class AdvancedClientCacheMiddleware(BaseHTTPMiddleware):
    """Advanced client cache middleware with path-specific configurations."""

    def __init__(
        self,
        app: FastAPI,
        default_max_age: int = 300,
        path_configs: dict[str, dict] = None
    ):
        super().__init__(app)
        self.default_max_age = default_max_age
        self.path_configs = path_configs or {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Get path-specific configuration
        cache_config = self._get_cache_config(request.url.path)

        # Set cache headers based on configuration
        if cache_config.get("no_cache", False):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        else:
            max_age = cache_config.get("max_age", self.default_max_age)
            visibility = "private" if cache_config.get("private", False) else "public"

            cache_control = f"{visibility}, max-age={max_age}"

            if cache_config.get("must_revalidate", False):
                cache_control += ", must-revalidate"

            if cache_config.get("immutable", False):
                cache_control += ", immutable"

            response.headers["Cache-Control"] = cache_control

        return response

    def _get_cache_config(self, path: str) -> dict:
        """Get cache configuration for a specific path."""
        for pattern, config in self.path_configs.items():
            print(path, pattern, config)
            if path.startswith(pattern):
                return config
        return {}

