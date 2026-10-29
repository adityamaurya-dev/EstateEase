import os
os.environ['DISABLE_SQLALCHEMY_CEXT'] = '1'

from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(20), default='agent')  # 'agent', 'buyer', 'admin'
    agency = db.Column(db.String(120), default='EstateEase Premier Realty')
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship('Property', backref='owner', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'agency': self.agency,
            'avatar_url': self.avatar_url or f"https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
        }

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False, index=True)
    purpose = db.Column(db.String(10), nullable=False, default='buy', index=True)  # 'buy' or 'rent'
    property_type = db.Column(db.String(50), nullable=False, index=True)  # 'Single Family', 'Luxury Villa', 'Modern Apartment', 'Penthouse', 'Townhouse', 'Commercial'
    status = db.Column(db.String(20), nullable=False, default='Available', index=True)  # 'Available', 'Pending', 'Sold', 'Rented'
    
    # Location
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False, index=True)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='USA')
    
    # Specifications
    bedrooms = db.Column(db.Integer, nullable=False, default=1, index=True)
    bathrooms = db.Column(db.Float, nullable=False, default=1)
    area_sqft = db.Column(db.Integer, nullable=False, index=True)
    garages = db.Column(db.Integer, default=1)
    year_built = db.Column(db.Integer, nullable=True)
    
    # Features & Media
    amenities = db.Column(db.Text, default='[]')  # JSON array string
    featured = db.Column(db.Boolean, default=False, index=True)
    is_demo = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    
    # Contact
    contact_name = db.Column(db.String(120), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    
    # Timestamps & User
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan', order_by='PropertyImage.is_primary.desc(), PropertyImage.id.asc()')
    inquiries = db.relationship('Inquiry', backref='property', lazy=True, cascade='all, delete-orphan', order_by='Inquiry.created_at.desc()')
    favorites = db.relationship('Favorite', backref='property', lazy=True, cascade='all, delete-orphan')

    @property
    def primary_image_url(self):
        if self.images:
            for img in self.images:
                if img.is_primary:
                    return img.image_url
            return self.images[0].image_url
        return "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"

    @property
    def amenities_list(self):
        if not self.amenities:
            return []
        try:
            return json.loads(self.amenities)
        except Exception:
            return [a.strip() for a in self.amenities.split(',') if a.strip()]

    def set_amenities_list(self, items):
        if isinstance(items, list):
            self.amenities = json.dumps(items)
        else:
            self.amenities = json.dumps([])

    @property
    def price_per_sqft(self):
        if self.area_sqft and self.area_sqft > 0:
            return round(self.price / self.area_sqft, 1)
        return 0

    @property
    def formatted_price(self):
        if self.purpose == 'rent':
            return f"${self.price:,.0f}/mo"
        return f"${self.price:,.0f}"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'formatted_price': self.formatted_price,
            'purpose': self.purpose,
            'property_type': self.property_type,
            'status': self.status,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area_sqft': self.area_sqft,
            'price_per_sqft': self.price_per_sqft,
            'year_built': self.year_built,
            'garages': self.garages,
            'amenities': self.amenities_list,
            'featured': self.featured,
            'is_demo': self.is_demo,
            'primary_image': self.primary_image_url,
            'images': [img.to_dict() for img in self.images],
            'contact_name': self.contact_name or (self.owner.full_name if self.owner else ''),
            'contact_email': self.contact_email or (self.owner.email if self.owner else ''),
            'contact_phone': self.contact_phone or (self.owner.phone if self.owner else ''),
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'owner_id': self.user_id,
            'owner_name': self.owner.full_name if self.owner else 'EstateEase Agent'
        }

class PropertyImage(db.Model):
    __tablename__ = 'property_images'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    caption = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'is_primary': self.is_primary,
            'caption': self.caption
        }

class Inquiry(db.Model):
    __tablename__ = 'inquiries'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, nullable=False)
    inquiry_type = db.Column(db.String(50), default='Information Request')  # 'Tour Request', 'Information Request', 'Price Offer'
    preferred_date = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Contacted', 'Resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'property_title': self.property.title if self.property else 'Unknown Property',
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'inquiry_type': self.inquiry_type,
            'preferred_date': self.preferred_date,
            'status': self.status,
            'created_at': self.created_at.strftime('%b %d, %Y %I:%M %p')
        }

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
