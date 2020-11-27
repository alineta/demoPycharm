import pandas as pd
import sqlalchemy

class lireOracle():
    def __init__(self):
        engine = sqlalchemy.create_engine("oracle+cx_oracle://stagbi25:Phoenix#Icar67@51.91.76.248:15440/coursdb")
        print("connexion avec la base de données Oracle : " + str(engine))
        self.connection     = engine.connect()
        self.listeTables    = pd.DataFrame()
        self.listeColTables = pd.DataFrame()
        self.listeRelTab    = pd.DataFrame()

    def lectureListeTables(self):
        """
           la lecture à partir de la base de données de la requette et alimentation du DataFrame en retour
        """
        requette = """
                    select table_name as "nom_table"
                    from user_tables
                   """
        return pd.read_sql_query(requette, self.connection)


    def lectureListeRelationsTables(self):
        requette = """
                select tbe.CONSTRAINT_NAME        as "nom_contrainte",  
                           tbm.TABLE_NAME         as "table_parent",
                           clm.COLUMN_NAME        as "col_tab_parent",
                           tbe.TABLE_NAME         as "table_enfant",
                           cle.COLUMN_NAME        as "col_tab_enfant" 
                from user_constraints tbe 
                     join user_cons_columns cle
                       on  tbe.TABLE_NAME      = cle.TABLE_NAME
                       and tbe.CONSTRAINT_NAME = cle.CONSTRAINT_NAME 
                     join user_constraints tbm 
                       on tbm.CONSTRAINT_NAME = tbe.R_CONSTRAINT_NAME 
                     join user_cons_columns clm
                       on  tbm.TABLE_NAME      = clm.TABLE_NAME
                       and tbm.CONSTRAINT_NAME = clm.CONSTRAINT_NAME 
                where tbe.CONSTRAINT_TYPE = 'R'
        """

        return pd.read_sql_query(requette, self.connection)


    def lectureListeTablesColonnees(self):
        requette = """
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

        return pd.read_sql_query(requette, self.connection)

    def lecture(self):
        """
           la lecture du dictionnaire
        """
        self.listeTables    = self.lectureListeTables()
        self.listeRelTab    = self.lectureListeRelationsTables()
        self.listeColTables = self.lectureListeTablesColonnees()





if __name__ == '__main__':
    lt = lireOracle()
    lt.lecture()
    print(lt.listeColTables.head())
