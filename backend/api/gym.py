from flask import Blueprint, request, jsonify, current_app
from database import db
from models import GymWeightSet, GymCardioEntry, Exercise
from datetime import date
import requests as http

gym_bp = Blueprint('gym', __name__)


# --- Exercise Library ---

@gym_bp.route('/api/gym/exercises', methods=['GET'])
def get_exercises():
    """Get all saved exercises, optionally filtered by type."""
    ex_type = request.args.get('type')  # weight or cardio
    query = Exercise.query
    if ex_type:
        query = query.filter(Exercise.exercise_type == ex_type)
    exercises = query.order_by(Exercise.category, Exercise.name).all()
    return jsonify([e.to_dict() for e in exercises])


@gym_bp.route('/api/gym/exercises', methods=['POST'])
def add_exercise():
    """Add a new exercise to the library."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Exercise name is required'}), 400
    exercise_type = data.get('exercise_type', 'weight')
    # Check for duplicate
    existing = Exercise.query.filter(
        db.func.lower(Exercise.name) == name.lower(),
        Exercise.exercise_type == exercise_type
    ).first()
    if existing:
        return jsonify({'error': 'Exercise already exists'}), 409
    exercise = Exercise(
        name=name,
        category=data.get('category', '').strip() or None,
        exercise_type=exercise_type,
        youtube_url=data.get('youtube_url', '').strip() or None,
    )
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise.to_dict()), 201


@gym_bp.route('/api/gym/exercises/<int:id>', methods=['PUT'])
def update_exercise(id):
    """Update an exercise (e.g. set its YouTube URL)."""
    exercise = Exercise.query.get_or_404(id)
    data = request.get_json()
    if 'youtube_url' in data:
        exercise.youtube_url = data['youtube_url'].strip() if data['youtube_url'] else None
    if 'category' in data:
        exercise.category = data['category'].strip() or None
    db.session.commit()
    return jsonify(exercise.to_dict())


@gym_bp.route('/api/gym/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    """Remove an exercise from the library."""
    exercise = Exercise.query.get_or_404(id)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'success': True})


# --- Weight Exercises ---

@gym_bp.route('/api/gym/weight', methods=['GET'])
def get_weight_exercises():
    date_filter = request.args.get('date')
    query = GymWeightSet.query
    if date_filter:
        query = query.filter(GymWeightSet.date == date_filter)
    entries = query.order_by(
        GymWeightSet.date.desc(),
        GymWeightSet.exercise_name,
        GymWeightSet.set_number
    ).all()
    return jsonify([e.to_dict() for e in entries])


@gym_bp.route('/api/gym/weight', methods=['POST'])
def add_weight_set():
    data = request.get_json()
    entry = GymWeightSet(
        date=date.fromisoformat(data.get('date', date.today().isoformat())),
        exercise_name=data['exercise_name'],
        set_number=data.get('set_number', 1),
        reps=data['reps'],
        weight=data['weight'],
        rest_seconds=data.get('rest_seconds', 0),
        comment=data.get('comment'),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@gym_bp.route('/api/gym/weight/batch', methods=['POST'])
def add_weight_sets_batch():
    """Add multiple sets at once for an exercise."""
    data = request.get_json()
    entries = []
    for item in data.get('sets', []):
        entry = GymWeightSet(
            date=date.fromisoformat(item.get('date', date.today().isoformat())),
            exercise_name=item['exercise_name'],
            set_number=item.get('set_number', 1),
            reps=item['reps'],
            weight=item['weight'],
            rest_seconds=item.get('rest_seconds', 0),
            comment=item.get('comment'),
        )
        entries.append(entry)
        db.session.add(entry)
    db.session.commit()
    return jsonify([e.to_dict() for e in entries]), 201


@gym_bp.route('/api/gym/weight/<int:id>', methods=['PUT'])
def update_weight_set(id):
    entry = GymWeightSet.query.get_or_404(id)
    data = request.get_json()
    for field in ['exercise_name', 'set_number', 'reps', 'weight', 'rest_seconds', 'comment']:
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict())


@gym_bp.route('/api/gym/weight/<int:id>', methods=['DELETE'])
def delete_weight_set(id):
    entry = GymWeightSet.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})


@gym_bp.route('/api/gym/weight/exercises', methods=['GET'])
def get_exercise_names():
    """Get list of unique exercise names for autocomplete."""
    exercises = db.session.query(GymWeightSet.exercise_name).distinct().all()
    return jsonify([e[0] for e in exercises])


# --- Cardio ---

@gym_bp.route('/api/gym/cardio', methods=['GET'])
def get_cardio():
    date_filter = request.args.get('date')
    query = GymCardioEntry.query
    if date_filter:
        query = query.filter(GymCardioEntry.date == date_filter)
    entries = query.order_by(GymCardioEntry.date.desc(), GymCardioEntry.exercise_name).all()
    return jsonify([e.to_dict() for e in entries])


@gym_bp.route('/api/gym/cardio', methods=['POST'])
def add_cardio():
    data = request.get_json()
    entry = GymCardioEntry(
        date=date.fromisoformat(data.get('date', date.today().isoformat())),
        exercise_name=data['exercise_name'],
        distance=data.get('distance'),
        duration_minutes=data.get('duration_minutes'),
        calories=data.get('calories'),
        comment=data.get('comment'),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@gym_bp.route('/api/gym/cardio/<int:id>', methods=['PUT'])
def update_cardio(id):
    entry = GymCardioEntry.query.get_or_404(id)
    data = request.get_json()
    for field in ['exercise_name', 'distance', 'duration_minutes', 'calories', 'comment']:
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict())


@gym_bp.route('/api/gym/cardio/<int:id>', methods=['DELETE'])
def delete_cardio(id):
    entry = GymCardioEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})


@gym_bp.route('/api/gym/cardio/exercises', methods=['GET'])
def get_cardio_exercise_names():
    """Get list of unique cardio exercise names."""
    exercises = db.session.query(GymCardioEntry.exercise_name).distinct().all()
    return jsonify([e[0] for e in exercises])


@gym_bp.route('/api/gym/youtube-search', methods=['GET'])
def youtube_search():
    """Search YouTube for exercise tutorial videos."""
    api_key = current_app.config.get('YOUTUBE_API_KEY')
    if not api_key:
        return jsonify({'error': 'YouTube API key not configured — add YOUTUBE_API_KEY to .env'}), 503

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400

    try:
        resp = http.get(
            'https://www.googleapis.com/youtube/v3/search',
            params={
                'part': 'snippet',
                'type': 'video',
                'maxResults': 6,
                'q': query,
                'key': api_key,
                'relevanceLanguage': 'en',
            },
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get('items', [])
        videos = [
            {
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'url': f'https://www.youtube.com/watch?v={item["id"]["videoId"]}',
            }
            for item in items
        ]
        return jsonify(videos)
    except http.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502
