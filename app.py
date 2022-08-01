# flask packages
from flask import Flask, render_template, jsonify, request, make_response
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.json_util import dumps, loads
import bcrypt
import jwt
import datetime
from functools import wraps
from bson.objectid import ObjectId





# Setting up the Flask app
default_config = {'MONGODB_SETTINGS': {
    'db': 'plannit_db',
    'host': 'localhost',
    'port': 27017}}

CONNECTION_STRING = "*******************************************************************************************************"

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = CONNECTION_STRING
app.config['SECRET_KEY'] = 'jahsfkjjgsadsahdfj'
mongo = PyMongo(app)




# Token checker
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})
        except Exception as e:
            print("In Token checker, " + e)
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorator




@app.route('/')
def homepage():
    return jsonify({"message": "What\'s up, this is the Plannit team."})




# All about Businesses
@app.route('/explore/<float:longitude>/<float:latitude>', methods=['GET'])
# no need token
def explore(current_user, longitude, latitude):
    bus = mongo.db.businesses.find({'latitude': {'$gte': latitude - 0.05, '$lte': latitude - 0.05},
                                  'longitude': {'$gte': longitude - 0.05, '$lte': longitude + 0.05}}).limit(10)
    return dumps(bus)

#retrieve 10 BEST businesses for each following category: Food, Arts & Entertainment, Nightlife, Hotels & Travel
@app.route('/get_business/<string:category>', methods=['GET'])
# no need token
def retrieve(category):
    data = mongo.db.businesses.find({"categories": {"$regex": category}}).limit(10)
    return dumps(data)

@app.route('/detailed-business/<string:business_id>', methods=['GET'])
# no need token
def get_detailed_business(business_id):
    foundB = mongo.db.businesses.find_one({'_id': ObjectId(str(business_id))})
    return dumps(foundB)




# All about Users
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    findUser = mongo.db.users.find_one({'username': username})
    if findUser:
        return jsonify({'error': 'Username already existed!'})
    password = data['password']
    email = data['email']
    findUser = mongo.db.users.find_one({'email': email})
    if findUser:
        return jsonify({'error': 'Email is already used for another account!'})
    phone = data['phone']
    hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(6))
    try:
        mongo.db.users.insert_one({
            'username': username,
            'password': hash,
            'email': email,
            'phone': phone,
            'planning_since': datetime.datetime.today(),
            'friends': [],
            'rating_average': 0,
            'review_count': 0,
            'public_plan_count': 0
        })
        return jsonify({'message': 'signup successfully'})
    except:
        return jsonify({'error': 'signup failed'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password'].encode('utf-8')

    findUser = mongo.db.users.find_one({'email': email})
    if not findUser:
        return jsonify({'error': 'Email not existed!'})
    if bcrypt.checkpw(password, findUser['password'].encode('utf-8')):
        print('hello')
        token = jwt.encode(
            {'user_id': str(findUser['_id'])}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('utf-8')})
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/get-user-info', methods=['GET'])
@token_required
def get_user_info(current_user):
    userF = mongo.db.users.find_one({'_id': current_user['_id']})
    return dumps(userF)




# All about Plans
@app.route('/get_public_plan', methods=['GET'])
@token_required
def get_public_plan(current_user):
    data = mongo.db.plans.find({'isPublic': True}).sort('clap_count', -1).limit(10)
    return dumps(data)

@app.route('/get-invited-plan', methods=['GET'])
@token_required
def get_invited_plan(current_user):
    data = mongo.db.plans.find({'collaborators': {'$all': [str(current_user['_id'])]}}).sort('createdTime', -1)
    return dumps(data)

@app.route('/make-plan', methods=['POST'])
@token_required
def make_plan(current_user):
    data = request.get_json()
    # print(data)
    # print(current_user)
    name = data['name']
    isPublic = data['isPublic']
    hasCollab = data['hasCollab']
    #duration = data['duration']   comment out for testing
    contents = data['contents']
    collaborators = data['collaborators']
    try:
        mongo.db.plans.insert_one({
            'name': name,
            'isPublic': isPublic,
            'hasCollab': hasCollab,
            #'duration': duration,  comment out for testing
            'contents': contents,
            'collaborators': collaborators,  # change to plural
            'creator_id': current_user['_id'],
            'creator_name': current_user['username']
        })
        return jsonify({'message': 'Plan created successfully'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Creation failed'})

@app.route('/update-plan', methods=['POST'])
def update_plan():
    data = request.get_json()
    planId = data['planId']
    plan = data['plan']

    try:
        mongo.db.plans.update({'_id': ObjectId(str(planId))}, {'$set': plan})
        return jsonify({'message': 'Plan updated successfully'})
    except:
        return jsonify({'error': 'Update plan failed'})

@app.route('/get-my-plan', methods=['GET'])
@token_required
def get_my_plan(current_user):
    plans = mongo.db.plans.find({'creator_id': current_user['_id']})
    return dumps(plans)

@app.route('/save_plan', methods=['POST'])
@token_required
def save_plan(current_user):   # currently not needing
    data = request.get_json()
    plan_id = data['plan_id']
    planF = mongo.db.plans.find_one({'_id': plan_id})
    if not planF:
        return jsonify({'error': 'Plan not existed'})
    name = planF['name']
    duration = planF['duration']
    contents = planF['contents']
    try:
        mongo.db.plans.insert_one({
            'name': name,
            'duration': duration,
            'contents': contents,
            'creator': current_user['_id'],
            'collaborator': []
        })
        return jsonify({'message': 'Plan saved'})
    except:
        return jsonify({'error': 'Saving failed'})

@app.route('/delete-plan/<string:planId>', methods=['DELETE'])
@token_required
def delete_plan(current_user, planId):
    plan = mongo.db.plans.find_one({'_id': ObjectId(str(planId))})
    if plan:
        if plan['creator_id'] == current_user['_id']:
            try:
                mongo.db.plans.remove({'_id': ObjectId(str(planId))})
                return jsonify({'message': 'Plan deleted successfully'})
            except:
                return jsonify({'error': 'Deleting plan failed'})
        else:
            return jsonify({'error': 'You do not have the permission to do this action'})
    else:
        return jsonify({'error': 'Plan not found'})




# All about Reviews
@app.route('/review', methods=['PUT'])
@token_required
def review(current_user):
    data = request.get_json()
    bus_id = data['business_id']
    bus = mongo.db.businesses.find_one({'_id': bus_id})
    if not bus:
        return jsonify({'error': 'Business not found'})
    try:
        mongo.db.businesses.update({'_id': bus_id},
                                 {'$push':
                                      {'reviews':
                                           {
                                               'reviewer': current_user['_id'],
                                               'text': data['text'],
                                               'rating': data['rating'],
                                                #'pictures': data['pictures']
                                           }
                                      }
                                 })
        return jsonify({'message': 'Your review has been added'})
    except:
        return jsonify({'error': 'Review failed'})

@app.route('/make-review', methods=['POST'])
@token_required
def make_review(current_user):
    data = request.get_json()
    business = data['business']
    rating = data['rating']
    text = data['text']
    try:
        mongo.db.reviews.insert_one({
            'business': business,
            'reviewer_id': current_user['_id'],
            'reviewer_name': current_user['username'],
            'rating': rating,
            'text': text,
            'review_at': datetime.datetime.today(),
            'useful': 0,
            'funny': 0,
            'excellent': 0,
        })
        return jsonify({'message': 'Review created successfully'})
    except:
        return jsonify({'error': 'Creation failed'})

@app.route('/get-business-review/<string:businessId>', methods=['GET'])
def get_business_review(businessId):
    reviews = mongo.db.reviews.find({'business': ObjectId(str(businessId))})
    return dumps(reviews)




# All about interactions
@app.route('/clap', methods=['PUT'])
@token_required
def clap():
    data = request.get_json()
    plan_id = data['plan_id']
    planF = mongo.db.plans.find_one({'_id': plan_id})
    if not planF:
        return jsonify({'error': 'Plan not existed'})
    try:
        mongo.db.plans.update({'_id': plan_id},
                             {'$set': {'clap_count': planF['clap_count'] + 1}})
        return jsonify({'message': 'Clapped'})
    except:
        return jsonify({'error': 'Action failed'})

@app.route('/add-friend', methods=['PUT'])
@token_required
def add_friend(current_user):
    data = request.get_json()
    friend_id = data['friend_id']
    try:
        mongo.db.users.update({'_id': current_user['_id']}, {'$push': {'friends': friend_id}})
        mongo.db.users.update({'_id': friend_id}, {'$push': {'friends': current_user['_id']}})
        return jsonify({'message': 'Added'})
    except:
        return jsonify({'error': 'Adding failed'})

@app.route('/get-friends', methods=['GET'])
@token_required
def get_friends(current_user):
    userF = mongo.db.users.find_one({'_id': current_user['_id']})
    friend_Ids = userF['friends']
    friends = []

    for friend_id in friend_Ids:
        friend = mongo.db.users.find_one({'_id': friend_id})
        friends.append(friend)

    return dumps(friends)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1313, debug=True)
