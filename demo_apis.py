from flask import request, jsonify

import containers
from engine.application import app

# Initialize service (assuming repositories are set up)

profiling_service = containers.Clients.user_static_response_service()
user_profile_data_service = containers.Clients.user_profile_data_service()
question_answer_service = containers.Clients.question_answer_service()

@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.json
    # Assuming your repository has a method like 'add_question'
    new_question = profiling_service.add_question(data)
    if new_question == True:
        return jsonify({"message": "Question added successfully"}), 201
    else:
        return jsonify({"error": "Failed to add question"}), 500


@app.route('/get_user_response', methods=['GET'])
def get_questions():
    user_id = request.args.get('user_id')
    user_questions = profiling_service.get_user_response(user_id)
    return jsonify([user_question.as_dict() for user_question in user_questions])


@app.route('/submit_response', methods=['POST'])
def submit_response():
    data = request.json
    response_submitted = profiling_service.submit_user_response(data)
    if response_submitted:
        return jsonify({"message": "Response submitted successfully"}), 200
    else:
        return jsonify({"error": "Failed to submit user response"}), 500


@app.route('/onboard_user', methods=['POST'])
def onboard_user():
    # Extract LinkedIn profile ID from the request
    linkedin_profile_id = request.json.get('linkedin_profile_id')

    # Check if LinkedIn profile ID is provided
    if not linkedin_profile_id:
        return jsonify({'error': 'LinkedIn profile ID is required'}), 400

    success, user_id = user_profile_data_service.onboard_user(linkedin_profile_id)

    if success:
        return jsonify({'message': 'User onboarded successfully', 'data': {'user_id': user_id}}), 200
    else:
        return jsonify({'error': 'Error onboarding user'}), 500


@app.route('/get_user_profile_data', methods=['GET'])
def get_user_profile_data():
    try:
        user_id = request.args.get('user_id')
        user_profile_data = user_profile_data_service.fetch_user_profile_data(user_id)
        if user_profile_data:
            return jsonify({'user_profile_data': user_profile_data.to_dict()}), 200
        else:
            return jsonify({'message': 'No user profile data found for user'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/user/completion-status', methods=['GET'])
def check_completion_status():
    user_id = request.args.get('user_id')
    status = profiling_service.check_profile_completion_status(user_id)
    return jsonify({"completion_status": status}), 200

@app.route('/user/pinecone', methods=['POST'])
def store_user_responses_to_pinecone():
    data=request.json
    user_id = data["user_id"]
    responses = profiling_service.get_responses_for_user(user_id)
    res=[]
    for response in responses:
        a={
            'user_id': response.user_id,
            'question_id': response.question_id,
            'response': response.response,
        }
        res.append(a)
    response=question_answer_service.fetch_from_db(res, "profile-agent")
    return jsonify(response)

@app.route("/user/pinecone/response", methods=["POST"])
def rag_response():
    data=request.json
    query=data["query"]
    user_id = data["user_id"]
    # print(query, user_id)   
    response = question_answer_service.ask_question(user_id, query)
    return jsonify(response)