"""Initial migration

Revision ID: cb59f3cb7323
Revises: 
Create Date: 2021-09-06 16:20:57.278153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb59f3cb7323'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('elections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('individual', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('participants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('individual', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('electionparticipants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('electionId', sa.Integer(), nullable=False),
    sa.Column('participantId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['electionId'], ['elections.id'], ),
    sa.ForeignKeyConstraint(['participantId'], ['participants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('votes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('electionId', sa.Integer(), nullable=False),
    sa.Column('poolNumber', sa.Integer(), nullable=False),
    sa.Column('electionOfficialJmbg', sa.String(length=13), nullable=False),
    sa.Column('ballotGuid', sa.String(length=39), nullable=False),
    sa.Column('valid', sa.Boolean(), nullable=False),
    sa.Column('reason', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['electionId'], ['elections.id'], ),
    sa.ForeignKeyConstraint(['poolNumber'], ['participants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votes')
    op.drop_table('electionparticipants')
    op.drop_table('participants')
    op.drop_table('elections')
    # ### end Alembic commands ###
