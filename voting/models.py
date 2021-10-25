from flask_sqlalchemy import SQLAlchemy;

database=SQLAlchemy();


class ElectionParticipant(database.Model):
    __tablename__ = "electionparticipants";

    id = database.Column(database.Integer, primary_key=True);
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False);
    participantId = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable=False);
    result=database.Column(database.Integer,nullable=True);
    poolNumber=database.Column(database.Integer,nullable=False);


class Participant(database.Model):
    __tablename__="participants";

    id=database.Column(database.Integer,primary_key=True);
    name=database.Column(database.String(256),nullable=False);
    individual=database.Column(database.Boolean,nullable=False);
    elections=database.relationship("Election",secondary=ElectionParticipant.__table__,back_populates="participants")

    def to_JSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'individual': self.individual
        }

class Election(database.Model):
    __tablename__="elections";

    id=database.Column(database.Integer,primary_key=True);
    start=database.Column(database.DateTime(timezone=True),nullable=False);
    end=database.Column(database.DateTime(timezone=True),nullable=False);
    individual=database.Column(database.Boolean,nullable=False);
    participants=database.relationship("Participant",secondary=ElectionParticipant.__table__,back_populates="elections");
    votes = database.relationship("Vote", back_populates="election");
    votesNumber=database.Column(database.Integer,nullable=False);

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

class Vote(database.Model):
    __tablename__="votes";

    id = database.Column(database.Integer, primary_key=True);
    electionId=database.Column(database.Integer,database.ForeignKey("elections.id"),nullable=False);
    poolNumber=database.Column(database.Integer,nullable=False);
    electionOfficialJmbg=database.Column(database.String(13),nullable=False);
    ballotGuid=database.Column(database.String(39),nullable=False);
    valid=database.Column(database.Boolean,nullable=False);
    reason=database.Column(database.String(256));

    election = database.relationship("Election", back_populates="votes");

    def to_JSON(self):
        return {
            'electionOfficialJmbg': self.electionOfficialJmbg,
            'ballotGuid': self.ballotGuid,
            'pollNumber': self.pollNumber,
            'reason': self.reason
        }