from flask import Blueprint, request, jsonify
from models import db, Property, Inquiry, Favorite
from flask_login import current_user
from sqlalchemy import or_

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/properties')
def api_properties():
    query = Property.query

    q = request.args.get('q', '').strip()
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Property.title.ilike(search_pattern),
                Property.description.ilike(search_pattern),
                Property.address.ilike(search_pattern),
                Property.city.ilike(search_pattern),
                Property.state.ilike(search_pattern)
            )
        )

    purpose = request.args.get('purpose', '').strip().lower()
    if purpose in ['buy', 'rent']:
        query = query.filter(Property.purpose == purpose)

    prop_type = request.args.get('type', '').strip()
    if prop_type and prop_type != 'All':
        query = query.filter(Property.property_type == prop_type)

    city = request.args.get('city', '').strip()
    if city and city != 'All':
        query = query.filter(Property.city.ilike(f"%{city}%"))

    status = request.args.get('status', '').strip()
    if status and status != 'All':
        query = query.filter(Property.status == status)

    min_price = request.args.get('min_price', '').strip()
    if min_price:
        try:
            query = query.filter(Property.price >= float(min_price))
        except ValueError:
            pass

    max_price = request.args.get('max_price', '').strip()
    if max_price:
        try:
            query = query.filter(Property.price <= float(max_price))
        except ValueError:
            pass

    bedrooms = request.args.get('bedrooms', '').strip()
    if bedrooms and bedrooms != 'Any':
        try:
            query = query.filter(Property.bedrooms >= int(bedrooms))
        except ValueError:
            pass

    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'area_desc':
        query = query.order_by(Property.area_sqft.desc())
    else:
        query = query.order_by(Property.created_at.desc())

    limit = request.args.get('limit', 20, type=int)
    results = query.limit(limit).all()

    return jsonify({
        'count': len(results),
        'properties': [p.to_dict() for p in results]
    })

@api_bp.route('/properties/<int:property_id>/inquiry', methods=['POST'])
def submit_inquiry(property_id):
    prop = Property.query.get_or_404(property_id)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()
    inquiry_type = request.form.get('inquiry_type', 'Information Request')
    preferred_date = request.form.get('preferred_date', '').strip()

    if not name or not email or not phone or not message:
        return jsonify({
            'success': False,
            'message': 'Please fill out all required fields (Name, Email, Phone, Message).'
        }), 400

    new_inquiry = Inquiry(
        property_id=prop.id,
        name=name,
        email=email,
        phone=phone,
        message=message,
        inquiry_type=inquiry_type,
        preferred_date=preferred_date or None
    )
    db.session.add(new_inquiry)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Thank you, {name}! Your inquiry has been sent to the listing agent. They will reach out shortly.'
    })

