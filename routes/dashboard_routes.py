from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Property, Inquiry, User
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_home():
    # Base query for listings: admin sees all, agents see their own (or all if specified)
    # The requirement says:
    # "Create a modern dashboard displaying: Total properties, Available properties, Pending properties, Sold properties, Rented properties, Recent listings..."
    # If the user is admin or agent, let's show both aggregate system metrics and their personal listings!
    
    # Live database queries
    total_properties = Property.query.count()
    available_properties = Property.query.filter_by(status='Available').count()
    pending_properties = Property.query.filter_by(status='Pending').count()
    sold_properties = Property.query.filter_by(status='Sold').count()
    rented_properties = Property.query.filter_by(status='Rented').count()
    
    # Average price query
    avg_price_result = db.session.query(func.avg(Property.price)).filter_by(purpose='buy').scalar()
    avg_price = round(avg_price_result, 0) if avg_price_result else 0

    # User's own counts
    user_properties_count = Property.query.filter_by(user_id=current_user.id).count()
    
    # Recent listings (show recent properties)
    recent_listings = Property.query.order_by(Property.created_at.desc()).limit(8).all()
    
    # Inquiries: for properties owned by this user or all if admin
    if current_user.role == 'admin':
        inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(10).all()
        total_inquiries = Inquiry.query.count()
    else:
        inquiries = Inquiry.query.join(Property).filter(Property.user_id == current_user.id).order_by(Inquiry.created_at.desc()).limit(10).all()
        total_inquiries = Inquiry.query.join(Property).filter(Property.user_id == current_user.id).count()

    # Breakdown by property type
    type_distribution = db.session.query(
        Property.property_type, func.count(Property.id)
    ).group_by(Property.property_type).all()

    return render_template(
        'dashboard/index.html',
        total_properties=total_properties,
        available_properties=available_properties,
        pending_properties=pending_properties,
        sold_properties=sold_properties,
        rented_properties=rented_properties,
        avg_price=avg_price,
        user_properties_count=user_properties_count,
        recent_listings=recent_listings,
        inquiries=inquiries,
        total_inquiries=total_inquiries,
        type_distribution=type_distribution
    )

@dashboard_bp.route('/dashboard/property/<int:property_id>/status', methods=['POST'])
@login_required
def update_status(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    new_status = request.form.get('status')
    if new_status in ['Available', 'Pending', 'Sold', 'Rented']:
        prop.status = new_status
        db.session.commit()
        flash(f'Status for "{prop.title}" updated to {new_status}.', 'success')
    return redirect(request.referrer or url_for('dashboard.dashboard_home'))

@dashboard_bp.route('/dashboard/inquiry/<int:inquiry_id>/status', methods=['POST'])
@login_required
def update_inquiry_status(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    # verify ownership
    if inquiry.property.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    new_status = request.form.get('status')
    if new_status in ['Pending', 'Contacted', 'Resolved']:
        inquiry.status = new_status
        db.session.commit()
        flash(f'Inquiry from {inquiry.name} marked as {new_status}.', 'success')
    return redirect(request.referrer or url_for('dashboard.dashboard_home'))

