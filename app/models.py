"""Data models."""
from . import db

import json

class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = "sit-raman-user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=False, unique=True, nullable=False)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    bio = db.Column(db.Text, index=False, unique=False, nullable=True)
    admin = db.Column(db.Boolean, index=False, unique=False, nullable=False)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Spectrum(db.Model):
    """Data model for user spectrum."""

    __tablename__ = "sit-raman-spectrum"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=False, unique=False, nullable=False)
    cas = db.Column(db.String(80), index=False, unique=False, nullable=True)
    created = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    data = db.Column(db.Text, index=False, unique=False, nullable=True)
    description = db.Column(db.Text, index=False, unique=False, nullable=True)
    ideal_chemistry = db.Column(db.Text, index=False, unique=False, nullable=True)
    measured_chemistry = db.Column(db.Text, index=False, unique=False, nullable=True)
    orientation = db.Column(db.Text, index=False, unique=False, nullable=True)
    status = db.Column(db.Text, index=False, unique=False, nullable=True)
    pin_id = db.Column(db.Text, index=False, unique=False, nullable=True)
    source = db.Column(db.Text, index=False, unique=False, nullable=True)
    locality = db.Column(db.Text, index=False, unique=False, nullable=True)
    # rruffid = db.Column(db.Text, index=False, unique=False, nullable=True)
    # owner = db.Column(db.Text, index=False, unique=False, nullable=True)
    # url = db.Column(db.Text, index=False, unique=False, nullable=True)
    
    def __repr__(self):
        # return "<Spectrum {} {}>".format(self.name, self.id)
        return json.dumps({'name': self.name, 'cas': self.cas, 'data': self.data})
    
    
class Bio_Spectrum(Spectrum):
    """Data model for user bio spectrum."""
    
    __tablename__ = "sit-raman-bio-spectrum"
    
    
    

