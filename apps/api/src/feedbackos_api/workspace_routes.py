from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field, StringConstraints
from sqlalchemy import Row, Select, func, select
from sqlalchemy.orm import Session as DBSession

from feedbackos_api.auth import UserIdentity
from feedbackos_api.auth_routes import require_current_user, require_trusted_origin
from feedbackos_api.contracts import ErrorCode, PaginatedResponse, PaginationMeta, SuccessResponse
from feedbackos_api.database import Database, get_database
from feedbackos_api.errors import ApiException, PrivateRoute
from feedbackos_api.models import Member, MemberRole, Project, Workspace

router = APIRouter(prefix="/workspaces", tags=["workspaces"], route_class=PrivateRoute)
Actor = Annotated[UserIdentity, Depends(require_current_user)]
Store = Annotated[Database, Depends(get_database)]


class CreateResource(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=1, max_length=200, pattern=r"^[^\x00]+$"
        ),
    ]


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class WorkspaceData(BaseModel):
    id: UUID
    name: str
    role: MemberRole


class WorkspaceResponse(SuccessResponse[WorkspaceData]):
    pass


class WorkspaceListResponse(PaginatedResponse[WorkspaceData]):
    pass


class ProjectData(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str


class ProjectResponse(SuccessResponse[ProjectData]):
    pass


class ProjectListResponse(PaginatedResponse[ProjectData]):
    pass


def _page[T: tuple[object, ...]](
    session: DBSession, query: Select[T], params: PageParams
) -> tuple[list[Row[T]], PaginationMeta]:
    total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    pagination = PaginationMeta.from_total(
        page=params.page, page_size=params.page_size, total=total
    )
    offset = (params.page - 1) * params.page_size
    if offset >= total:
        return [], pagination
    rows = session.execute(query.offset(offset).limit(params.page_size)).all()
    return list(rows), pagination


def _member_workspaces(user_id: UUID) -> Select[tuple[Workspace, MemberRole]]:
    return (
        select(Workspace, Member.role)
        .select_from(Member)
        .join(Workspace, Workspace.id == Member.workspace_id)
        .where(Member.user_id == user_id)
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_trusted_origin)],
)
def create_workspace(body: CreateResource, actor: Actor, database: Store) -> WorkspaceResponse:
    with database.transaction() as session:
        workspace = Workspace(name=body.name)
        session.add(workspace)
        session.flush()
        session.add(Member(workspace_id=workspace.id, user_id=actor.id, role=MemberRole.OWNER))
        return WorkspaceResponse(
            data=WorkspaceData(id=workspace.id, name=workspace.name, role=MemberRole.OWNER)
        )


@router.get("")
def list_workspaces(
    actor: Actor, database: Store, params: Annotated[PageParams, Query()]
) -> WorkspaceListResponse:
    with database.transaction() as session:
        query = _member_workspaces(actor.id).order_by(Workspace.created_at, Workspace.id)
        rows, pagination = _page(session, query, params)
        return WorkspaceListResponse(
            data=[
                WorkspaceData(id=workspace.id, name=workspace.name, role=role)
                for workspace, role in rows
            ],
            pagination=pagination,
        )


@router.get("/{workspace_id}")
def get_workspace(workspace_id: UUID, actor: Actor, database: Store) -> WorkspaceResponse:
    with database.transaction() as session:
        row = session.execute(
            _member_workspaces(actor.id).where(Member.workspace_id == workspace_id)
        ).one_or_none()
        if row is None:
            raise ApiException(ErrorCode.RESOURCE_NOT_FOUND)
        workspace, role = row
        return WorkspaceResponse(
            data=WorkspaceData(id=workspace.id, name=workspace.name, role=role)
        )


def _require_workspace_membership(session: DBSession, user_id: UUID, workspace_id: UUID) -> None:
    # Keep membership in place through the project query/write in this transaction.
    membership = session.scalar(
        select(Member.id)
        .where(Member.user_id == user_id, Member.workspace_id == workspace_id)
        .with_for_update(read=True)
    )
    if membership is None:
        raise ApiException(ErrorCode.RESOURCE_NOT_FOUND)


def _project_data(project: Project) -> ProjectData:
    return ProjectData(id=project.id, workspace_id=project.workspace_id, name=project.name)


@router.post(
    "/{workspace_id}/projects",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_trusted_origin)],
    tags=["projects"],
)
def create_project(
    workspace_id: UUID, body: CreateResource, actor: Actor, database: Store
) -> ProjectResponse:
    with database.transaction() as session:
        _require_workspace_membership(session, actor.id, workspace_id)
        project = Project(workspace_id=workspace_id, name=body.name)
        session.add(project)
        session.flush()
        return ProjectResponse(data=_project_data(project))


@router.get("/{workspace_id}/projects", tags=["projects"])
def list_projects(
    workspace_id: UUID, actor: Actor, database: Store, params: Annotated[PageParams, Query()]
) -> ProjectListResponse:
    with database.transaction() as session:
        _require_workspace_membership(session, actor.id, workspace_id)
        query = (
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .order_by(Project.created_at, Project.id)
        )
        rows, pagination = _page(session, query, params)
        return ProjectListResponse(
            data=[_project_data(project) for (project,) in rows], pagination=pagination
        )


@router.get("/{workspace_id}/projects/{project_id}", tags=["projects"])
def get_project(
    workspace_id: UUID, project_id: UUID, actor: Actor, database: Store
) -> ProjectResponse:
    with database.transaction() as session:
        project = session.scalar(
            select(Project)
            .select_from(Member)
            .join(Project, Project.workspace_id == Member.workspace_id)
            .where(
                Member.user_id == actor.id,
                Member.workspace_id == workspace_id,
                Project.id == project_id,
            )
        )
        if project is None:
            raise ApiException(ErrorCode.RESOURCE_NOT_FOUND)
        return ProjectResponse(data=_project_data(project))
