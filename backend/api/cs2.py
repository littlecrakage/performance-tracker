from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from database import db
from models import CS2Match, CS2Comment, CS2Training
from api.games.leetify import LeetifyAPI

cs2_bp = Blueprint('cs2', __name__)


def get_leetify_api():
    api_key = current_app.config.get('LEETIFY_API_KEY')
    steam_id = current_app.config.get('STEAM_ID')
    if not api_key or not steam_id:
        return None
    return LeetifyAPI(api_key, steam_id)


@cs2_bp.route('/api/cs2/sync', methods=['POST'])
def sync_stats():
    """Pull latest matches from Leetify and upsert into DB."""
    leetify = get_leetify_api()
    if not leetify:
        return jsonify({'error': 'Leetify API not configured. Set LEETIFY_API_KEY and STEAM_ID in .env'}), 400

    matches_raw = leetify.get_match_history()
    if matches_raw is None:
        return jsonify({'error': 'Failed to fetch matches from Leetify API'}), 502

    new_count = 0
    updated_count = 0
    for match_data in matches_raw:
        parsed = leetify.parse_match(match_data)
        if not parsed or not parsed.get('game_id'):
            continue

        existing = CS2Match.query.filter_by(game_id=parsed['game_id']).first()
        if existing:
            # Update existing match
            for key, val in parsed.items():
                if key != 'game_id' and val is not None:
                    if key == 'finished_at':
                        val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                    setattr(existing, key, val)
            updated_count += 1
        else:
            # Create new match
            finished = None
            if parsed.get('finished_at'):
                finished = datetime.fromisoformat(parsed['finished_at'].replace('Z', '+00:00'))
            match = CS2Match(
                game_id=parsed['game_id'],
                finished_at=finished,
                data_source=parsed.get('data_source'),
                map_name=parsed.get('map_name'),
                outcome=parsed.get('outcome'),
                score_us=parsed.get('score_us', 0),
                score_them=parsed.get('score_them', 0),
                has_banned_player=parsed.get('has_banned_player', False),
                kills=parsed.get('kills', 0),
                deaths=parsed.get('deaths', 0),
                assists=parsed.get('assists', 0),
                kd_ratio=parsed.get('kd_ratio', 0),
                adr=parsed.get('adr', 0),
                hs_kills=parsed.get('hs_kills', 0),
                hs_pct=parsed.get('hs_pct', 0),
                mvps=parsed.get('mvps', 0),
                total_damage=parsed.get('total_damage', 0),
                leetify_rating=parsed.get('leetify_rating'),
                ct_leetify_rating=parsed.get('ct_leetify_rating'),
                t_leetify_rating=parsed.get('t_leetify_rating'),
                accuracy_head=parsed.get('accuracy_head'),
                accuracy_enemy_spotted=parsed.get('accuracy_enemy_spotted'),
                spray_accuracy=parsed.get('spray_accuracy'),
                preaim=parsed.get('preaim'),
                reaction_time=parsed.get('reaction_time'),
                rounds_count=parsed.get('rounds_count', 0),
                rounds_won=parsed.get('rounds_won', 0),
                multi2k=parsed.get('multi2k', 0),
                multi3k=parsed.get('multi3k', 0),
                multi4k=parsed.get('multi4k', 0),
                multi5k=parsed.get('multi5k', 0),
            )
            db.session.add(match)
            new_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'new_matches': new_count,
        'updated_matches': updated_count,
        'total_fetched': len(matches_raw),
    })


@cs2_bp.route('/api/cs2/matches', methods=['GET'])
def get_matches():
    """Get all stored matches, newest first."""
    matches = CS2Match.query.order_by(CS2Match.finished_at.desc()).all()
    return jsonify([m.to_dict() for m in matches])


@cs2_bp.route('/api/cs2/matches/<int:id>', methods=['DELETE'])
def delete_match(id):
    match = CS2Match.query.get_or_404(id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({'success': True})


@cs2_bp.route('/api/cs2/profile', methods=['GET'])
def get_profile():
    """Get live profile from Leetify (ratings, ranks, stats)."""
    leetify = get_leetify_api()
    if not leetify:
        return jsonify({'error': 'Leetify API not configured'}), 400

    raw = leetify.get_profile()
    if not raw:
        return jsonify({'error': 'Failed to fetch profile from Leetify'}), 502

    profile = leetify.parse_profile(raw)
    return jsonify(profile)


@cs2_bp.route('/api/cs2/comments', methods=['GET'])
def get_comments():
    comments = CS2Comment.query.order_by(CS2Comment.timestamp.desc()).all()
    return jsonify([c.to_dict() for c in comments])


@cs2_bp.route('/api/cs2/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    comment = CS2Comment(comment=data.get('comment', ''))
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@cs2_bp.route('/api/cs2/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    comment = CS2Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True})


# ── CS2 Training ────────────────────────────────────

@cs2_bp.route('/api/cs2/training', methods=['GET'])
def get_training():
    entries = CS2Training.query.order_by(CS2Training.date.desc(), CS2Training.created_at.desc()).all()
    return jsonify([t.to_dict() for t in entries])


@cs2_bp.route('/api/cs2/training', methods=['POST'])
def add_training():
    data = request.get_json()
    training_type = data.get('training_type', '').strip()
    if not training_type:
        return jsonify({'error': 'training_type is required'}), 400

    entry = CS2Training(
        date=date.fromisoformat(data['date']) if data.get('date') else date.today(),
        training_type=training_type,
        duration_minutes=data.get('duration_minutes'),
        comment=data.get('comment', '').strip() or None,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@cs2_bp.route('/api/cs2/training/<int:id>', methods=['DELETE'])
def delete_training(id):
    entry = CS2Training.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})
