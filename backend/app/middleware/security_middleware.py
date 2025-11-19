"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Security middleware for adding security headers and request tracking.
"""

import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to responses.
    
    Adds various security headers (CSP, CORS, etc.) to improve security posture.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        content_security_policy: str | None = None,
        include_default_csp: bool = True,
        x_frame_options: str = "DENY",
        x_content_type_options: str = "nosniff",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str | None = None,
        include_default_permissions_policy: bool = True,
        strict_transport_security: str = "max-age=31536000; includeSubDomains",
        cross_origin_opener_policy: str = "same-origin",
        cross_origin_embedder_policy: str = "require-corp",
        cross_origin_resource_policy: str = "same-origin",
    ):
        """
        Initialize the security headers middleware.
        
        Args:
            app: The ASGI application
            content_security_policy: Custom CSP header value
            include_default_csp: Whether to use default CSP directives
            x_frame_options: X-Frame-Options header value
            x_content_type_options: X-Content-Type-Options header value
            referrer_policy: Referrer-Policy header value
            permissions_policy: Custom Permissions-Policy header value
            include_default_permissions_policy: Whether to use default permissions policy
            strict_transport_security: HSTS header value
            cross_origin_opener_policy: COOP header value
            cross_origin_embedder_policy: COEP header value
            cross_origin_resource_policy: CORP header value
        """
        super().__init__(app)
        
        # Set default CSP if not provided
        if content_security_policy is None and include_default_csp:
            self.content_security_policy = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests; "
                "block-all-mixed-content"
            )
        else:
            self.content_security_policy = content_security_policy
        
        # Set default permissions policy if not provided
        if permissions_policy is None and include_default_permissions_policy:
            self.permissions_policy = (
                "accelerometer=(), "
                "ambient-light-sensor=(), "
                "autoplay=(), "
                "battery=(), "
                "camera=(), "
                "display-capture=(), "
                "document-domain=(), "
                "encrypted-media=(), "
                "fullscreen=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "midi=(), "
                "payment=(), "
                "picture-in-picture=(), "
                "usb=(), "
                "web-share=()"
            )
        else:
            self.permissions_policy = permissions_policy
        
        # Store other security headers
        self.x_frame_options = x_frame_options
        self.x_content_type_options = x_content_type_options
        self.referrer_policy = referrer_policy
        self.strict_transport_security = strict_transport_security
        self.cross_origin_opener_policy = cross_origin_opener_policy
        self.cross_origin_embedder_policy = cross_origin_embedder_policy
        self.cross_origin_resource_policy = cross_origin_resource_policy
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.
        
        Args:
            request: The HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            Response with security headers
        """
        response = await call_next(request)
        
        # Add security headers
        if self.content_security_policy:
            response.headers["Content-Security-Policy"] = self.content_security_policy
        
        if self.x_frame_options:
            response.headers["X-Frame-Options"] = self.x_frame_options
        
        if self.x_content_type_options:
            response.headers["X-Content-Type-Options"] = self.x_content_type_options
        
        if self.referrer_policy:
            response.headers["Referrer-Policy"] = self.referrer_policy
        
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy
        
        # Only add HSTS for HTTPS requests
        if self.strict_transport_security and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = self.strict_transport_security
        
        if self.cross_origin_opener_policy:
            response.headers["Cross-Origin-Opener-Policy"] = self.cross_origin_opener_policy
        
        if self.cross_origin_embedder_policy:
            response.headers["Cross-Origin-Embedder-Policy"] = self.cross_origin_embedder_policy
        
        if self.cross_origin_resource_policy:
            response.headers["Cross-Origin-Resource-Policy"] = self.cross_origin_resource_policy
        
        # Add cache control for non-static resources
        if not request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding unique request IDs to requests and responses.
    
    Generates a unique ID for each request for traceability and debugging.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
        include_in_response: bool = True,
    ):
        """
        Initialize the request ID middleware.
        
        Args:
            app: The ASGI application
            header_name: Header name for the request ID
            include_in_response: Whether to include request ID in response
        """
        super().__init__(app)
        self.header_name = header_name
        self.include_in_response = include_in_response
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add request ID.
        
        Args:
            request: The HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            Response with request ID header
        """
        # Use existing request ID or generate new one
        request_id = request.headers.get(self.header_name, str(uuid.uuid4()))
        
        # Store request ID in request state for logging
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        if self.include_in_response:
            response.headers[self.header_name] = request_id
        
        return response


def add_security_middleware(app: FastAPI) -> None:
    """
    Add all security middleware to the FastAPI application.
    
    Args:
        app: The FastAPI application
    """
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)
