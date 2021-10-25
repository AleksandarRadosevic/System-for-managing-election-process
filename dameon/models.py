from sqlalchemy.ext.declarative import declarative_base;
from sqlalchemy import Column, Integer, String,ForeignKey,Boolean,DateTime
from sqlalchemy.orm import relationship;


Base = declarative_base()

class ElectionParticipant(Base):
    __tablename__ = "electionparticipants";

    id = Column(Integer, primary_key=True);
    electionId = Column(Integer, ForeignKey("elections.id"), nullable=False);
    participantId = Column(Integer, ForeignKey("participants.id"), nullable=False);
    result=Column(Integer,nullable=True);
    poolNumber=Column(Integer,nullable=False);


class Participant(Base):
    __tablename__="participants";

    id=Column(Integer,primary_key=True);
    name=Column(String(256),nullable=False);
    individual=Column(Boolean,nullable=False);
    elections=relationship("Election",secondary=ElectionParticipant.__table__,back_populates="participants")

    def to_JSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'individual': self.individual
        }

class Election(Base):
    __tablename__="elections";

    id=Column(Integer,primary_key=True);
    start=Column(DateTime(timezone=True),nullable=False);
    end=Column(DateTime(timezone=True),nullable=False);
    individual=Column(Boolean,nullable=False);
    participants=relationship("Participant",secondary=ElectionParticipant.__table__,back_populates="elections");
    votes = relationship("Vote", back_populates="election");
    votesNumber=Column(Integer,nullable=False);

    def to_JSON(self):
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'individual': self.individual,
            'participants':[
                {'id':participant.id, 'name':participant.name} for participant in self.participants
            ]
        }

class Vote(Base):
    __tablename__="votes";

    id = Column(Integer, primary_key=True);
    electionId=Column(Integer,ForeignKey("elections.id"),nullable=False);
    poolNumber=Column(Integer,nullable=False);
    electionOfficialJmbg=Column(String(13),nullable=False);
    ballotGuid=Column(String(39),nullable=False);
    valid=Column(Boolean,nullable=False);
    reason=Column(String(256));

    election = relationship("Election", back_populates="votes");

    def to_JSON(self):
        return {
            'electionOfficialJmbg': self.electionOfficialJmbg,
            'ballotGuid': self.ballotGuid,
            'pollNumber': self.pollNumber,
            'reason': self.reason
        }