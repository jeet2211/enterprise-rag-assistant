from __future__ import annotations

from fastapi import Request


def get_settings(request: Request):
    return request.app.state.settings


def get_document_service(request: Request):
    return request.app.state.document_service


def get_pipeline(request: Request):
    return request.app.state.pipeline


def get_chat_service(request: Request):
    return request.app.state.chat_service

