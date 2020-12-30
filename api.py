from flask import Flask, jsonify, request, session, flash
from flask_pymongo import PyMongo
import hashlib
from functools import wraps
import jwt
import datetime

salt = "5gz"

app = Flask(__name__)


app.config['MONGO_DBNAME'] = 'Login' # db name
app.config['MONGO_URI'] = 'mongodb+srv://HP:hp27299hp@cluster0.yleg7.mongodb.net/Login?retryWrites=true&w=majority'

mongo = PyMongo(app)

app.config['SECRET_KEY'] = '0#pp4RT'
def check_token(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message':'Missing token'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
        except Exception as e:
            print(e)
            return jsonify({'message':'Invalid token'}), 403
        return func(*args,**kwargs)
    return wrapped



@app.route('/getusers', methods=['GET'])
def get_users():
    users = mongo.db.Users #collection name
    output = []
    for i in users.find():

        output.append({"name":i["name"],"email":i["email"],"password":i['password']})
    return jsonify({"result":output})

@app.route('/login', methods=['POST'])

def auth_user():
    users = mongo.db.Users #collection name
    email = request.json['email']
    password = request.json['password']

    q = users.find_one({"email" : email})

    if q:
        ps = password + salt
        h = hashlib.md5(ps.encode())
        if h.hexdigest() == q['password']:
            session['logged_in'] = True
            output = 'User authentication success'
            token = jwt.encode({
            'user' : email,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds = 60)
            },
            app.config['SECRET_KEY'],algorithm="HS256")


        else:
            output = 'Wrong password'

    else:
        output = 'No user found'

    return jsonify({"result":output,"token" : token})

@app.route('/signup', methods=['POST'])
def add_user():

    users = mongo.db.Users #collection name
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    q = users.find_one({"email" : email})

    if q:
        output = "User already registerd"
    else:
        ps = password + salt
        h = hashlib.md5(ps.encode())
        users = users.insert_one({'name' : name, 'email' : email,'password':h.hexdigest()})
        output = "Successfully registerd"
    return jsonify({'result' : output})

@app.route('/deluser', methods=['POST'])
@check_token
def del_user():
    users = mongo.db.Users #collection name
    email = request.json['email']
    users.delete_one({"email":email})
    return jsonify({'result' : 'User deleted'})


if __name__ == "__main__":
    app.run(debug = True)
