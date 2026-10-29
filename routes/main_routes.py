from flask import Blueprint, render_template
from models import Property, User, db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Featured listings
    featured_properties = Property.query.filter_by(featured=True).limit(6).all()
    if not featured_properties:
        featured_properties = Property.query.order_by(Property.created_at.desc()).limit(6).all()

    # Recent listings
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(6).all()

    # Real database statistics
    total_listings = Property.query.count()
    available_count = Property.query.filter_by(status='Available').count()
    sold_rented_count = Property.query.filter(Property.status.in_(['Sold', 'Rented'])).count()
    total_agents = User.query.filter_by(role='agent').count() or 1

    # Unique cities
    cities = [r[0] for r in db.session.query(Property.city).distinct().limit(8).all()]

    return render_template(
        'index.html',
        featured_properties=featured_properties,
        recent_properties=recent_properties,
        total_listings=total_listings,
        available_count=available_count,
        sold_rented_count=sold_rented_count,
        total_agents=total_agents,
        cities=cities
    )

@main_bp.route('/about')
def about():
    total_listings = Property.query.count()
    total_agents = User.query.filter_by(role='agent').count() or 1
    return render_template('about.html', total_listings=total_listings, total_agents=total_agents)

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

