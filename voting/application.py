from flask import Flask,request,Response,jsonify;
from configuration import Configuration;
from models import database;
from flask_jwt_extended import JWTManager, get_jwt;
from roleDecorater import roleCheck;
from redis import Redis;
from datetime import datetime, timezone;

import io;
import csv;
import pytz;

application=Flask(__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);


@application.route("/vote",methods=["POST"])
@roleCheck(role="zvanicnik")
def vote():
    try:
        file = request.files.get("file", None);
        if file is None:
            raise Exception();
        content = file.stream.read().decode("utf-8");
        stream = io.StringIO(content);
        reader = csv.reader(stream);
    except:
        return jsonify({'message': 'Field file is missing.'}),400;

    val=0;
    for row in reader:
        if (len(row)!=2):
            return jsonify({'message': f'Incorrect number of values on line {val}.'}),400;
        try:
            if (int(row[1])<0):
                return jsonify({'message': f'Incorrect poll number on line {val}.'}),400;
        except:
            return jsonify({'message': f'Incorrect poll number on line {val}.'}), 400;
        val=val+1;

    stream = io.StringIO(content);
    reader = csv.reader(stream);
    timeNow = datetime.now(timezone.utc).astimezone(pytz.timezone('Europe/Belgrade'));

    jmbg = get_jwt().get("jmbg", "");

    for row in reader:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_VOTES_LIST, row[0] + "," + row[1] + "," + datetime.strftime(timeNow,"%Y-%m-%dT%H:%M:%S%z") + "," + jmbg);

    return Response(status=200);

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( host = "0.0.0.0", port = 5003);
