from flask import jsonify, make_response


def string_is_valid(string):
    return string is not None and string != '' and all(ch.isalnum() or ch.isspace() for ch in string)


def jsonify_response_with_cors(response_content):
    response = make_response(jsonify(response_content))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
