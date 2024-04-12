from flask import Blueprint, jsonify

quiz = Blueprint('quiz', __name__)


@quiz.route('/', methods=['GET'])
def example():
    data = {
        'name': 'Juan',
        'age': 30,
        'city': 'Madrid'
    }
    return jsonify(data)
