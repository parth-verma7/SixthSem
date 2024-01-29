from flask import jsonify

def app_error(msg, code):
    return jsonify({"error" : msg}), code

def malformed_body(mime):
    return app_error(f"Invalid {mime}", 400) 

def bad_request(msg):
    return app_error(msg, 400)

def server_error():
    return app_error("unexpected error", 500)
