from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from models import db, Property, PropertyImage, Inquiry, Favorite
from utils import save_uploaded_image, delete_uploaded_image, validate_property_data, STANDARD_AMENITIES, PROPERTY_TYPES
from sqlalchemy import or_

property_bp = Blueprint('properties', __name__)

@property_bp.route('/properties')
def list_properties():
    query = Property.query

    # Search query
    q = request.args.get('q', '').strip()
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Property.title.ilike(search_pattern),
                Property.description.ilike(search_pattern),
                Property.address.ilike(search_pattern),
                Property.city.ilike(search_pattern),
                Property.state.ilike(search_pattern),
                Property.zip_code.ilike(search_pattern)
            )
        )

    # Filter: Purpose (buy / rent)
    purpose = request.args.get('purpose', '').strip().lower()
    if purpose in ['buy', 'rent']:
        query = query.filter(Property.purpose == purpose)

    # Filter: Property Type
    prop_type = request.args.get('type', '').strip()
    if prop_type and prop_type != 'All':
        query = query.filter(Property.property_type == prop_type)

    # Filter: City / Location
    city = request.args.get('city', '').strip()
    if city and city != 'All':
        query = query.filter(Property.city.ilike(f"%{city}%"))

    # Filter: Status
    status = request.args.get('status', '').strip()
    if status and status != 'All':
        query = query.filter(Property.status == status)

    # Filter: Min Price
    min_price = request.args.get('min_price', '').strip()
    if min_price:
        try:
            query = query.filter(Property.price >= float(min_price))
        except ValueError:
            pass

    # Filter: Max Price
    max_price = request.args.get('max_price', '').strip()
    if max_price:
        try:
            query = query.filter(Property.price <= float(max_price))
        except ValueError:
            pass

    # Filter: Bedrooms
    bedrooms = request.args.get('bedrooms', '').strip()
    if bedrooms and bedrooms != 'Any':
        try:
            query = query.filter(Property.bedrooms >= int(bedrooms))
        except ValueError:
            pass

    # Filter: Bathrooms
    bathrooms = request.args.get('bathrooms', '').strip()
    if bathrooms and bathrooms != 'Any':
        try:
            query = query.filter(Property.bathrooms >= float(bathrooms))
        except ValueError:
            pass

    # Filter: Amenities
    amenity_filter = request.args.get('amenity', '').strip()
    if amenity_filter:
        query = query.filter(Property.amenities.ilike(f"%{amenity_filter}%"))

    # Sorting
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'area_desc':
        query = query.order_by(Property.area_sqft.desc())
    elif sort_by == 'beds_desc':
        query = query.order_by(Property.bedrooms.desc())
    else:  # newest
        query = query.order_by(Property.created_at.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 9
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    properties = pagination.items

    # Available cities for filter dropdown
    available_cities = [r[0] for r in db.session.query(Property.city).distinct().order_by(Property.city).all()]

    # User favorite IDs if logged in
    user_fav_ids = set()
    if current_user.is_authenticated:
        user_fav_ids = {f.property_id for f in Favorite.query.filter_by(user_id=current_user.id).all()}

    return render_template(
        'properties/index.html',
        properties=properties,
        pagination=pagination,
        total_results=pagination.total,
        property_types=PROPERTY_TYPES,
        available_cities=available_cities,
        standard_amenities=STANDARD_AMENITIES,
        active_filters={
            'q': q,
            'purpose': purpose,
            'type': prop_type,
            'city': city,
            'status': status,
            'min_price': min_price,
            'max_price': max_price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'amenity': amenity_filter,
            'sort': sort_by
        },
        user_fav_ids=user_fav_ids
    )

@property_bp.route('/properties/<int:property_id>')
def show_property(property_id):
    prop = Property.query.get_or_404(property_id)
    
    # Increment view counter
    prop.views_count = (prop.views_count or 0) + 1
    db.session.commit()

    # Similar properties (same city or same property type, excluding current)
    similar_properties = Property.query.filter(
        Property.id != prop.id,
        or_(Property.city == prop.city, Property.property_type == prop.property_type)
    ).limit(3).all()

    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, property_id=prop.id).first() is not None

    return render_template(
        'properties/show.html',
        property=prop,
        similar_properties=similar_properties,
        is_favorited=is_favorited,
        standard_amenities=STANDARD_AMENITIES
    )

@property_bp.route('/properties/create', methods=['GET', 'POST'])
@login_required
def create_property():
    if request.method == 'POST':
        form_data = request.form
        errors = validate_property_data(form_data)

        if errors:
            for field, err in errors.items():
                flash(f"{err}", 'error')
            return render_template(
                'properties/create.html',
                property_types=PROPERTY_TYPES,
                standard_amenities=STANDARD_AMENITIES,
                form_data=form_data
            )

        # Collect checked amenities
        selected_amenities = request.form.getlist('amenities')

        new_prop = Property(
            title=form_data.get('title').strip(),
            description=form_data.get('description').strip(),
            price=float(form_data.get('price')),
            purpose=form_data.get('purpose', 'buy'),
            property_type=form_data.get('property_type', 'Single Family Home'),
            status=form_data.get('status', 'Available'),
            address=form_data.get('address').strip(),
            city=form_data.get('city').strip(),
            state=form_data.get('state').strip(),
            zip_code=form_data.get('zip_code').strip(),
            country=form_data.get('country', 'USA').strip(),
            bedrooms=int(form_data.get('bedrooms', 1)),
            bathrooms=float(form_data.get('bathrooms', 1)),
            area_sqft=int(form_data.get('area_sqft')),
            garages=int(form_data.get('garages', 1)),
            year_built=int(form_data.get('year_built')) if form_data.get('year_built') else None,
            featured=bool(form_data.get('featured')),
            contact_name=form_data.get('contact_name', current_user.full_name).strip(),
            contact_email=form_data.get('contact_email', current_user.email).strip(),
            contact_phone=form_data.get('contact_phone', current_user.phone or '').strip(),
            user_id=current_user.id
        )
        new_prop.set_amenities_list(selected_amenities)
        db.session.add(new_prop)
        db.session.flush()  # assign id to new_prop

        # Handle uploaded images
        uploaded_files = request.files.getlist('images')
        saved_any_image = False
        is_first = True

        for file in uploaded_files:
            if file and file.filename:
                saved_url = save_uploaded_image(file)
                if saved_url:
                    img = PropertyImage(
                        property_id=new_prop.id,
                        image_url=saved_url,
                        is_primary=is_first
                    )
                    db.session.add(img)
                    saved_any_image = True
                    is_first = False

        # If user also entered custom image URL
        custom_img_url = form_data.get('custom_image_url', '').strip()
        if custom_img_url:
            img = PropertyImage(
                property_id=new_prop.id,
                image_url=custom_img_url,
                is_primary=not saved_any_image
            )
            db.session.add(img)
            saved_any_image = True

        # Fallback default image if none provided
        if not saved_any_image:
            fallback_img = PropertyImage(
                property_id=new_prop.id,
                image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
                is_primary=True,
                caption="Main Exterior"
            )
            db.session.add(fallback_img)

        db.session.commit()
        flash('Property listing published successfully!', 'success')
        return redirect(url_for('properties.show_property', property_id=new_prop.id))

    return render_template(
        'properties/create.html',
        property_types=PROPERTY_TYPES,
        standard_amenities=STANDARD_AMENITIES,
        form_data={}
    )

@property_bp.route('/properties/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)

    # Security check: User must own the listing or be an admin
    if prop.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized. You can only edit your own listings.', 'error')
        return redirect(url_for('properties.show_property', property_id=prop.id))

    if request.method == 'POST':
        form_data = request.form
        errors = validate_property_data(form_data)

        if errors:
            for field, err in errors.items():
                flash(f"{err}", 'error')
            return render_template(
                'properties/edit.html',
                property=prop,
                property_types=PROPERTY_TYPES,
                standard_amenities=STANDARD_AMENITIES
            )

        # Update basic fields
        prop.title = form_data.get('title').strip()
        prop.description = form_data.get('description').strip()
        prop.price = float(form_data.get('price'))
        prop.purpose = form_data.get('purpose', 'buy')
        prop.property_type = form_data.get('property_type', prop.property_type)
        prop.status = form_data.get('status', prop.status)
        prop.address = form_data.get('address').strip()
        prop.city = form_data.get('city').strip()
        prop.state = form_data.get('state').strip()
        prop.zip_code = form_data.get('zip_code').strip()
        prop.country = form_data.get('country', 'USA').strip()
        prop.bedrooms = int(form_data.get('bedrooms', 1))
        prop.bathrooms = float(form_data.get('bathrooms', 1))
        prop.area_sqft = int(form_data.get('area_sqft'))
        prop.garages = int(form_data.get('garages', 1))
        prop.year_built = int(form_data.get('year_built')) if form_data.get('year_built') else None
        prop.featured = bool(form_data.get('featured'))
        prop.contact_name = (form_data.get('contact_name') or current_user.full_name).strip()
        prop.contact_email = (form_data.get('contact_email') or current_user.email).strip()
        prop.contact_phone = (form_data.get('contact_phone') or '').strip()

        # Update amenities
        selected_amenities = request.form.getlist('amenities')
        prop.set_amenities_list(selected_amenities)

        # Handle newly uploaded images
        uploaded_files = request.files.getlist('images')
        has_primary = any(img.is_primary for img in prop.images)

        for file in uploaded_files:
            if file and file.filename:
                saved_url = save_uploaded_image(file)
                if saved_url:
                    img = PropertyImage(
                        property_id=prop.id,
                        image_url=saved_url,
                        is_primary=not has_primary
                    )
                    db.session.add(img)
                    has_primary = True

        # Custom image URL addition
        custom_url = form_data.get('custom_image_url', '').strip()
        if custom_url:
            img = PropertyImage(
                property_id=prop.id,
                image_url=custom_url,
                is_primary=not has_primary
            )
            db.session.add(img)

        db.session.commit()
        flash('Property listing updated successfully!', 'success')
        return redirect(url_for('properties.show_property', property_id=prop.id))

    return render_template(
        'properties/edit.html',
        property=prop,
        property_types=PROPERTY_TYPES,
        standard_amenities=STANDARD_AMENITIES
    )

@property_bp.route('/properties/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)

    # Security check: User must own the listing or be an admin
    if prop.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized. You can only delete your own listings.', 'error')
        return redirect(url_for('properties.show_property', property_id=prop.id))

    # Clean up uploaded images from disk
    for img in prop.images:
        delete_uploaded_image(img.image_url)

    db.session.delete(prop)
    db.session.commit()
    flash(f'Listing "{prop.title}" has been permanently removed.', 'success')
    return redirect(url_for('properties.my_listings'))

@property_bp.route('/properties/<int:property_id>/image/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_property_image(property_id, image_id):
    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id and current_user.role != 'admin':
        abort(403)

    img = PropertyImage.query.filter_by(id=image_id, property_id=prop.id).first_or_404()
    
    # Do not delete if it's the only image
    if len(prop.images) <= 1:
        flash('A listing must have at least one image.', 'error')
        return redirect(url_for('properties.edit_property', property_id=prop.id))

    delete_uploaded_image(img.image_url)
    was_primary = img.is_primary
    db.session.delete(img)
    db.session.flush()

    if was_primary and prop.images:
        remaining = PropertyImage.query.filter_by(property_id=prop.id).first()
        if remaining:
            remaining.is_primary = True

    db.session.commit()
    flash('Image removed.', 'info')
    return redirect(url_for('properties.edit_property', property_id=prop.id))

@property_bp.route('/properties/<int:property_id>/image/<int:image_id>/set-primary', methods=['POST'])
@login_required
def set_primary_image(property_id, image_id):
    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id and current_user.role != 'admin':
        abort(403)

    # Reset all to False
    for img in prop.images:
        img.is_primary = (img.id == image_id)

    db.session.commit()
    flash('Primary cover photo updated.', 'success')
    return redirect(url_for('properties.edit_property', property_id=prop.id))

@property_bp.route('/my-listings')
@login_required
def my_listings():
    properties = Property.query.filter_by(user_id=current_user.id).order_by(Property.created_at.desc()).all()
    
    # Calculate stats for user's listings
    total_count = len(properties)
    available_count = sum(1 for p in properties if p.status == 'Available')
    pending_count = sum(1 for p in properties if p.status == 'Pending')
    closed_count = sum(1 for p in properties if p.status in ['Sold', 'Rented'])
    total_views = sum(p.views_count or 0 for p in properties)

    return render_template(
        'properties/my_listings.html',
        properties=properties,
        total_count=total_count,
        available_count=available_count,
        pending_count=pending_count,
        closed_count=closed_count,
        total_views=total_views
    )

@property_bp.route('/properties/<int:property_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    prop = Property.query.get_or_404(property_id)
    fav = Favorite.query.filter_by(user_id=current_user.id, property_id=prop.id).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from saved properties.'})
    else:
        new_fav = Favorite(user_id=current_user.id, property_id=prop.id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Saved to favorites!'})
