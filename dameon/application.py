from configuration import Configuration;
from models import Election,ElectionParticipant,Vote;
from datetime import datetime,timezone;
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_;
from redis import Redis;


engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

while True:
    try:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            while True:
                bytesList = redis.lrange(Configuration.REDIS_VOTES_LIST, 0, 0);
                if len(bytesList) != 0:
                    bytes=redis.lpop(Configuration.REDIS_VOTES_LIST);
                    data=bytes.decode("utf-8");
                    list=data.split(',');
                    guid=list[0];
                    participantNum=int(list[1]);
                    time = datetime.strptime(list[2], "%Y-%m-%dT%H:%M:%S%z");
                    jmbg=list[3];
                    existsElection=session.query(Election).filter(and_(Election.start<=time,time<=Election.end)).first();
                    if existsElection is not None:
                        electionId=existsElection.id;
                        isduplicate=session.query(Vote).filter(and_(Vote.ballotGuid==guid)).first();
                        if isduplicate is not None:
                            print(participantNum);
                            vote=Vote(electionId=electionId,poolNumber=participantNum,electionOfficialJmbg=jmbg,ballotGuid=guid,valid=False,reason="Duplicate ballot.");
                            session.add(vote);
                            session.commit();
                            continue;
                        participant=session.query(ElectionParticipant).filter(and_(ElectionParticipant.poolNumber==participantNum,ElectionParticipant.electionId==electionId)).first();
                        if participant is None:
                            print(participantNum);
                            vote=Vote(electionId=electionId,poolNumber=participantNum,electionOfficialJmbg=jmbg,ballotGuid=guid,valid=False,reason="Invalid poll number.");
                            session.add(vote);
                            session.commit();
                            continue;
                        vote=Vote(electionId=electionId,poolNumber=participantNum,electionOfficialJmbg=jmbg,ballotGuid=guid,valid=True);
                        session.add(vote);
                        if participant.result is not None:
                            participant.result+=1;
                        else:
                            participant.result=1;
                        election=session.query(Election).filter(Election.id==electionId).first();
                        election.votesNumber+=1;
                        session.commit();
                    else:
                        print("Ne postoje izbori");
    except Exception as error:
        print(error);