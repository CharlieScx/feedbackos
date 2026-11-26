"""创建第二周导入基础表

Revision ID: 0001_import_foundation
Revises:
Create Date: 2026-11-26 15:43:22.481050
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_import_foundation"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("email = lower(trim(email))", name=op.f("ck_users_normalized_email")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "workspaces",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspaces")),
    )
    op.create_table(
        "members",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner", "member", name="member_role", native_enum=False, create_constraint=True
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_members_user_id_users")),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name=op.f("fk_members_workspace_id_workspaces")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_members")),
        sa.UniqueConstraint("workspace_id", "user_id", name=op.f("uq_members_workspace_id")),
    )
    op.create_index(op.f("ix_members_user_id"), "members", ["user_id"], unique=False)
    op.create_index(op.f("ix_members_workspace_id"), "members", ["workspace_id"], unique=False)
    op.create_table(
        "projects",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name=op.f("fk_projects_workspace_id_workspaces")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("workspace_id", "id", name=op.f("uq_projects_workspace_id")),
    )
    op.create_index(op.f("ix_projects_workspace_id"), "projects", ["workspace_id"], unique=False)
    op.create_table(
        "sessions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("expires_at > created_at", name=op.f("ck_sessions_positive_lifetime")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_sessions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)
    op.create_table(
        "data_sources",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "file_upload", name="data_source_kind", native_enum=False, create_constraint=True
            ),
            nullable=False,
        ),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name=op.f("fk_data_sources_workspace_id_projects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_sources")),
        sa.UniqueConstraint(
            "workspace_id", "project_id", "id", name=op.f("uq_data_sources_workspace_id")
        ),
    )
    op.create_table(
        "stored_files",
        sa.Column("uploaded_by_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("object_key", sa.String(length=1024), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("media_type", sa.String(length=255), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("byte_size >= 0", name=op.f("ck_stored_files_nonnegative_byte_size")),
        sa.ForeignKeyConstraint(
            ["uploaded_by_id"], ["users.id"], name=op.f("fk_stored_files_uploaded_by_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name=op.f("fk_stored_files_workspace_id_projects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stored_files")),
        sa.UniqueConstraint("object_key", name=op.f("uq_stored_files_object_key")),
        sa.UniqueConstraint(
            "workspace_id", "project_id", "id", name=op.f("uq_stored_files_workspace_id")
        ),
    )
    op.create_table(
        "import_batches",
        sa.Column("data_source_id", sa.Uuid(), nullable=False),
        sa.Column("stored_file_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "uploaded",
                "preview_ready",
                "mapping_confirmed",
                "failed",
                name="import_batch_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("row_count", sa.BigInteger(), nullable=True),
        sa.Column("preview_metadata", sa.JSON(), nullable=True),
        sa.Column("field_mapping", sa.JSON(), nullable=True),
        sa.Column("mapping_version", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("retryable", sa.Boolean(), nullable=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status != 'failed' OR (error_code IS NOT NULL AND retryable IS NOT NULL)",
            name=op.f("ck_import_batches_failed_has_error"),
        ),
        sa.CheckConstraint(
            "mapping_version >= 0", name=op.f("ck_import_batches_nonnegative_mapping_version")
        ),
        sa.CheckConstraint(
            "row_count IS NULL OR row_count >= 0",
            name=op.f("ck_import_batches_nonnegative_row_count"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"], ["users.id"], name=op.f("fk_import_batches_created_by_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id", "data_source_id"],
            ["data_sources.workspace_id", "data_sources.project_id", "data_sources.id"],
            name=op.f("fk_import_batches_workspace_id_data_sources"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id", "stored_file_id"],
            ["stored_files.workspace_id", "stored_files.project_id", "stored_files.id"],
            name=op.f("fk_import_batches_workspace_id_stored_files"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name=op.f("fk_import_batches_workspace_id_projects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_import_batches")),
        sa.UniqueConstraint(
            "created_by_id",
            "project_id",
            "idempotency_key",
            name=op.f("uq_import_batches_created_by_id"),
        ),
        sa.UniqueConstraint("stored_file_id", name=op.f("uq_import_batches_stored_file_id")),
        sa.UniqueConstraint(
            "workspace_id", "project_id", "id", name=op.f("uq_import_batches_workspace_id")
        ),
    )
    op.create_table(
        "feedback_items",
        sa.Column("import_batch_id", sa.Uuid(), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("product_version", sa.String(length=200), nullable=True),
        sa.Column("channel", sa.String(length=200), nullable=True),
        sa.Column("customer_ref", sa.String(length=255), nullable=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source_row_number > 0", name=op.f("ck_feedback_items_positive_source_row")
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id", "import_batch_id"],
            ["import_batches.workspace_id", "import_batches.project_id", "import_batches.id"],
            name=op.f("fk_feedback_items_workspace_id_import_batches"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name=op.f("fk_feedback_items_workspace_id_projects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedback_items")),
        sa.UniqueConstraint(
            "import_batch_id", "source_row_number", name=op.f("uq_feedback_items_import_batch_id")
        ),
        sa.UniqueConstraint(
            "workspace_id", "project_id", "id", name=op.f("uq_feedback_items_workspace_id")
        ),
    )


def downgrade() -> None:
    op.drop_table("feedback_items")
    op.drop_table("import_batches")
    op.drop_table("stored_files")
    op.drop_table("data_sources")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(op.f("ix_projects_workspace_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_members_workspace_id"), table_name="members")
    op.drop_index(op.f("ix_members_user_id"), table_name="members")
    op.drop_table("members")
    op.drop_table("workspaces")
    op.drop_table("users")
