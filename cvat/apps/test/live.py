# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

"""
Live updates for the annotation counts page.

Any process that saves annotations (server or import worker) publishes the task id to Redis.
The WebSocket below listens on Redis and tells the page "task N changed". It never sends counts:
the page fetches them again over REST, so the task permission check stays in one place.
"""

import asyncio
import json
import re
from http.cookies import SimpleCookie
from importlib import import_module

import redis
import redis.asyncio as aioredis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user
from django.http import HttpRequest

WS_PATH = re.compile(r"^/api/test/tasks/(\d+)/annotation-counts/ws$")
HEARTBEAT_SECONDS = 25


def _channel(task_id: int) -> str:
    return f"test:annotation-counts:task:{task_id}"


def _redis_kwargs() -> dict:
    return {
        "host": settings.REDIS_INMEM_SETTINGS["HOST"],
        "port": settings.REDIS_INMEM_SETTINGS["PORT"],
        "password": settings.REDIS_INMEM_SETTINGS["PASSWORD"] or None,
    }


def publish_annotations_changed(task_id: int) -> None:
    redis.Redis(**_redis_kwargs()).publish(_channel(task_id), "changed")


def _get_user(cookie_header: str):
    cookies = SimpleCookie()
    cookies.load(cookie_header)
    session_cookie = cookies.get(settings.SESSION_COOKIE_NAME)
    request = HttpRequest()
    request.session = import_module(settings.SESSION_ENGINE).SessionStore(
        session_cookie.value if session_cookie else None
    )
    return get_user(request)


async def _serve(scope, receive, send, task_id: int):
    await receive()  # websocket.connect
    cookie_header = dict(scope["headers"]).get(b"cookie", b"").decode()
    user = await sync_to_async(_get_user)(cookie_header)
    if not user.is_authenticated:
        await send({"type": "websocket.close", "code": 4401})
        return

    await send({"type": "websocket.accept"})
    client = aioredis.Redis(**_redis_kwargs())
    pubsub = client.pubsub()
    await pubsub.subscribe(_channel(task_id))

    async def forward_changes():
        async for message in pubsub.listen():
            if message["type"] == "message":
                text = json.dumps({"type": "annotations_changed", "task_id": task_id})
                await send({"type": "websocket.send", "text": text})

    async def heartbeat():
        # keeps the connection open through nginx's idle timeout
        while True:
            await asyncio.sleep(HEARTBEAT_SECONDS)
            await send({"type": "websocket.send", "text": json.dumps({"type": "ping"})})

    tasks = [asyncio.create_task(forward_changes()), asyncio.create_task(heartbeat())]
    try:
        while (await receive())["type"] != "websocket.disconnect":
            pass
    finally:
        for task in tasks:
            task.cancel()
        await pubsub.aclose()
        await client.aclose()


def with_annotation_counts_ws(app):
    """Wraps the Django ASGI app, which only handles HTTP, to serve the counts WebSocket."""

    async def application(scope, receive, send):
        if scope["type"] != "websocket":
            return await app(scope, receive, send)

        match = WS_PATH.match(scope["path"])
        if not match:
            await send({"type": "websocket.close", "code": 4404})
            return

        await _serve(scope, receive, send, int(match[1]))

    return application
