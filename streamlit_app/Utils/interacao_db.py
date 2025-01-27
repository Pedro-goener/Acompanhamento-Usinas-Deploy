import pandas as pd
from sqlalchemy import create_engine,text
import streamlit as st
def load_and_prepare_data(db_config: dict, query: str) -> pd.DataFrame:
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )
    engine = create_engine(connection_string)

    df = pd.read_sql_query(query, engine)

    return df
db_config = {
        'host': st.secrets["database"]["host"],
        'port': st.secrets["database"]["port"],
        'dbname': st.secrets["database"]["database"],
        'user': st.secrets["database"]["user"],
        'password': st.secrets["database"]["password"]
}
usinas_dict = {
    'bet01':1,
    'por01':2,
    'cem01':3,
    'cem02':4,
    'jgr01':5,
    'ara01':6
}


def update_data(db_config, update_id, observacao):

    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )

    engine = create_engine(connection_string)

    query = text("""
        UPDATE tabela_ocorrencias 
        SET "Verificado" = NOT "Verificado",
            "Observacao" = :observacao 
        WHERE index = :update_id
        """)
    params = {
        'observacao': observacao,
        'update_id': int(update_id)
    }
    with engine.connect() as connection:
        connection.execute(query,params)
        connection.commit()

