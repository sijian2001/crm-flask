"""Add employee management tables

Revision ID: 002
Revises: 001
Create Date: 2025-09-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create employee, position, and department tables"""

    # Create positions table first (no dependencies)
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('is_management', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('salary_max', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_positions_level', 'positions', ['level'])
    op.create_index('ix_positions_is_active', 'positions', ['is_active'])

    # Create departments table (self-referencing)
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_departments_parent_id', 'departments', ['parent_id'])
    op.create_index('ix_departments_is_active', 'departments', ['is_active'])

    # Create employees table (references stores, positions, departments, and self)
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_code', sa.String(length=20), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('employment_status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('salary_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('employee_code'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint('salary_level >= 1 AND salary_level <= 10', name='check_salary_level_range')
    )
    op.create_index('ix_employees_employee_code', 'employees', ['employee_code'])
    op.create_index('ix_employees_email', 'employees', ['email'])
    op.create_index('ix_employees_store_id', 'employees', ['store_id'])
    op.create_index('ix_employees_position_id', 'employees', ['position_id'])
    op.create_index('ix_employees_department_id', 'employees', ['department_id'])
    op.create_index('ix_employees_manager_id', 'employees', ['manager_id'])
    op.create_index('ix_employees_employment_status', 'employees', ['employment_status'])
    op.create_index('ix_employees_hire_date', 'employees', ['hire_date'])
    op.create_index('ix_employees_last_name', 'employees', ['last_name'])


def downgrade():
    """Drop employee management tables"""

    # Drop in reverse order due to foreign key constraints
    op.drop_table('employees')
    op.drop_table('departments')
    op.drop_table('positions')