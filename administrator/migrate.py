from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate,init,migrate,upgrade;
from models import database,Vote,Election,Participant,ElectionParticipant;
from sqlalchemy_utils import database_exists,create_database;


application=Flask(__name__);
application.config.from_object(Configuration);

migrateObject=Migrate(application,database);

done=False;

while not done:
    try:
        if (not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"]);

        database.init_app(application);

        with application.app_context() as context:
            init();
            migrate(message="Production migration");
            upgrade();
            Vote.query.delete();
            database.session.commit();
            ElectionParticipant.query.delete();
            database.session.commit();
            Participant.query.delete();
            database.session.commit();
            Election.query.delete();
            database.session.commit();

            done = True;
			
    except Exception as error:
        print(error);