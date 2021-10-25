from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate,init,migrate,upgrade;
from models import database,Role,User,UserRole;
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
            UserRole.query.delete();
            database.session.commit();
            Role.query.delete();
            database.session.commit();
            User.query.delete();
            database.session.commit();

            adminRole=Role(name="administrator");
            userRole=Role(name="zvanicnik");

            database.session.add(adminRole);
            database.session.add(userRole);

            database.session.commit();

            admin=User(
                jmbg="0000000000000",
                forename="admin",
                surname="admin",
                email="admin@admin.com",
                password="1"
        );
            database.session.add(admin);
            database.session.commit();
            userRole=UserRole(
                userId=admin.id,
                roleId=adminRole.id
        );
            database.session.add(userRole);
            database.session.commit();
            done = True;
    except Exception as error:
        print(error);