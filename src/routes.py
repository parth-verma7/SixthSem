import json

from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, g, request
from transformers import AutoModelForCausalLM, AutoTokenizer

from . import errors
from .db import get_db
from .openapi import get_openai_client
from .pinecone_ops import ask_question, fetch_from_db
from .validators import validate_answer, validate_question

api = Blueprint("question", __name__, url_prefix="/api")


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
        return
    if request.headers["Content-Type"] != "application/json":
        return jsonify({"error": "Unsupported Mime Type"}), 415
    try:
        request.data = request.json
    except Exception as e:
        print(f"Error: {str(e)}")
        return errors.malformed_body("JSON")


# use questionId in body for answer to specific question
@api.route("/answer/<user_id>", methods=["GET", "POST"], endpoint="user_answers")
@exception_handler
def user_answers(user_id):
    db = get_db()
    answer_collection = db["answer"]
    if request.method == "GET":
        question_id = None
        if (request.data):
            question_id = request.data.get("questionId", None)
        query = {"userId": ObjectId(user_id)}
        if question_id:
            query["questionId"] = ObjectId(question_id)
        pipeline = [
            {"$match": query},
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "questionId",
                    "foreignField": "_id",
                    "as": "questionData",
                }
            },
        ]
        cursor = answer_collection.aggregate(pipeline)
        json_list = dumps([doc for doc in cursor])
        return json_list, 200
    else:
        if not isinstance(request.data, list):
            return errors.bad_request(
                "data must be a list of answer object obeying answer schema"
            )

        data = [{"userId": user_id, **answer} for answer in request.data]
        try:
            all(validate_answer(answer) for answer in data)
        except Exception as e:
            raise e

        if db["users"].find_one({"_id": ObjectId(user_id)}) is None:
            raise Exception("No such user")

        data = list(
            map(
                lambda answer: {
                    **answer,
                    "questionId": ObjectId(answer["questionId"]),
                    "userId": ObjectId(answer["userId"]),
                },
                data,
            )
        )
        questionIds = [answer["questionId"] for answer in data]
        cnt = db["questions"].count_documents({"_id": {"$in": questionIds}})
        if cnt != len(questionIds):
            return errors.bad_request(
                "Either some questions do not exists or there are answers to duplicate questions in the request data"
            )

        answer_collection.insert_many(data)
        return {"data": "created"}, 201


@api.route(
    "/pinecone_store/<user_id>", methods=["GET", "POST"], endpoint="store_to_pinecone"
)
@exception_handler
def pinecone_store(user_id):
    db = get_db()
    answer_collection = db["answer"]
    print("User ID is", user_id)
    if request.method == "GET":
        question_id = None
        if (request.data):
            question_id = request.data.get("questionId", None)
        query = {"userId": ObjectId(user_id)}
        if question_id:
            query["questionId"] = ObjectId(question_id)
        pipeline = [
            {"$match": query},
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "questionId",
                    "foreignField": "_id",
                    "as": "questionData",
                }
            },
        ]
        cursor = answer_collection.aggregate(pipeline)
        json_list = dumps([doc for doc in cursor])
        ## start
        json_list = json.loads(json_list)
        res = []
        for response in json_list:
            answer = response["text"]
            question = response["questionData"][0]["title"]
            d = {}
            d["question"] = question
            d["answer"] = answer
            res.append(d)
        # print(res)
        return fetch_from_db(res, user_id)


@api.route(
    "/pinecone_response/<user_id>",
    methods=["GET", "POST"],
    endpoint="generate_pinecone_response",
)
@exception_handler
def pinecone_response(user_id):
    db = get_db()
    if request.method == "GET":
        cursor = db["response"].find({"userId": user_id})
        json_list = dumps([doc for doc in cursor])
        return json_list, 200
    else:
        data = request.get_json()
        query = data.get("query")
        res = ask_question(user_id, query)
        print("The res is------------------------")
        print(res)

        assist_prompt = f"""
            Give me an article that I can post on my social media.
            Don't give me any warnings. 
            Give me such response that can attract public. 
            Also while generating response take some inspiration from this content and keep this content as your base.
            The content is -{res}
        """

        user_prompt = f"""
            {query}
        """

        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": assist_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b", token='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')
        # model = AutoModelForCausalLM.from_pretrained("google/gemma-2b", token='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')

        # user_input = user_prompt
        # input_ids = tokenizer.encode(user_input, return_tensors="pt")
        # output = model.generate(input_ids, max_length=100, num_beams=5, no_repeat_ngram_size=2, top_k=50, top_p=0.95, temperature=0.7)
        # generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        final_response = response.choices[0].message.content
        print("The final response is ----------------------------------------------------------------")
        print(final_response)
        response_document = {
            "response": final_response,
            "userId": user_id,
            "prompt": query,
        }
        db["response"].insert_one(response_document)
        return final_response, 200


# GET for frontend, LLM. POST only for admin, convenience
@api.route("/question", methods=["POST", "GET"], endpoint="question_routes")
@exception_handler
def question():
    db = get_db()
    question_collection = db["questions"]
    if request.method == "POST":
        data = request.data
        validate_question(data)
        result = question_collection.insert_one(data)
        return {"data": "created"}, 201
    else:
        cursor = question_collection.find({})
        json_list = dumps([doc for doc in cursor])
        return json_list, 200


@api.route("/test", methods=["GET"])
def testing():
    from .db import get_db

    db = get_db()
    return {"data": "ok"}, 200
