import os;

databaseUrl = os.environ["DATABASE_URL"];
redisHost = os.environ["REDIS_HOST"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/electionsDatabaseDB";
    JSON_SORT_KEYS = False;
    JWT_SECRET_KEY = "JWT_SECRET_KEY";
    REDIS_HOST = redisHost;
    REDIS_VOTES_LIST = "votes";

