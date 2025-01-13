import pandas as pd
from sqlalchemy import create_engine
def load_and_prepare_data(db_config: dict, query: str) -> pd.DataFrame:
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )
    engine = create_engine(connection_string)

    df = pd.read_sql_query(query, engine)

    return df