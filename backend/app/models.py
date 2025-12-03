from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB

class TransitNode(db.Model):
    __tablename__ = 'transit_nodes'
    id = db.Column(db.Integer, primary_key=True)
    osm_id = db.Column(db.String, index=True)
    type = db.Column(db.String)  # bus_stop, subway_entrance, station
    name = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class Business(db.Model):
    __tablename__ = 'businesses'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    osm_id = db.Column(db.BigInteger, index=True, nullable=False)
    name = db.Column(db.String, nullable=True)
    category = db.Column(db.String, nullable=False)  # amenity, shop, office, other
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    raw_tags = db.Column(JSONB, nullable=True)  # Store all tags as JSON
