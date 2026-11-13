from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Identity:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ProjectScope:
    workspace_id: Mapped[UUID] = mapped_column(nullable=False)
    project_id: Mapped[UUID] = mapped_column(nullable=False)


def project_scope_constraints() -> tuple[ForeignKeyConstraint, UniqueConstraint]:
    return (
        ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
        ),
        UniqueConstraint("workspace_id", "project_id", "id"),
    )


class MemberRole(StrEnum):
    OWNER = "owner"
    MEMBER = "member"


class DataSourceKind(StrEnum):
    FILE_UPLOAD = "file_upload"


class ImportBatchStatus(StrEnum):
    UPLOADED = "uploaded"
    PREVIEW_READY = "preview_ready"
    MAPPING_CONFIRMED = "mapping_confirmed"
    FAILED = "failed"


def enum_type[T: StrEnum](enum: type[T], name: str) -> Enum:
    return Enum(
        enum,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [item.value for item in members],
    )


class User(Identity, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("email = lower(trim(email))", name="normalized_email"),)

    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)


class Session(Identity, Base):
    __tablename__ = "sessions"
    __table_args__ = (CheckConstraint("expires_at > created_at", name="positive_lifetime"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Workspace(Identity, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(200))


class Member(Identity, Base):
    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id"),)

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[MemberRole] = mapped_column(enum_type(MemberRole, "member_role"))


class Project(Identity, Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("workspace_id", "id"),)

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))


class DataSource(ProjectScope, Identity, Base):
    __tablename__ = "data_sources"
    __table_args__ = project_scope_constraints()

    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[DataSourceKind] = mapped_column(
        enum_type(DataSourceKind, "data_source_kind"),
        default=DataSourceKind.FILE_UPLOAD,
    )


class StoredFile(ProjectScope, Identity, Base):
    __tablename__ = "stored_files"
    __table_args__ = (
        *project_scope_constraints(),
        CheckConstraint("byte_size >= 0", name="nonnegative_byte_size"),
    )

    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    original_filename: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(String(1024), unique=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    media_type: Mapped[str] = mapped_column(String(255))
    byte_size: Mapped[int] = mapped_column(BigInteger)


class ImportBatch(ProjectScope, Identity, Base):
    __tablename__ = "import_batches"
    __table_args__ = (
        *project_scope_constraints(),
        ForeignKeyConstraint(
            ["workspace_id", "project_id", "data_source_id"],
            ["data_sources.workspace_id", "data_sources.project_id", "data_sources.id"],
        ),
        ForeignKeyConstraint(
            ["workspace_id", "project_id", "stored_file_id"],
            ["stored_files.workspace_id", "stored_files.project_id", "stored_files.id"],
        ),
        UniqueConstraint("created_by_id", "project_id", "idempotency_key"),
        UniqueConstraint("stored_file_id"),
        CheckConstraint("row_count IS NULL OR row_count >= 0", name="nonnegative_row_count"),
        CheckConstraint("mapping_version >= 0", name="nonnegative_mapping_version"),
        CheckConstraint(
            "status != 'failed' OR (error_code IS NOT NULL AND retryable IS NOT NULL)",
            name="failed_has_error",
        ),
    )

    data_source_id: Mapped[UUID] = mapped_column(nullable=False)
    stored_file_id: Mapped[UUID] = mapped_column(nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    status: Mapped[ImportBatchStatus] = mapped_column(
        enum_type(ImportBatchStatus, "import_batch_status"),
        default=ImportBatchStatus.UPLOADED,
    )
    row_count: Mapped[int | None] = mapped_column(BigInteger)
    preview_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    field_mapping: Mapped[dict[str, str] | None] = mapped_column(JSON)
    mapping_version: Mapped[int] = mapped_column(default=0)
    error_code: Mapped[str | None] = mapped_column(String(100))
    retryable: Mapped[bool | None]


class FeedbackItem(ProjectScope, Identity, Base):
    __tablename__ = "feedback_items"
    __table_args__ = (
        *project_scope_constraints(),
        ForeignKeyConstraint(
            ["workspace_id", "project_id", "import_batch_id"],
            ["import_batches.workspace_id", "import_batches.project_id", "import_batches.id"],
        ),
        UniqueConstraint("import_batch_id", "source_row_number"),
        CheckConstraint("source_row_number > 0", name="positive_source_row"),
    )

    import_batch_id: Mapped[UUID] = mapped_column(nullable=False)
    source_row_number: Mapped[int]
    feedback_text: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    product_version: Mapped[str | None] = mapped_column(String(200))
    channel: Mapped[str | None] = mapped_column(String(200))
    customer_ref: Mapped[str | None] = mapped_column(String(255))
