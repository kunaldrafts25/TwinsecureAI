"""Fix partitioned table PK

Revision ID: 1c01dbd33ee8
Revises: 0c01dbd33ee7
Create Date: 2025-05-14 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1c01dbd33ee8'
down_revision: Union[str, None] = '0c01dbd33ee7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Fix for the partitioned table primary key issue ###

    # Drop all tables in reverse order to avoid foreign key constraints
    op.drop_table('alert_notes')
    op.drop_table('reports')
    op.drop_table('report_templates')
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('alerts')
    op.drop_table('users')

    # Recreate the users table with the correct primary key that includes the partitioning column
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING', name='userstatus'), nullable=False),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('last_login_attempt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=True),
        sa.Column('mfa_secret', sa.String(), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        # Include role in the primary key constraint
        sa.PrimaryKeyConstraint('id', 'role', name=op.f('pk_users')),
        # Self-referential foreign keys need to be added after the table is created
        postgresql_partition_by='LIST (role)'
    )

    # Add self-referential foreign keys after table creation
    # For partitioned tables with composite primary keys, we need to add the role column
    # But since we don't have a created_by_role column, we'll skip these foreign keys for now
    # op.create_foreign_key(op.f('fk_users_created_by_users'), 'users', 'users', ['created_by'], ['id'])
    # op.create_foreign_key(op.f('fk_users_updated_by_users'), 'users', 'users', ['updated_by'], ['id'])

    # For partitioned tables, unique indexes must include all partitioning columns
    op.create_index(op.f('ix_users_email_role'), 'users', ['email', 'role'], unique=True)
    op.create_index(op.f('ix_users_full_name'), 'users', ['full_name'], unique=False)

    # Recreate the alerts table
    op.create_table('alerts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('alert_type', sa.Enum('HONEYPOT_TRIGGER', 'ANOMALY_DETECTED', 'BRUTE_FORCE', 'SUSPICIOUS_IP', 'MALWARE_DETECTED', 'DATA_EXFILTRATION', 'UNAUTHORIZED_ACCESS', 'CONFIGURATION_CHANGE', 'SYSTEM_ALERT', 'CUSTOM', name='alerttype'), nullable=False),
        sa.Column('source', sa.Enum('HONEYPOT', 'IDS', 'WAF', 'SIEM', 'ML_MODEL', 'MANUAL', 'EXTERNAL', name='alertsource'), nullable=False),
        sa.Column('severity', sa.Enum('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alertseverity'), nullable=True),
        sa.Column('status', sa.Enum('NEW', 'ACKNOWLEDGED', 'INVESTIGATING', 'ESCALATED', 'RESOLVED', 'FALSE_POSITIVE', 'IGNORED', name='alertstatus'), nullable=True),
        sa.Column('source_ip', postgresql.INET(), nullable=True),
        sa.Column('source_hostname', sa.String(), nullable=True),
        sa.Column('source_mac', sa.String(), nullable=True),
        sa.Column('source_ports', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('source_protocol', sa.String(), nullable=True),
        sa.Column('target_ip', postgresql.INET(), nullable=True),
        sa.Column('target_hostname', sa.String(), nullable=True),
        sa.Column('target_port', sa.Integer(), nullable=True),
        sa.Column('target_protocol', sa.String(), nullable=True),
        sa.Column('target_service', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('raw_log', sa.Text(), nullable=True),
        sa.Column('enrichment_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('threat_intel', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('malware_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('abuse_score', sa.Integer(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('false_positive_probability', sa.Float(), nullable=True),
        sa.Column('assigned_to_id', sa.UUID(), nullable=True),
        sa.Column('acknowledged_by_id', sa.UUID(), nullable=True),
        sa.Column('resolved_by_id', sa.UUID(), nullable=True),
        sa.Column('related_alerts', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        # We need to add role columns for these foreign keys to work with the partitioned users table
        sa.Column('assigned_to_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=True),
        sa.Column('acknowledged_by_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=True),
        sa.Column('resolved_by_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=True),
        sa.ForeignKeyConstraint(['acknowledged_by_id', 'acknowledged_by_role'], ['users.id', 'users.role'], name=op.f('fk_alerts_acknowledged_by_id_users')),
        sa.ForeignKeyConstraint(['assigned_to_id', 'assigned_to_role'], ['users.id', 'users.role'], name=op.f('fk_alerts_assigned_to_id_users')),
        sa.ForeignKeyConstraint(['resolved_by_id', 'resolved_by_role'], ['users.id', 'users.role'], name=op.f('fk_alerts_resolved_by_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_alerts'))
    )

    # Recreate indexes for alerts
    op.create_index(op.f('ix_alerts_abuse_score'), 'alerts', ['abuse_score'], unique=False)
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)
    op.create_index('ix_alerts_enrichment_gin', 'alerts', ['enrichment_data'], unique=False, postgresql_using='gin')
    op.create_index('ix_alerts_payload_gin', 'alerts', ['payload'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_alerts_risk_score'), 'alerts', ['risk_score'], unique=False)
    op.create_index(op.f('ix_alerts_severity'), 'alerts', ['severity'], unique=False)
    op.create_index(op.f('ix_alerts_source_ip'), 'alerts', ['source_ip'], unique=False)
    op.create_index('ix_alerts_source_ip_triggered_at', 'alerts', ['source_ip', 'triggered_at'], unique=False)
    op.create_index(op.f('ix_alerts_status'), 'alerts', ['status'], unique=False)
    op.create_index('ix_alerts_status_created_at', 'alerts', ['status', 'created_at'], unique=False)
    op.create_index(op.f('ix_alerts_target_ip'), 'alerts', ['target_ip'], unique=False)
    op.create_index(op.f('ix_alerts_triggered_at'), 'alerts', ['triggered_at'], unique=False)
    op.create_index('ix_alerts_triggered_at_severity', 'alerts', ['triggered_at', 'severity'], unique=False)
    op.create_index('ix_alerts_type_severity', 'alerts', ['alert_type', 'severity'], unique=False)

    # Recreate the api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('user_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id', 'user_role'], ['users.id', 'users.role'], name=op.f('fk_api_keys_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_api_keys')),
        sa.UniqueConstraint('key', name=op.f('uq_api_keys_key'))
    )

    # Recreate the audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('user_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.UUID(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id', 'user_role'], ['users.id', 'users.role'], name=op.f('fk_audit_logs_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )

    # Recreate the report_templates table
    op.create_table('report_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.Enum('DAILY_SUMMARY', 'WEEKLY_SUMMARY', 'MONTHLY_SUMMARY', 'QUARTERLY_REVIEW', 'ANNUAL_REVIEW', 'INCIDENT_REPORT', 'THREAT_ANALYSIS', 'COMPLIANCE_REPORT', 'CUSTOM', name='reporttype'), nullable=False),
        sa.Column('template_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('default_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by_id', sa.UUID(), nullable=False),
        sa.Column('created_by_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id', 'created_by_role'], ['users.id', 'users.role'], name=op.f('fk_report_templates_created_by_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_report_templates'))
    )

    # Recreate the reports table
    op.create_table('reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.Enum('DAILY_SUMMARY', 'WEEKLY_SUMMARY', 'MONTHLY_SUMMARY', 'QUARTERLY_REVIEW', 'ANNUAL_REVIEW', 'INCIDENT_REPORT', 'THREAT_ANALYSIS', 'COMPLIANCE_REPORT', 'CUSTOM', name='reporttype'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'GENERATING', 'COMPLETED', 'FAILED', 'ARCHIVED', name='reportstatus'), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_location', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_format', sa.Enum('PDF', 'HTML', 'JSON', 'CSV', 'EXCEL', 'MARKDOWN', name='reportformat'), nullable=True),
        sa.Column('file_hash', sa.String(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_findings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('visualizations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('generation_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('time_range', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('included_sections', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_scheduled', sa.Boolean(), nullable=True),
        sa.Column('schedule_cron', sa.String(), nullable=True),
        sa.Column('next_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('allowed_roles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('allowed_users', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('creator_id', sa.UUID(), nullable=False),
        sa.Column('creator_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('related_alerts', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('related_reports', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('change_history', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['creator_id', 'creator_role'], ['users.id', 'users.role'], name=op.f('fk_reports_creator_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_reports')),
        sa.UniqueConstraint('filename', name=op.f('uq_reports_filename'))
    )

    # Recreate indexes for reports
    op.create_index('ix_reports_creator_created_at', 'reports', ['creator_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_reports_generated_at'), 'reports', ['generated_at'], unique=False)
    op.create_index('ix_reports_status_created_at', 'reports', ['status', 'created_at'], unique=False)
    op.create_index('ix_reports_type_created_at', 'reports', ['report_type', 'created_at'], unique=False)

    # Recreate the alert_notes table
    op.create_table('alert_notes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('alert_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('user_role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', 'API_USER', name='userrole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], name=op.f('fk_alert_notes_alert_id_alerts')),
        sa.ForeignKeyConstraint(['user_id', 'user_role'], ['users.id', 'users.role'], name=op.f('fk_alert_notes_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_alert_notes'))
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # This is a fix migration, so downgrade would revert to the broken state
    # It's better to not implement a downgrade path for this migration
    pass
    # ### end Alembic commands ###
