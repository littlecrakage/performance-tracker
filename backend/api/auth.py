from flask import Blueprint, request, jsonify, session, current_app

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify_pin():
    data = request.get_json()
    pin = data.get('pin', '')
    correct_pin = current_app.config['PIN']

    if str(pin) == str(correct_pin):
        session['authenticated'] = True
        session.permanent = True
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Invalid PIN'}), 401


@auth_bp.route('/api/auth/check', methods=['GET'])
def check_auth():
    if session.get('authenticated'):
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('authenticated', None)
    return jsonify({'success': True})
