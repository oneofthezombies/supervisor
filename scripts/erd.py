import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy_schemadisplay import create_schema_graph

db_username = os.environ["DB_USERNAME"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_name = "supervisor"

engine = create_engine(
    f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
)

metadata = MetaData()
metadata.reflect(bind=engine)

graph = create_schema_graph(engine, metadata=metadata)
graph.write_png("erd.png")
