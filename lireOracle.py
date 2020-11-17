import pandas as pd
import sqlalchemy

def lireFichierAir():
    return pd.read_csv('c:/Solutions/donnees/AirQualityUCI01.csv')

def lireConstraintes():
    engine = sqlalchemy.create_engine("oracle+cx_oracle://stag01:Phoenix#Icar67@51.91.76.248:15440/coursdb")
    print("connecting with engine " + str(engine))
    connection = engine.connect()
    query = """
                select p.table_name,
                       f.table_name, 
                       p.constraint_name,
                       f.constraint_name
                from user_constraints p join user_constraints f 
                on f.r_constraint_name = p.constraint_name
    """
    return pd.read_sql_query(query, connection)



if __name__ == '__main__':
    print(lireFichierAir().head())
