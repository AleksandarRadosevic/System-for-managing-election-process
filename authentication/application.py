from flask import Flask,request,Response,jsonify;
from configuration import Configuration;
from models import database,User,UserRole;
from email.utils import parseaddr;
from re import match,search;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from adminDecorater import roleCheck;


application=Flask(__name__);
application.config.from_object(Configuration);


def is_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True;
            else:
                return False;
        else:
            return True;
    else:
        return False;

#check if jmbg is correct
def is_valid_jmbg(jmbg):
    if (match('^[0-9]{13}$',jmbg) is None):
        return False;
    dd=int(jmbg[0:2]);
    a=int(jmbg[0]);
    b=int(jmbg[1]);

    mm=int(jmbg[2:4]);
    c=int(jmbg[2]);
    d=int(jmbg[3]);

    yyy=int(jmbg[4:7]);
    e=int(jmbg[4]);
    f=int(jmbg[5]);
    g=int(jmbg[6]);

    rr=int(jmbg[7:9]);
    h=int(jmbg[7]);
    i=int(jmbg[8]);

    bbb=int(jmbg[9:12]);
    j=int(jmbg[9]);
    k=int(jmbg[10]);
    l=int(jmbg[11]);

    lastNumber=int(jmbg[12:13]);




    isleap=is_leap_year(yyy);

    if (dd<0 or dd>31):
        return False;
    elif (mm<0 or mm>12):
        return False;
    elif (mm==2 and isleap==True and dd>29):
        return False;
    elif (mm==2 and isleap==False and dd>28):
        return False;
    elif (mm not in [1,3,5,7,8,10,12] and dd==31):
        return False;
    elif (rr<70 or rr>99):
        return False;

    m=11-((7*(a+g)+6*(b+h)+5*(c+i)+4*(d+j)+3*(e+k)+2*(f+l))% 11);
    if (m>9):
        m=0;
    if (m!=lastNumber):
        return False;
    return True;

def is_valid_password(password):
    if (len(password)<8 or len(password)>256):
        return False;
    elif (search('[a-z]', password) is None):
        return False;
    elif (search('[A-Z]', password) is None):
        return False;
    elif (search('[\d]', password) is None):
        return False;

#register user
@application.route("/register",methods=["POST"])
def register():
    jmbg=request.json.get("jmbg","");
    forename=request.json.get("forename","");
    surname=request.json.get("surname","");
    email=request.json.get("email","");
    password=request.json.get("password","");

    if (len(jmbg)==0):
        return Response("Field jmbg is missing",status=400);
    elif (len(forename)==0):
        return Response("Field forename is missing",status=400);
    elif (len(surname)==0):
        return Response("Field surname is missing",status=400);
    elif (len(email)==0):
        return Response("Field email is missing",status=400);
    elif (len(password)==0):
        return Response("Field password is missing",status=400);

    #check for valid jmbg
    if (is_valid_jmbg(jmbg)==False):
        return Response("Invalid jmbg.");

    #check for valid email
    result = parseaddr ( email );
    if ( len ( result[1] ) == 0 or len(email)>256):
        return Response ( "Invalid email.", status = 400 );

    #check for valid password
    passValid=is_valid_password(password);
    if (passValid==False):
        return Response("Invalid password",status=400);

    #check if someone has this mail
    if (User.query.filter(User.email==email).first() is not None):
        return Response ( "Email already exists.", status = 400 );
    elif (User.query.filter(User.jmbg==jmbg).first() is not None):
        return Response("JMBG alreay exists.",status=400);
    user=User(email=email,forename=forename,surname=surname,password=password,jmbg=jmbg);
    database.session.add(user);
    database.session.commit();

    userRole = UserRole(userId=user.id, roleId=2);
    database.session.add(userRole);
    database.session.commit();

    return Response(status=200);

jwt=JWTManager(application);

@application.route("/login",methods=["POST"])
def login():
    email=request.json.get("email","");
    password=request.json.get("password","");

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;

    if (emailEmpty):
        return Response("Field email is empty ",status=400);
    elif (passwordEmpty):
        return Response("Field password is empty",status=400);

    result = parseaddr ( email );
    if ( len ( result[1] ) == 0 or len(email)>256):
        return Response ( "Invalid email.", status = 400 );

    user=User.query.filter(and_(User.email==email,User.password==password)).first();
    if (not user):
        return Response("Invalid credentials!",status=400);

    additionalClaims = {
            "forename": user.forename,
            "surname": user.surname,
            "roles": [ str ( role ) for role in user.roles ]
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    return jsonify ( accessToken = accessToken, refreshToken = refreshToken );

@application.route("/refresh",methods=["POST"])
@jwt_required()
def refresh():
    identity=get_jwt_identity();
    refreshClaims=get_jwt();

    additionalCLaims= {
        "jmbg":refreshClaims["jmbg"],
        "forename":refreshClaims["forename"],
        "surname":refreshClaims["surname"],
        "roles":refreshClaims["roles"]
    };
    return Response(create_access_token(identity=identity,additional_claims=additionalCLaims),200);


@application.route("/delete",methods=["POST"])
@roleCheck(role="admin")
def delete():
    email=request.json.get("email","");
    if not email:
        return jsonify({'message': 'Field email is missing.'}), 400;

    result = parseaddr(email);
    if (len(result[1]) == 0 or len(email) > 256):
        return jsonify({'message': 'Invalid email.'}), 400;


    user=User.query.filter(User.email==email).first();
    if (not user):
        return jsonify({'message': 'Unkown user.'}), 400;

    database.session.delete(user);
    database.session.commit();
    return Response(status=200);


@application.route("/", methods=["GET"])
def index():
    return "Hello world";


if (__name__=="__main__"):
    database.init_app(application);
    application.run ( debug = True, host = "0.0.0.0", port = 5002 );