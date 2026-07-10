"""initial schema

Revision ID: dd417b6648f8
Revises:
Create Date: 2026-07-10 02:28:02.383204

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

revision: str = 'dd417b6648f8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CATEGORIES = [
    {"id": 1, "slug": "love", "color": "#E5484D", "icon": "heart", "position": 1},
    {"id": 2, "slug": "happy_moments", "color": "#FFB224", "icon": "smile", "position": 2},
    {"id": 3, "slug": "dreams", "color": "#6E56CF", "icon": "sparkles", "position": 3},
    {"id": 4, "slug": "education", "color": "#3E63DD", "icon": "graduation-cap", "position": 4},
    {"id": 5, "slug": "career", "color": "#64748B", "icon": "briefcase", "position": 5},
    {"id": 6, "slug": "travel", "color": "#0BA5EC", "icon": "plane", "position": 6},
    {"id": 7, "slug": "friendship", "color": "#F76B15", "icon": "users", "position": 7},
    {"id": 8, "slug": "childhood", "color": "#EC4899", "icon": "baby", "position": 8},
    {"id": 9, "slug": "achievements", "color": "#18A957", "icon": "trophy", "position": 9},
    {"id": 10, "slug": "beautiful_places", "color": "#12A594", "icon": "mountain", "position": 10},
    {"id": 11, "slug": "memories", "color": "#A9714B", "icon": "camera", "position": 11},
    {"id": 12, "slug": "urban_legends", "color": "#A21CAF", "icon": "ghost", "position": 12},
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    categories = op.create_table('categories',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('slug', sa.Text(), nullable=False),
    sa.Column('color', sa.Text(), nullable=False),
    sa.Column('icon', sa.Text(), nullable=False),
    sa.Column('position', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('slug', name=op.f('uq_categories_slug'))
    )
    op.bulk_insert(categories, CATEGORIES)
    op.execute("SELECT setval(pg_get_serial_sequence('categories', 'id'), 12)")

    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.Text(), nullable=True),
    sa.Column('first_name', sa.Text(), nullable=True),
    sa.Column('last_name', sa.Text(), nullable=True),
    sa.Column('language_code', sa.Text(), nullable=True),
    sa.Column('photo_url', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('telegram_id', name=op.f('uq_users_telegram_id'))
    )
    op.create_table('stories',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('category_id', sa.SmallInteger(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('happened_on', sa.Date(), nullable=True),
    sa.Column('is_anonymous', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('visibility', sa.Enum('public', 'private', name='story_visibility'), server_default='public', nullable=False),
    sa.Column('location_precision', sa.Enum('exact', 'approx', name='location_precision'), nullable=False),
    sa.Column('location_exact', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('location_public', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('is_hidden', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_stories_author_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_stories_category_id_categories'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_stories'))
    )
    op.create_index(op.f('ix_stories_author_id'), 'stories', ['author_id'], unique=False)
    op.create_index(op.f('ix_stories_category_id'), 'stories', ['category_id'], unique=False)
    op.create_index('ix_stories_created_at', 'stories', ['created_at'], unique=False)
    op.create_index('ix_stories_location_public', 'stories', ['location_public'], unique=False, postgresql_using='gist')
    op.create_table('bookmarks',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('story_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], name=op.f('fk_bookmarks_story_id_stories'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_bookmarks_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'story_id', name=op.f('pk_bookmarks'))
    )
    op.create_table('comments',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('story_id', sa.UUID(), nullable=False),
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('is_hidden', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_comments_author_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], name=op.f('fk_comments_story_id_stories'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_comments'))
    )
    op.create_index(op.f('ix_comments_author_id'), 'comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_comments_story_id'), 'comments', ['story_id'], unique=False)
    op.create_table('reactions',
    sa.Column('story_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.Text(), server_default=sa.text("'heart'"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], name=op.f('fk_reactions_story_id_stories'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_reactions_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('story_id', 'user_id', name=op.f('pk_reactions'))
    )
    op.create_table('story_photos',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('story_id', sa.UUID(), nullable=False),
    sa.Column('object_key', sa.Text(), nullable=False),
    sa.Column('thumb_key', sa.Text(), nullable=True),
    sa.Column('content_type', sa.Text(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('position', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('status', sa.Enum('pending', 'ready', 'failed', name='photo_status'), server_default='pending', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], name=op.f('fk_story_photos_story_id_stories'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_story_photos'))
    )
    op.create_index(op.f('ix_story_photos_story_id'), 'story_photos', ['story_id'], unique=False)
    op.create_table('reports',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('reporter_id', sa.BigInteger(), nullable=True),
    sa.Column('story_id', sa.UUID(), nullable=True),
    sa.Column('comment_id', sa.UUID(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('(story_id IS NULL) != (comment_id IS NULL)', name=op.f('ck_reports_exactly_one_target')),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], name=op.f('fk_reports_comment_id_comments'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], name=op.f('fk_reports_reporter_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], name=op.f('fk_reports_story_id_stories'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_reports'))
    )
    op.create_index('uq_reports_reporter_comment', 'reports', ['reporter_id', 'comment_id'], unique=True, postgresql_where=sa.text('comment_id IS NOT NULL'))
    op.create_index('uq_reports_reporter_story', 'reports', ['reporter_id', 'story_id'], unique=True, postgresql_where=sa.text('story_id IS NOT NULL'))


def downgrade() -> None:
    op.drop_index('uq_reports_reporter_story', table_name='reports', postgresql_where=sa.text('story_id IS NOT NULL'))
    op.drop_index('uq_reports_reporter_comment', table_name='reports', postgresql_where=sa.text('comment_id IS NOT NULL'))
    op.drop_table('reports')
    op.drop_index(op.f('ix_story_photos_story_id'), table_name='story_photos')
    op.drop_table('story_photos')
    op.drop_table('reactions')
    op.drop_index(op.f('ix_comments_story_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_author_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_table('bookmarks')
    op.drop_index('ix_stories_location_public', table_name='stories', postgresql_using='gist')
    op.drop_index('ix_stories_created_at', table_name='stories')
    op.drop_index(op.f('ix_stories_category_id'), table_name='stories')
    op.drop_index(op.f('ix_stories_author_id'), table_name='stories')
    op.drop_table('stories')
    op.drop_table('users')
    op.drop_table('categories')
    op.execute("DROP TYPE IF EXISTS photo_status")
    op.execute("DROP TYPE IF EXISTS location_precision")
    op.execute("DROP TYPE IF EXISTS story_visibility")
