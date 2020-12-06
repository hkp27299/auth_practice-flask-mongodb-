from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import hashlib
salt = "5gz"

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'Login' # db name
app.config['MONGO_URI'] = 'mongodb+srv://HP:hp27299hp@cluster0.yleg7.mongodb.net/Login?retryWrites=true&w=majority'

mongo = PyMongo(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = mongo.db.Users #collection name
    output = []
    for i in users.find():

        output.append({"name":i["name"],"email":i["email"],"password":i['password']})
    return jsonify({"result":output})

@app.route('/auth', methods=['POST'])
def auth_user():
    users = mongo.db.Users #collection name
    email = request.json['email']
    password = request.json['password']

    q = users.find_one({"email" : email})

    if q:
        ps = password + salt
        h = hashlib.md5(ps.encode())
        if h.hexdigest() == q['password']:
            output = 'User authentication success'
        else:
            output = 'Wrong password'

    else:
        output = 'No user found'

    return jsonify({"result":output})

@app.route('/addusers', methods=['POST'])
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
        users = users.insert({'name' : name, 'email' : email,'password':h.hexdigest()})
        output = "Successfully registerd"
    return jsonify({'result' : output})

@app.route('/delusers', methods=['POST'])
def del_user():
    users = mongo.db.Users #collection name
    email = request.json['email']
    q = users.find_one({"email" : email})
    if q:
        users.delete_one({"email":email})
        output = 'User deleted'
    else:
        output = 'User not found'      
    
    return jsonify({'result' : output})


if __name__ == "__main__":
    app.run(debug = True)
