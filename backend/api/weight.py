from flask import Blueprint, request, jsonify
from database import db
from models import BodyWeight
from datetime import date

weight_bp = Blueprint('weight', __name__)


@weight_bp.route('/api/weight', methods=['GET'])
def get_weights():
    entries = BodyWeight.query.order_by(BodyWeight.date.desc()).all()
    return jsonify([e.to_dict() for e in entries])


@weight_bp.route('/api/weight', methods=['POST'])
def add_weight():
    data = request.get_json()
    entry_date = date.fromisoformat(data.get('date', date.today().isoformat()))

    # Update if entry exists for this date
    existing = BodyWeight.query.filter_by(date=entry_date).first()
    if existing:
        existing.weight = data['weight']
        existing.comment = data.get('comment')
        db.session.commit()
        return jsonify(existing.to_dict())

    entry = BodyWeight(
        date=entry_date,
        weight=data['weight'],
        comment=data.get('comment'),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@weight_bp.route('/api/weight/<int:id>', methods=['DELETE'])
def delete_weight(id):
    entry = BodyWeight.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})
