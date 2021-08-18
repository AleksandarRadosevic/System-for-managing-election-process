from flask import Flask,request,Response,jsonify;
from configuration import Configuration;
from models import database,Participant,Election,ElectionParticipant;
from email.utils import parseaddr;
from re import match,search;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from adminDecorater import roleCheck;
from datetime import datetime;

application=Flask(__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

@application.route("/createParticipant",methods=["POST"])
@roleCheck(role="administrator")
def createParticipant():
    name = request.json.get("name", "");
    individual = request.json.get("individual", None);

    if (len(name)==0):
        return jsonify({'message':'Field name is missing'}),400;
    if (individual is None):
        return jsonify({'message':'Field individual is missing'}),400;

    participant=Participant(name=name,individual=individual);

    database.session.add(participant);
    database.session.commit();

    return jsonify({'id':participant.id}),200;


@application.route("/getParticipants",methods=["GET"])
@roleCheck(role="administrator")
def getParticipants():
    participants=Participant.query.all();
    array=[];
    for participant in participants:
        array.append(participant.to_JSON());

    return jsonify(participants=array),200;


@application.route("/createElection",methods=["POST"])
@roleCheck(role="administrator")
def createElection():

    start=request.json.get("start","");
    end=request.json.get("end","");
    individual=request.json.get("individual",None);
    participants=request.json.get("participants","");

    # check if some field is missing
    if (len(start)==0):
        return jsonify({'message':'Field start is missing'}),400;
    if (len(end) == 0):
        return jsonify({'message': 'Field end is missing'}), 400;
    if (individual is None):
        return jsonify({'message':'Field individual is missing'}),400;
    if (type(individual)!=bool):
        return jsonify({'message':'Field individual must be bool'}),400;
    if (len(participants)==0):
        return jsonify({'message':'Field participants is missing'}),400;

    # check format of fields
    # check datas
    try:
        startDate = datetime.strptime(start, "%Y-%m-%d");
        endDate = datetime.strptime(end, "%Y-%m-%d");
    except:
        return jsonify({'message': 'Invalid date and time'}), 400;

    if (startDate>=endDate):
       return jsonify({'message':'Invalid date and time'}),400;

    elections=Election.query.all();
    for election in elections:
        if (min(election.end - startDate, endDate - election.start).days + 1>0):
            return jsonify({'message': 'Invalid date and time'}), 400;

    election=Election(start=start,end=end,individual=individual);
    database.session.add(election);
    # check participants
    if (len(participants)<2):
        return jsonify({'message': 'Invalid participant.'});

    for participantId in participants:
        existP=Participant.query.filter(Participant.id==participantId).first();
        if (not existP):
            return jsonify({'message':'Invalid participant.'});

        # if elections are parlamental and participant is individual
        # if elections are president and participant is not individual
        if (existP.individual ^ individual):
            return jsonify({'message': 'Invalid participant.'});
        participantInElection=ElectionParticipant(electionId=election.id,participantId=existP.id);
        database.session.add(participantInElection);


    database.session.commit();

    return jsonify(pollnumbers=participants),200;


@application.route("/getElections",methods=["GET"])
@roleCheck(role="administrator")
def getElections():
    elections=Election.query.all();
    arr=[];
    for election in elections:
        arr.append(election.to_JSON());
    return jsonify(elections=arr),200;

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, port = 5001 );