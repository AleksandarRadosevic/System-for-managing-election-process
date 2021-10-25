import os;

databaseUrl = os.environ["DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/electionsDatabaseDB";
    JWT_SECRET_KEY = "JWT_SECRET_KEY";
    JSON_SORT_KEYS = False;
