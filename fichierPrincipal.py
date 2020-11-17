import dash_core_components as dcc
import dash_html_components as html

import lireOracle
import pandas as pd
import sqlalchemy


if __name__ == '__main__':
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
    df = pd.read_sql_query(query, connection)  # df.to_sql('nom', con=engine,if_exists='replace')

    print(df.head())
