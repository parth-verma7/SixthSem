from flask import (
    Blueprint, g, request
)

from . import errors

api = Blueprint('question', __name__, url_prefix='/api')

@api.before_request
def jsonify_middleware():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Mime Type'}), 415
    try:
        request.data = request.json
    except Exception as e:
        return errors.malformed_body("JSON")


@api.route('/question', methods=['POST'])
def add_question():
    data = request.data
    if "questionId" not in data:
        return errors.bad_request("questionId is required") 
    if "answer" not in data:
        return errors.bad_request("answer is required") 
    return {"data" : "ok"}, 200
