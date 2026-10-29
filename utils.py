import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

STANDARD_AMENITIES = [
    {"id": "pool", "label": "Swimming Pool", "icon": "waves"},
    {"id": "gym", "label": "Private Gym", "icon": "dumbbell"},
    {"id": "smart_home", "label": "Smart Home Automation", "icon": "cpu"},
    {"id": "security", "label": "24/7 Security", "icon": "shield-check"},
    {"id": "balcony", "label": "Private Balcony / Terrace", "icon": "sun"},
    {"id": "central_ac", "label": "Central Climate Control", "icon": "wind"},
    {"id": "garden", "label": "Landscaped Garden", "icon": "trees"},
    {"id": "spa", "label": "Spa & Sauna", "icon": "sparkles"},
    {"id": "ev_charger", "label": "EV Charging Station", "icon": "zap"},
    {"id": "wine_cellar", "label": "Wine Cellar", "icon": "wine"},
    {"id": "theater", "label": "Home Theater", "icon": "film"},
    {"id": "chef_kitchen", "label": "Chef's Kitchen", "icon": "utensils"},
    {"id": "waterfront", "label": "Waterfront / Panoramic View", "icon": "compass"},
    {"id": "elevator", "label": "Private Elevator", "icon": "arrow-up-down"},
    {"id": "garage", "label": "Multi-Car Garage", "icon": "car"},
    {"id": "walk_in_closet", "label": "Custom Walk-in Closets", "icon": "hanger"}
]

PROPERTY_TYPES = [
    "Single Family Home",
    "Luxury Villa",
    "Modern Apartment",
    "Penthouse",
    "Townhouse",
    "Condominium",
    "Commercial"
]

def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_image(file_storage):
    """Saves an uploaded image file securely and returns its relative web path."""
    if not file_storage or not file_storage.filename:
        return None
        
    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    unique_prefix = uuid.uuid4().hex[:12]
    unique_filename = f"{unique_prefix}_{filename}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(file_path)
    
    # Return path suitable for web serving
    return f"/static/uploads/properties/{unique_filename}"

def delete_uploaded_image(image_url):
    """Deletes an image from the filesystem if it's a locally uploaded file."""
    if not image_url or not image_url.startswith('/static/uploads/properties/'):
        return False
        
    filename = os.path.basename(image_url)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False
    return False

def validate_property_data(data):
    """Validates property input data and returns errors dict."""
    errors = {}
    
    title = data.get('title', '').strip()
    if not title:
        errors['title'] = 'Property title is required.'
    elif len(title) < 5:
        errors['title'] = 'Title must be at least 5 characters long.'

    try:
        price = float(data.get('price', 0))
        if price <= 0:
            errors['price'] = 'Price must be a positive number.'
    except (ValueError, TypeError):
        errors['price'] = 'Please enter a valid numeric price.'

    try:
        area_sqft = int(data.get('area_sqft', 0))
        if area_sqft < 50:
            errors['area_sqft'] = 'Area must be at least 50 sq ft.'
    except (ValueError, TypeError):
        errors['area_sqft'] = 'Please enter a valid whole number for area.'

    try:
        bedrooms = int(data.get('bedrooms', 0))
        if bedrooms < 0:
            errors['bedrooms'] = 'Bedrooms cannot be negative.'
    except (ValueError, TypeError):
        errors['bedrooms'] = 'Please enter a valid number of bedrooms.'

    try:
        bathrooms = float(data.get('bathrooms', 0))
        if bathrooms < 0:
            errors['bathrooms'] = 'Bathrooms cannot be negative.'
    except (ValueError, TypeError):
        errors['bathrooms'] = 'Please enter a valid number of bathrooms.'

    address = data.get('address', '').strip()
    if not address:
        errors['address'] = 'Street address is required.'

    city = data.get('city', '').strip()
    if not city:
        errors['city'] = 'City is required.'

    state = data.get('state', '').strip()
    if not state:
        errors['state'] = 'State is required.'

    zip_code = data.get('zip_code', '').strip()
    if not zip_code:
        errors['zip_code'] = 'Zip code is required.'

    description = data.get('description', '').strip()
    if not description or len(description) < 20:
        errors['description'] = 'Description must be at least 20 characters.'

    return errors

