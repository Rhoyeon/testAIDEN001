"""Aggregated API v1 router."""

from fastapi import APIRouter

from app.api.v1 import projects, documents, phases, deliverables, agents, hitl, websocket

api_v1_router = APIRouter()

api_v1_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_v1_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_v1_router.include_router(phases.router, prefix="/phases", tags=["Phases"])
api_v1_router.include_router(deliverables.router, prefix="/deliverables", tags=["Deliverables"])
api_v1_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_v1_router.include_router(hitl.router, prefix="/reviews", tags=["HITL Reviews"])
api_v1_router.include_router(websocket.router, tags=["WebSocket"])
