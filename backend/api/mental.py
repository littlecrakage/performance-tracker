from flask import Blueprint, request, jsonify
from database import db
from models import MentalHealth
from datetime import date

mental_bp = Blueprint('mental', __name__)


@mental_bp.route('/api/mental', methods=['GET'])
def get_entries():
    entries = MentalHealth.query.order_by(MentalHealth.date.desc()).all()
    return jsonify([e.to_dict() for e in entries])


@mental_bp.route('/api/mental', methods=['POST'])
def add_entry():
    data = request.get_json()
    entry = MentalHealth(
        date=date.fromisoformat(data.get('date', date.today().isoformat())),
        mood=data.get('mood'),
        stress=data.get('stress'),
        sleep_quality=data.get('sleep_quality'),
        energy=data.get('energy'),
        anxiety=data.get('anxiety'),
        notes=data.get('notes'),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@mental_bp.route('/api/mental/<int:id>', methods=['PUT'])
def update_entry(id):
    entry = MentalHealth.query.get_or_404(id)
    data = request.get_json()
    for field in ['mood', 'stress', 'sleep_quality', 'energy', 'anxiety', 'notes']:
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict())


@mental_bp.route('/api/mental/<int:id>', methods=['DELETE'])
def delete_entry(id):
    entry = MentalHealth.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})
