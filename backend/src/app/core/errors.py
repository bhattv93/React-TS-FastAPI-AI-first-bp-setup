"""Domain exceptions and the single error envelope returned by the API.

Envelope::

    {"error": {"code": "...", "message": "...", "details": ..., "request_id": "..."}}

Unexpected exceptions are converted to the same envelope by ``RequestIdMiddleware``.
"""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import current_request_id


class AppError(Exception):
    """Base class for errors that map to an HTTP response.

    Parameters
    ----------
    message : str
        Human-readable description.
    details : Any, optional
        Extra machine-readable context.
    """

    status_code = 400
    code = "app_error"

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    """Raised when a request conflicts with the current state."""

    status_code = 409
    code = "conflict"


class DomainValidationError(AppError):
    """Raised when business rules reject otherwise well-formed input."""

    status_code = 422
    code = "validation_error"


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build a response in the standard error envelope.

    Parameters
    ----------
    status_code : int
        HTTP status code.
    code : str
        Stable machine-readable error code.
    message : str
        Human-readable description.
    details : Any, optional
        Extra machine-readable context.
    headers : Mapping[str, str], optional
        Extra response headers, such as ``WWW-Authenticate`` or ``Retry-After``.

    Returns
    -------
    JSONResponse
        The enveloped response.
    """
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": current_request_id(),
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers that map exceptions to the error envelope.

    Parameters
    ----------
    app : FastAPI
        The application to configure.
    """

    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError) -> JSONResponse:
        """Handle domain errors.

        Parameters
        ----------
        _request : Request
            The failing request (unused).
        exc : AppError
            The raised domain error.

        Returns
        -------
        JSONResponse
            The enveloped response.
        """
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation failures.

        Parameters
        ----------
        _request : Request
            The failing request (unused).
        exc : RequestValidationError
            The validation error raised by FastAPI.

        Returns
        -------
        JSONResponse
            A 422 response listing the invalid fields.
        """
        # ``input`` echoes the submitted value (possibly a password), so it is dropped;
        # ``ctx`` can hold exception objects that JSON cannot encode, hence the encoder.
        details = [
            {key: value for key, value in error.items() if key != "input"}
            for error in exc.errors()
        ]
        return error_response(
            422,
            "request_validation_error",
            "Request validation failed",
            jsonable_encoder(details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle framework HTTP errors such as 404 for unknown routes.

        Parameters
        ----------
        _request : Request
            The failing request (unused).
        exc : StarletteHTTPException
            The HTTP exception.

        Returns
        -------
        JSONResponse
            The enveloped response.
        """
        return error_response(
            exc.status_code, "http_error", str(exc.detail), headers=exc.headers
        )
