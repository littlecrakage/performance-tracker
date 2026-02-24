from datetime import datetime, date
from database import db


class CS2Match(db.Model):
    """Individual CS2 match data from Leetify."""
    __tablename__ = 'cs2_matches'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(100), unique=True, nullable=False)
    finished_at = db.Column(db.DateTime)
    data_source = db.Column(db.String(50))
    map_name = db.Column(db.String(50))
    outcome = db.Column(db.String(10))
    score_us = db.Column(db.Integer, default=0)
    score_them = db.Column(db.Integer, default=0)
    has_banned_player = db.Column(db.Boolean, default=False)
    # Core stats
    kills = db.Column(db.Integer, default=0)
    deaths = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    kd_ratio = db.Column(db.Float, default=0)
    adr = db.Column(db.Float, default=0)
    hs_kills = db.Column(db.Integer, default=0)
    hs_pct = db.Column(db.Float, default=0)
    mvps = db.Column(db.Integer, default=0)
    total_damage = db.Column(db.Integer, default=0)
    # Leetify ratings
    leetify_rating = db.Column(db.Float)
    ct_leetify_rating = db.Column(db.Float)
    t_leetify_rating = db.Column(db.Float)
    # Accuracy
    accuracy_head = db.Column(db.Float)
    accuracy_enemy_spotted = db.Column(db.Float)
    spray_accuracy = db.Column(db.Float)
    # Positioning
    preaim = db.Column(db.Float)
    reaction_time = db.Column(db.Float)
    # Rounds
    rounds_count = db.Column(db.Integer, default=0)
    rounds_won = db.Column(db.Integer, default=0)
    # Multi-kills
    multi2k = db.Column(db.Integer, default=0)
    multi3k = db.Column(db.Integer, default=0)
    multi4k = db.Column(db.Integer, default=0)
    multi5k = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'data_source': self.data_source,
            'map_name': self.map_name,
            'outcome': self.outcome,
            'score_us': self.score_us,
            'score_them': self.score_them,
            'has_banned_player': self.has_banned_player,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'kd_ratio': self.kd_ratio,
            'adr': self.adr,
            'hs_kills': self.hs_kills,
            'hs_pct': self.hs_pct,
            'mvps': self.mvps,
            'total_damage': self.total_damage,
            'leetify_rating': self.leetify_rating,
            'ct_leetify_rating': self.ct_leetify_rating,
            't_leetify_rating': self.t_leetify_rating,
            'accuracy_head': self.accuracy_head,
            'accuracy_enemy_spotted': self.accuracy_enemy_spotted,
            'spray_accuracy': self.spray_accuracy,
            'preaim': self.preaim,
            'reaction_time': self.reaction_time,
            'rounds_count': self.rounds_count,
            'rounds_won': self.rounds_won,
            'multi2k': self.multi2k,
            'multi3k': self.multi3k,
            'multi4k': self.multi4k,
            'multi5k': self.multi5k,
        }


class CS2Comment(db.Model):
    __tablename__ = 'cs2_comments'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'comment': self.comment,
        }


class CS2Training(db.Model):
    """CS2 training session log (deathmatch, utility, prefire, etc.)."""
    __tablename__ = 'cs2_training'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    training_type = db.Column(db.String(50), nullable=False)  # deathmatch, utility, prefire, aim, retakes, etc.
    duration_minutes = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'training_type': self.training_type,
            'duration_minutes': self.duration_minutes,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }


class Exercise(db.Model):
    """Saved exercise library for autocomplete."""
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Chest, Back, Legs, Shoulders, Arms, Core, Cardio, etc.
    exercise_type = db.Column(db.String(10), default='weight')  # weight or cardio
    youtube_url = db.Column(db.String(500))  # Optional YouTube tutorial URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('name', 'exercise_type', name='uq_exercise_name_type'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'exercise_type': self.exercise_type,
            'youtube_url': self.youtube_url,
            'created_at': self.created_at.isoformat(),
        }


class GymWeightSet(db.Model):
    __tablename__ = 'gym_weight_sets'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, default=1)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rest_seconds = db.Column(db.Integer, default=0)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'exercise_name': self.exercise_name,
            'set_number': self.set_number,
            'reps': self.reps,
            'weight': self.weight,
            'rest_seconds': self.rest_seconds,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }


class GymCardioEntry(db.Model):
    __tablename__ = 'gym_cardio_entries'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    exercise_name = db.Column(db.String(100), nullable=False)
    distance = db.Column(db.Float)
    duration_minutes = db.Column(db.Float)
    calories = db.Column(db.Float)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'exercise_name': self.exercise_name,
            'distance': self.distance,
            'duration_minutes': self.duration_minutes,
            'calories': self.calories,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }


class BodyWeight(db.Model):
    __tablename__ = 'body_weight'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today, unique=True)
    weight = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'weight': self.weight,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }


class MentalHealth(db.Model):
    __tablename__ = 'mental_health'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    mood = db.Column(db.Integer)
    stress = db.Column(db.Integer)
    sleep_quality = db.Column(db.Integer)
    energy = db.Column(db.Integer)
    anxiety = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'mood': self.mood,
            'stress': self.stress,
            'sleep_quality': self.sleep_quality,
            'energy': self.energy,
            'anxiety': self.anxiety,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }
