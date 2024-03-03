from flask import (
    Blueprint, g, request
)

from . import errors

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
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Mime Type'}), 415
    try:
        request.data = request.json
    except Exception as e:
        print(f"Error: {str(e)}")
        return errors.malformed_body("JSON")


@api.route('/answer', methods=['GET'])
@exception_handler
def add_answer():
    data = request.data
    if "questionId" not in data:
        return errors.bad_request("questionId is required") 
    if "answer" not in data:
        return errors.bad_request("answer is required") 
    return {"data" : "added answer"}, 201

@api.route('/question', methods=['POST'], endpoint='add_question')
@exception_handler
def add_question():
    data = request.data
    if "question" not in data:
        return errors.bad_request("question is required") 
    return {"data" : "created"}, 201



@api.route('/question/<question_id>', methods=['GET'], endpoint='get_question')
@exception_handler
def get_question(question_id):
    if (question_id):
        return {"data" : f"Your question id is {question_id}"}, 201
    else:
        return {"data" : f"what is your favourite color?"}, 201

@api.route('/test', methods=['GET'])
def testing():
    from .db import get_db
    db = get_db()
    return {"data" : "ok"}, 200

