"""criando tabela para termos de busca

Revision ID: 5a87008f3035
Revises: 32dc0da3388e
Create Date: 2024-12-05 01:29:48.396618
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5a87008f3035'
down_revision: Union[str, None] = '32dc0da3388e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Tabelas de termos de busca ###
    op.create_table('TB_CATEGORIA_BUSCA',
        sa.Column('ID', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('NM_CATEGORIA', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('ID')
    )
    
    op.create_table('TB_TERMO_BUSCA',
        sa.Column('ID', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ID_CATEGORIA', sa.Integer(), nullable=True),
        sa.Column('KEYWORD', sa.String(length=50), nullable=False),
        sa.Column('OR_TERMS', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['ID_CATEGORIA'], ['TB_CATEGORIA_BUSCA.ID']),
        sa.PrimaryKeyConstraint('ID')
    )
    
    # ### Modificação de tabela TB_NOTICIA_RASPADA ###
    op.alter_column('TB_NOTICIA_RASPADA', 'URL',
        existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=1000),
        nullable=False
    )
    op.alter_column('TB_NOTICIA_RASPADA', 'QUERY',
        existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=250),
        nullable=True
    )
    op.alter_column('TB_NOTICIA_RASPADA', 'STATUS',
        existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=45),
        type_=sa.String(length=25),
        existing_nullable=True
    )
    op.create_index(op.f('ix_TB_NOTICIA_RASPADA_ID'), 'TB_NOTICIA_RASPADA', ['ID'], unique=False)
    op.create_foreign_key(None, 'TB_NOTICIA_RASPADA', 'TB_USER', ['ID_USUARIO'], ['ID'])
    op.drop_column('TB_NOTICIA_RASPADA', 'OPERACAO')


def downgrade() -> None:
    # ### Desfazendo as modificações feitas ###

    # Removendo as tabelas de termos de busca
    op.drop_table('TB_TERMO_BUSCA')
    op.drop_table('TB_CATEGORIA_BUSCA')

    # Desfazendo as alterações na tabela TB_NOTICIA_RASPADA
    op.add_column('TB_NOTICIA_RASPADA', sa.Column('OPERACAO', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True))
    op.drop_constraint(None, 'TB_NOTICIA_RASPADA', type_='foreignkey')
    op.drop_index(op.f('ix_TB_NOTICIA_RASPADA_ID'), table_name='TB_NOTICIA_RASPADA')
    op.alter_column('TB_NOTICIA_RASPADA', 'STATUS',
        existing_type=sa.String(length=25),
        type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=45),
        existing_nullable=True
    )
    op.alter_column('TB_NOTICIA_RASPADA', 'QUERY',
        existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=250),
        nullable=False
    )
    op.alter_column('TB_NOTICIA_RASPADA', 'URL',
        existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=1000),
        nullable=True
    )
