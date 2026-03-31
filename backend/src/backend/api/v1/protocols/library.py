"""Protocol library endpoints for Research Protocol Definition (feature 010).

Routes:
- GET    /protocols                → 200 list of visible protocols
- POST   /protocols                → 201 created protocol (copy or full graph)
- GET    /protocols/{protocol_id}  → 200 full protocol detail | 403 | 404
- PUT    /protocols/{protocol_id}  → 200 updated protocol | 400 | 403 | 404 | 409
- DELETE /protocols/{protocol_id}  → 204 | 403 | 409
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.protocols.schemas import (
    ProtocolCopyRequest,
    ProtocolCreateRequest,
    ProtocolDetailResponse,
    ProtocolEdgeResponse,
    ProtocolListItemResponse,
    ProtocolUpdateRequest,
)
from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services.protocol_service import (
    build_edge_responses,
    copy_protocol,
    create_protocol,
    delete_protocol,
    get_protocol_detail,
    list_protocols,
    update_protocol,
)
from backend.services.protocol_yaml import ProtocolYamlService

router = APIRouter(tags=["protocols"])


@router.get("/protocols", response_model=list[ProtocolListItemResponse])
async def get_protocols(
    study_type: str | None = Query(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProtocolListItemResponse]:
    """Return all protocols visible to the authenticated user.

    Returns default templates plus the user's own custom protocols.
    An optional ``study_type`` query parameter filters by study type.

    Args:
        study_type: Optional study type filter (``SMS``, ``SLR``, etc.).
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        List of lightweight protocol summary items.

    """
    protocols = await list_protocols(current_user.user_id, study_type, db)
    return [ProtocolListItemResponse.model_validate(p) for p in protocols]


def _protocol_to_response(protocol) -> ProtocolDetailResponse:  # type: ignore[no-untyped-def]
    """Convert a loaded :class:`~db.models.protocols.ResearchProtocol` to response schema."""
    edge_dicts = build_edge_responses(protocol)
    edges = [ProtocolEdgeResponse(**e) for e in edge_dicts]
    return ProtocolDetailResponse(
        id=protocol.id,
        name=protocol.name,
        study_type=protocol.study_type,
        is_default_template=protocol.is_default_template,
        owner_user_id=protocol.owner_user_id,
        version_id=protocol.version_id,
        description=protocol.description,
        nodes=protocol.nodes,  # type: ignore[arg-type]
        edges=edges,
        created_at=protocol.created_at,
        updated_at=protocol.updated_at,
    )


@router.post(
    "/protocols",
    response_model=ProtocolDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_copy_protocol(
    body: ProtocolCopyRequest | ProtocolCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolDetailResponse:
    """Create a new custom protocol, either by copying an existing one or from a full graph.

    Accepts either a :class:`~backend.api.v1.protocols.schemas.ProtocolCopyRequest`
    (with ``copy_from_protocol_id``) or a
    :class:`~backend.api.v1.protocols.schemas.ProtocolCreateRequest` (with full graph).

    Args:
        body: Copy or create request body.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        Full :class:`~backend.api.v1.protocols.schemas.ProtocolDetailResponse` for the new protocol.

    Raises:
        HTTP 400: If graph validation fails (cycle, dangling input, unknown task type).
        HTTP 403: If source protocol belongs to another user (copy mode).
        HTTP 409: If a protocol with the same name already exists for this user.

    """
    if isinstance(body, ProtocolCopyRequest):
        protocol = await copy_protocol(
            source_id=body.copy_from_protocol_id,
            user_id=current_user.user_id,
            new_name=body.name,
            description=body.description,
            db=db,
        )
    else:
        nodes_payload = [n.model_dump() for n in body.nodes]
        edges_payload = [e.model_dump() for e in body.edges]
        protocol = await create_protocol(
            name=body.name,
            study_type=body.study_type,
            description=body.description,
            nodes_payload=nodes_payload,
            edges_payload=edges_payload,
            user_id=current_user.user_id,
            db=db,
        )
    return _protocol_to_response(protocol)


@router.get("/protocols/{protocol_id}", response_model=ProtocolDetailResponse)
async def get_protocol(
    protocol_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolDetailResponse:
    """Return full protocol detail including nodes, edges, gates, and assignees.

    Args:
        protocol_id: Primary key of the requested protocol.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        Full :class:`~backend.api.v1.protocols.schemas.ProtocolDetailResponse`.

    Raises:
        HTTP 403: If the protocol belongs to another user.
        HTTP 404: If no protocol with *protocol_id* exists.

    """
    protocol = await get_protocol_detail(protocol_id, current_user.user_id, db)
    return _protocol_to_response(protocol)


@router.put("/protocols/{protocol_id}", response_model=ProtocolDetailResponse)
async def update_protocol_endpoint(
    protocol_id: int,
    body: ProtocolUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolDetailResponse:
    """Replace the full protocol graph (optimistic lock via version_id).

    Args:
        protocol_id: Primary key of the protocol to update.
        body: Replacement graph payload with required ``version_id``.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        Updated :class:`~backend.api.v1.protocols.schemas.ProtocolDetailResponse`.

    Raises:
        HTTP 400: If graph validation fails.
        HTTP 403: If not owner or protocol is a default template.
        HTTP 404: If protocol not found.
        HTTP 409: If ``version_id`` is stale.

    """
    nodes_payload = [n.model_dump() for n in body.nodes]
    edges_payload = [e.model_dump() for e in body.edges]
    protocol = await update_protocol(
        protocol_id=protocol_id,
        version_id=body.version_id,
        name=body.name,
        description=body.description,
        nodes_payload=nodes_payload,
        edges_payload=edges_payload,
        user_id=current_user.user_id,
        db=db,
    )
    return _protocol_to_response(protocol)


@router.delete("/protocols/{protocol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol_endpoint(
    protocol_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a custom protocol.

    Args:
        protocol_id: Primary key of the protocol to delete.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        Empty 204 response.

    Raises:
        HTTP 403: If not owner or is a default template.
        HTTP 409: If protocol is assigned to one or more studies.

    """
    await delete_protocol(protocol_id, current_user.user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/protocols/{protocol_id}/export")
async def export_protocol_yaml(
    protocol_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export a protocol as a YAML file download.

    Args:
        protocol_id: Primary key of the protocol to export.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        YAML file as ``application/x-yaml`` streaming response.

    Raises:
        HTTP 403: If the protocol belongs to another user.
        HTTP 404: If no protocol with *protocol_id* exists.

    """
    protocol = await get_protocol_detail(protocol_id, current_user.user_id, db)
    yaml_str = await ProtocolYamlService().export(protocol)
    safe_name = protocol.name.replace(" ", "_")
    return StreamingResponse(
        iter([yaml_str]),
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f'attachment; filename="protocol-{safe_name}.yaml"',
        },
    )


@router.post(
    "/protocols/import",
    response_model=ProtocolDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_protocol_yaml(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolDetailResponse:
    """Import a protocol from an uploaded YAML file.

    Creates a new custom protocol owned by the authenticated researcher.
    Validates the graph before persisting.

    Args:
        file: Multipart YAML file upload.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        Full :class:`~backend.api.v1.protocols.schemas.ProtocolDetailResponse` for the new protocol.

    Raises:
        HTTP 400: On YAML parse error, unsupported schema version, cycle, or dangling input.

    """
    raw_bytes = await file.read()
    try:
        yaml_str = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded.",
        ) from exc

    protocol = await ProtocolYamlService().import_yaml(yaml_str, current_user.user_id, db)
    return _protocol_to_response(protocol)
