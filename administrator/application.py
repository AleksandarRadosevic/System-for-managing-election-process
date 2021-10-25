from flask import Flask,request,Response,jsonify;
from configuration import Configuration;
from models import database,Participant,Election,ElectionParticipant,Vote;
from email.utils import parseaddr;
from re import match,search;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_, or_;
from adminDecorater import roleCheck;
from datetime import datetime,timezone;
import pytz;
from sqlalchemy import desc;

application=Flask(__name__);
application.config.from_object(Configuration);
jwt = JWTManager(application);

@application.route("/createParticipant",methods=["POST"])
@roleCheck(role="administrator")
def createParticipant():
    name = request.json.get("name", "");
    individual = request.json.get("individual", None);

    if (len(name)==0):
        return jsonify({'message':'Field name is missing.'}),400;
    if (individual is None):
        return jsonify({'message':'Field individual is missing.'}),400;

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
    try:
        start=request.json.get("start","");
        end=request.json.get("end","");
        individual=request.json.get("individual",None);
        participants=request.json.get("participants",None);
    except:
        return jsonify(message='Field start is missing.'), 400;
    # check if some field is missing
    if (len(start)==0):
        return jsonify({'message':'Field start is missing.'}),400;
    if (len(end) == 0):
        return jsonify({'message': 'Field end is missing.'}),400;
    if (individual is None):
        return jsonify({'message':'Field individual is missing.'}),400;
    if (type(individual)!=bool):
        return jsonify({'message':'Field individual is missing.'}),400;
    if participants is None:
        return jsonify({'message':'Field participants is missing.'}),400;

    # check format of fields
    # check datas
    try:
        if len(start)==19 or len(end)==19:
            raise Exception();
        startDate = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z");
        endDate = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z");

    except:
        try:
            if len(start)==19:
                startDate=start+"+0200";
            else:
                startDate=start;
            if len(end)==19:
                endDate=end+"+0200";
            else:
                endDate=end;
            startDate = datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S%z");
            endDate = datetime.strptime(endDate, "%Y-%m-%dT%H:%M:%S%z");

        except:
            return jsonify({'message': 'Invalid date and time.'}),400;
    startDate = startDate.astimezone(pytz.timezone('Europe/Belgrade'));
    endDate = endDate.astimezone(pytz.timezone('Europe/Belgrade'));
    if (startDate>=endDate):
        return jsonify({'message':'Invalid date and time.'}),400;

    elections=Election.query.all();
    if len(elections)>0:
        number=Election.query.filter(or_(and_(startDate<=Election.start,Election.start<=endDate),and_(startDate>=Election.start,startDate<=Election.end))).count();
        if number>0:
            return jsonify({'message': 'Invalid date and time.'}),400;
    election = Election(start=startDate, end=endDate, individual=individual, votesNumber=0);
    database.session.add(election);

    # check participants
    if (len(participants)<2):
        return jsonify({'message': 'Invalid participants.'}),400;

    participantsNew=[];
    i=1;
    for participantId in participants:
        try:
            int(participantId);
        except:
            return jsonify(message='Invalid participants.'), 400;
        existP=Participant.query.filter(Participant.id==participantId).first();
        if (not existP):
            return jsonify({'message':'Invalid participants.'}),400;

        # if elections are parlamental and participant is individual
        # if elections are president and participant is not individual
        if ((existP.individual==False and individual==True) or (existP.individual==True and individual==False)):
            return jsonify({'message': 'Invalid participants.'}),400;
        participantInElection=ElectionParticipant(electionId=election.id,participantId=existP.id,poolNumber=i);
        database.session.add(participantInElection);
        participantsNew.append(i);
        i=i+1;

    database.session.commit();

    return jsonify(pollNumbers=participantsNew),200;


@application.route("/getElections",methods=["GET"])
@roleCheck(role="administrator")
def getElections():
    elections=Election.query.all();
    arr=[];
    for election in elections:
        arr.append(election.to_JSON());
    return jsonify(elections=arr),200;


@application.route("/getResults",methods=["GET"])
@roleCheck(role="administrator")
def getResults():
    try:
        electionId = request.args.get("id", None);
        if electionId is None:
            raise Exception;
    except:
        return jsonify(message="Field id is missing."), 400;

    election=Election.query.filter(Election.id==electionId).first();
    if election is None:
        return jsonify({'message':'Election does not exist.'}),400;

    timeNow = datetime.now(timezone.utc).astimezone(pytz.timezone('Europe/Belgrade'));
    startDate= pytz.utc.localize(election.start);
    endDate=pytz.utc.localize(election.end);
    if startDate<=timeNow and endDate>=timeNow:
        return jsonify({'message':'Election is ongoing.'}),400;

    participants=[];
    participantsInElection=ElectionParticipant.query.filter(ElectionParticipant.electionId==electionId);
    # calculate if elections are presidental
    if election.individual==1:
        for item in participantsInElection:
            participant=presidentalElection(item,election);
            participants.append(participant);
    else:
        participants=parlamentalElecion(participantsInElection,election);
    invalidVotes=Vote.query.filter(and_(Vote.electionId==electionId,Vote.valid==False));
    invalidData=[];
    for item in invalidVotes:
        invalidData.append({
            "electionOfficialJmbg": item.electionOfficialJmbg,
            "ballotGuid": item.ballotGuid,
            "pollNumber": item.poolNumber,
            "reason": item.reason
        });

    return jsonify(participants=participants,invalidVotes=invalidData),200;
def presidentalElection(item,election):
    part = Participant.query.filter(Participant.id == item.participantId).first();
    participant={
        "pollNumber": item.poolNumber,
        "name": part.name,
        "result": 0,
    }
    if election.votesNumber>0:
        res=item.result/election.votesNumber;
        res=float(str(round(res,2)));
        participant['result']=res;
    return participant;


def parlamentalElecion(participantsInElection,election):
    mandateNumbers=250;
    participantsPassed=[];

    for item in participantsInElection:
        percentage=item.result/election.votesNumber;
        part=Participant.query.filter(Participant.id==item.participantId).first();
        participantsPassed.append({
            'id':part.id,
            'pollNumber':item.poolNumber,
            'name':part.name,
            'voteNumber':item.result,
            'mandatesNumber':0
        });
        if percentage<0.05:
            participantsPassed[-1]['voteNumber']=0;
    while mandateNumbers>0:
        averages=[];
        for item in participantsPassed:
            res=item['voteNumber']/(item['mandatesNumber']+1);
            averages.append(res);
        maxValue=max(averages);
        index=averages.index(maxValue);
        participantsPassed[index]['mandatesNumber']+=1;
        averages.clear();
        mandateNumbers-=1;

    participants=[];
    for item in participantsPassed:
        participants.append({
        'pollNumber': item['pollNumber'],
        "name": item['name'],
        "result":int(item['mandatesNumber'])
        });
    return participants;

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run (host = "0.0.0.0", port = 5001 );