"""
Security middleware for FastAPI application.

Provides:
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- CORS configuration for frontend origin
- Simple in-memory rate limiting per IP address (disabilitabile via config)
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from src.shared.infra.config import get_settings


class SecurityHeadersMiddleware:
    """Middleware che aggiunge security header base alle risposte."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                # Add security headers
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"x-xss-protection", b"1; mode=block"))
                headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


class RateLimitMiddleware:
    """Middleware per rate limiting semplice in memoria per IP address.
    
    Disabilitabile via configurazione per ambienti di sviluppo locale.
    """

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        # Dict[ip_address] = [timestamp1, timestamp2, ...]
        self.ip_requests: dict[str, list[float]] = defaultdict(list)
        self.settings = get_settings()

    def _get_client_ip(self, request: Request) -> str:
        """Estrae il client IP dallo header X-Forwarded-For o dalla connessione."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For può contenere più IP, prendi il primo
            return forwarded_for.split(",")[0].strip()
        
        # Fallback a client diretto
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Verifica se il client ha superato il rate limit."""
        if not self.requests_per_minute:
            return False
        
        now = time.time()
        one_minute_ago = now - 60
        
        # Pulisci le richieste più vecchie di 1 minuto
        self.ip_requests[client_ip] = [
            req_time for req_time in self.ip_requests[client_ip]
            if req_time > one_minute_ago
        ]
        
        # Controlla se abbiamo superato il limite
        if len(self.ip_requests[client_ip]) >= self.requests_per_minute:
            return True
        
        # Aggiungi la nuova richiesta
        self.ip_requests[client_ip].append(now)
        return False

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Skip rate limiting se disabilitato
        if not self.settings.ENABLE_RATE_LIMIT:
            await self.app(scope, receive, send)
            return

        # Crea una request-like object per ottenere l'IP
        # (Non è una vera Request di FastAPI, ma abbiamo i dati necessari)
        request = Request(scope)
        client_ip = self._get_client_ip(request)

        if self._is_rate_limited(client_ip):
            async def send_rate_limit_error(message):
                if message["type"] == "http.response.start":
                    message["status"] = 429  # Too Many Requests
                    message["headers"] = [
                        (b"content-type", b"application/json"),
                        (b"retry-after", b"60"),
                    ]
                await send(message)

            await send_rate_limit_error(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({
                "type": "http.response.body",
                "body": b'{"detail":"Rate limit exceeded. Max 60 requests per minute."}',
                "more_body": False,
            })
            return

        await self.app(scope, receive, send)


def setup_security_middleware(app: FastAPI) -> None:
    """Setup security middleware per l'applicazione FastAPI.
    
    Aggiunge in ordine:
    1. SecurityHeadersMiddleware - Aggiunge security headers
    2. CORS middleware - Configura CORS per il frontend
    3. RateLimitMiddleware - Rate limiting per IP (opzionale)
    
    Args:
        app: FastAPI application instance
    """
    settings = get_settings()

    # 1. Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Local development
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
        + (settings.CORS_ORIGINS if settings.CORS_ORIGINS else []),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Rate limit middleware (opzionale, disabilitabile)
    if settings.ENABLE_RATE_LIMIT:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        )
