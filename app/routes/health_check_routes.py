from flask import Blueprint, jsonify

health_check_api = Blueprint('health_check_api', __name__)


@health_check_api.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200
