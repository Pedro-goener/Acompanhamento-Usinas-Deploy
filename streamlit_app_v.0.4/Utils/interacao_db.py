import pandas as pd
from sqlalchemy import create_engine
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