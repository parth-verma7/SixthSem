from flask import (
    Blueprint, g, request
)

from . import errors
from .db import get_db
from .validators import (
    validate_question, validate_answer
)
from bson.json_util import (
    loads, dumps
)
from bson.objectid import ObjectId

api = Blueprint('question', __name__, url_prefix='/api')

def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_code = getattr(e, "code", 500)
            print(f"Error: {str(e)}")
            return errors.server_error()
    wrapper.__name__ = func.__name__
    return wrapper

@api.before_request
@exception_handler
def jsonify_middleware():
    if not request.data:
        return;
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Mime Type'}), 415
    try:
        request.data = request.json
    except Exception as e:
        print(f"Error: {str(e)}")
        return errors.malformed_body("JSON")

# GET for frontend and LLM. POST is convenience method for admin
# use questionId in body for answer to specific question
@api.route('/answer/<user_id>', methods=['GET', 'POST'], endpoint='user_answers')
@exception_handler
def user_answers(user_id):
    db = get_db()
    answer_collection = db["answer"]
    if request.method == 'GET':
        print(request.data)
        question_id = request.data.get('questionId', None)
        query = {"userId" : user_id}
        if question_id:  query["questionId"] = question_id
        print(query)
        cursor = answer_collection.find(query)
        json_list = dumps([doc for doc in cursor])
        return json_list, 200
    else: # TODO
        data = {"userId": user_id, **request.data}
        validate_answer(data)
        if db["users"].find_one({"_id": ObjectId(user_id)})  is None:
            raise Exception("No such user")
        if db["questions"].find_one({"_id" : ObjectId(data["questionId"])}) is None:
            raise Exception("No such question")
        answer_collection.insert_one(data)
        return {"data" : "created"}, 201


# GET for frontend, LLM. POST only for admin, convenience
@api.route('/question', methods=['POST', 'GET'], endpoint='question_routes')
@exception_handler
def question():
    db = get_db()
    question_collection = db["questions"]
    if request.method == 'POST':
        data = request.data
        validate_question(data);
        result = question_collection.insert_one(data)
        return {"data" : "created"}, 201
    else:
        cursor = question_collection.find({})
        json_list = dumps([doc for doc in cursor])
        return json_list, 200

# For frontend and LLM
@api.route('/question/<question_id>', methods=['GET'], endpoint='get_specific_question')
@exception_handler
def get_specific_question(question_id):
    return {"data" : f"Your question id is {question_id}"}, 201


@api.route('/test', methods=['GET'])
def testing():
    from .db import get_db
    db = get_db()
    return {"data" : "ok"}, 200

