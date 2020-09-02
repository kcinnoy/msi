from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    metrics = db.relationship('Metric', backref='creator', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
                followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), index=True)
    service_element_name = db.Column(db.String(120), index=True)
    service_level_detail = db.Column(db.Text,index=False)
    target = db.Column(db.Integer, index=True)
    service_provider_steward_1 = db.Column(db.String(120), index=True)
    metric_name = db.Column(db.String(120), index=True)
    metric_description = db.Column(db.Text,index=False )
    metric_rationale = db.Column(db.Text, index=False)
    metric_value_display_format = db.Column(db.String(120), index=False)
    threshold_target = db.Column(db.Integer, index=False)
    threshold_target_rationale = db.Column(db.String(500), index=False)
    threshold_target_direction = db.Column(db.String(10), index=False)
    threshold_trigger = db.Column(db.Integer, index=False)
    threshold_trigger_rationale = db.Column(db.String(500), index=False)
    threshold_trigger_direction = db.Column(db.String(10), index=False)
    data_source = db.Column(db.String(120), index=True)
    data_update_frequency = db.Column(db.String(120), index=True)
    metric_owner_primary = db.Column(db.String(120), index=True)
    vantage_control_id = db.Column(db.String(120), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(
        self, 
        service_name, 
        service_element_name,
        service_level_detail, 
        target,  
        service_provider_steward_1,  
        metric_name,  
        metric_description,  
        metric_rationale,  
        metric_value_display_format,  
        threshold_target,  
        threshold_target_rationale,  
        threshold_target_direction,  
        threshold_trigger,  
        threshold_trigger_rationale,  
        threshold_trigger_direction,  
        data_source,  
        data_update_frequency,  
        metric_owner_primary, 
        vantage_control_id):
        self.service_name = service_name
        self.service_element_name = service_element_name
        self.service_level_detail = service_level_detail
        self.target = target  
        self.service_provider_steward_1 = service_provider_steward_1  
        self.metric_name = metric_name
        self.metric_description = metric_description
        self.metric_rationale  = metric_rationale
        self.metric_value_display_format =  metric_value_display_format
        self.threshold_target = threshold_target
        self.threshold_target_rationale = threshold_target_rationale
        self.threshold_target_direction = threshold_target_direction
        self.threshold_trigger = threshold_trigger 
        self.threshold_trigger_rationale = threshold_trigger_rationale  
        self.threshold_trigger_direction = threshold_trigger_direction  
        self.data_source = data_source  
        self.data_update_frequency = data_update_frequency  
        self.metric_owner_primary = metric_owner_primary 
        self.vantage_control_id = vantage_control_id

    def __repr__(self):
        return '<Metric {}>'.format(self.service_name)