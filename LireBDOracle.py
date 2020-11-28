import pandas as pd
from sqlalchemy import create_engine

#____ Connexion à la base Oracle
engine = create_engine('oracle+cx_oracle://stagbi25:Phoenix#Icar67@51.91.76.248:15440/coursdb',
                       max_identifier_length=128)
print("connecting with engine " + str(engine))
connection = engine.connect()

#____Extraction de la table des contraintes = Relations entre les tables
def BdDlisteRelations():
    queryTRelations = """
                SELECT
    rel_tablemère.constraint_name    "id_TableRelation",           
    rel_tablemère.table_name    "NomTableMère",
    t_clés_mère.column_name     "colTableMère",
    rel_tablefille.table_name   "NomTableFille",
    t_clés_fille.column_name    "colTableFille",
    Rel_TableMère.constraint_type "TypeRelMère",
    rel_tablefille.constraint_type "RTypeRelFille"

    FROM
    user_constraints    rel_tablemère
    JOIN user_cons_columns   t_clés_mère ON t_clés_mère.constraint_name = rel_tablemère.constraint_name
    JOIN user_constraints    rel_tablefille ON rel_tablefille.constraint_name = rel_tablemère.r_constraint_name
    JOIN user_cons_columns   t_clés_fille ON rel_tablefille.constraint_name = t_clés_fille.constraint_name
                                           AND t_clés_fille.position = t_clés_mère.position
    """
    return pd.read_sql_query(queryTRelations, connection)


#____Extraction du nom des tables de la BdD
def BdDlisteTables():
    #max_identifier_length=128
    queryListeTables = """
    SELECT
    constraint_name     "Id_RelTable",
    table_name          "NomTable",
    column_name         "IdTable"
FROM
    user_cons_columns
WHERE
    position = 1
ORDER BY table_name
"""
    return pd.read_sql_query(queryListeTables, connection)

def BdDlisteColonnesTables():
    queryListeColTables = """
                    select  
                           tc.TABLE_NAME                                                 as "nom_table",
                           tc.COLUMN_ID                                                  as "id_colonne",
                           tc.COLUMN_NAME                                                as "nom_colonne",
                           lower(tc.DATA_TYPE)                                           as "type_colonne",
                           nvl(to_char(coalesce(tc.DATA_PRECISION, tc.DATA_LENGTH)),' ') as "taille_colonne",
                           nvl(to_char(tc.DATA_SCALE),' ')                               as "precision_colonne",
                           decode(tc.NULLABLE,'Y','null','N','not null')                 as "is_nullable",
                           nvl(ky.CONSTRAINT_TYPE,' ')                                   as "type_contrainte", 
                           nvl(ky.CONSTRAINT_NAME,' ')                                   as "nom_contrainte"
                    from user_tab_columns tc
                         left join (select                             
                                       co.OWNER                   ,
                                       co.TABLE_NAME              ,
                                       cc.COLUMN_NAME             ,
                                       co.CONSTRAINT_TYPE||'K'  as CONSTRAINT_TYPE,
                                       co.CONSTRAINT_NAME         
                                from user_constraints co 
                                     join user_cons_columns cc
                                       on  co.TABLE_NAME      = cc.TABLE_NAME
                                       and co.CONSTRAINT_NAME = cc.CONSTRAINT_NAME 
                                where co.CONSTRAINT_TYPE in ('P','U')) ky
                          on (     tc.TABLE_NAME     = ky.TABLE_NAME  
                               and tc.COLUMN_NAME    = ky.COLUMN_NAME  )
"""
    return pd.read_sql_query(queryListeColTables, connection)