import json
from models import db, User, Property, PropertyImage, Inquiry
from werkzeug.security import generate_password_hash

def seed_database():
    print("Checking database records...")
    # Check if demo user already exists
    if User.query.filter_by(email='agent@estateease.com').first():
        print("Database already contains demo seed data. Skipping seed.")
        return

    print("Creating demo users...")
    agent_user = User(
        username='agent_elena',
        email='agent@estateease.com',
        full_name='Elena Vance',
        phone='+1 (555) 328-9842',
        role='agent',
        agency='EstateEase Premier Luxury Group',
        bio='Senior luxury property advisor with over 12 years of experience specializing in architectural residences, waterfront villas, and prime urban penthouses.',
        avatar_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80'
    )
    agent_user.set_password('password123')
    db.session.add(agent_user)

    buyer_user = User(
        username='buyer_marcus',
        email='buyer@estateease.com',
        full_name='Marcus Sterling',
        phone='+1 (555) 782-1144',
        role='buyer',
        agency='Independent Investor',
        bio='Private real estate investor seeking premium residential assets.',
        avatar_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80'
    )
    buyer_user.set_password('password123')
    db.session.add(buyer_user)

    admin_user = User(
        username='admin_alex',
        email='admin@estateease.com',
        full_name='Alexander Hayes',
        phone='+1 (555) 901-4455',
        role='admin',
        agency='EstateEase HQ Operations',
        bio='Platform Administrator and Portfolio Director.',
        avatar_url='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80'
    )
    admin_user.set_password('password123')
    db.session.add(admin_user)

    db.session.flush()

    print("Creating realistic demo properties...")
    demo_properties = [
        {
            "title": "The Azure Modernist Glass Villa",
            "description": "[DEMO LISTING] An architectural tour de force situated along prime waterfront, this contemporary villa features floor-to-ceiling motorized Fleetwood glass pocket walls, seamless indoor-outdoor living, an infinity-edge saltwater pool, custom Boffi Italian kitchen, and a private dock for yacht mooring. Designed for both intimate luxury living and large-scale entertaining.",
            "price": 6450000,
            "purpose": "buy",
            "property_type": "Luxury Villa",
            "status": "Available",
            "address": "428 Ocean Boulevard",
            "city": "Miami Beach",
            "state": "FL",
            "zip_code": "33139",
            "bedrooms": 5,
            "bathrooms": 6.5,
            "area_sqft": 7200,
            "garages": 3,
            "year_built": 2023,
            "featured": True,
            "is_demo": True,
            "amenities": ["Swimming Pool", "Waterfront / Panoramic View", "Smart Home Automation", "Private Gym", "24/7 Security", "Wine Cellar", "EV Charging Station", "Landscaped Garden"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Villa Exterior & Infinity Pool"},
                {"url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Grand Living Room"},
                {"url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Chef's Kitchen"},
                {"url": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Primary Suite Sanctuary"}
            ]
        },
        {
            "title": "Skyline Heights Horizon Penthouse",
            "description": "[DEMO LISTING] Soaring 54 stories above Manhattan, this duplex penthouse offers 360-degree panoramic skyline and river vistas. Boasting 14-foot ceilings, solid European white oak herringbone flooring, a dramatic sculptural floating staircase, private elevator entry, and a 1,200 sq ft wrap-around sky terrace.",
            "price": 8900000,
            "purpose": "buy",
            "property_type": "Penthouse",
            "status": "Available",
            "address": "157 Central Park South, PH-54",
            "city": "New York",
            "state": "NY",
            "zip_code": "10019",
            "bedrooms": 4,
            "bathrooms": 4.5,
            "area_sqft": 5400,
            "garages": 2,
            "year_built": 2022,
            "featured": True,
            "is_demo": True,
            "amenities": ["Private Elevator", "Private Balcony / Terrace", "Smart Home Automation", "24/7 Security", "Spa & Sauna", "Home Theater", "Custom Walk-in Closets"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Penthouse Living Lounge"},
                {"url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Dining & Skyline Vistas"},
                {"url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Exterior Sunset View"}
            ]
        },
        {
            "title": "The Beverly Crest Mid-Century Sanctuary",
            "description": "[DEMO LISTING] Nestled behind private gated walls in prestigious Beverly Hills, this mid-century modern triumph was comprehensively renovated with zero compromises. Features radiant limestone terraces, terrazzo floors, a 60-foot zero-edge pool, private screening room, and secluded tranquil Zen gardens.",
            "price": 12500000,
            "purpose": "buy",
            "property_type": "Single Family Home",
            "status": "Available",
            "address": "1044 Loma Vista Drive",
            "city": "Beverly Hills",
            "state": "CA",
            "zip_code": "90210",
            "bedrooms": 6,
            "bathrooms": 7.0,
            "area_sqft": 8600,
            "garages": 4,
            "year_built": 2021,
            "featured": True,
            "is_demo": True,
            "amenities": ["Swimming Pool", "Home Theater", "Wine Cellar", "Private Gym", "Landscaped Garden", "Smart Home Automation", "EV Charging Station"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Estate Residence Front"},
                {"url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Open Concept Architecture"},
                {"url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Designer Bathroom Spa"}
            ]
        },
        {
            "title": "Aspen Timberline Alpine Chalet",
            "description": "[DEMO LISTING] Direct ski-in / ski-out luxury retreat boasting reclaimed timber beams, hand-carved stone fireplaces, heated flagstone motor court, outdoor Jacuzzi spa overlooking the mountains, dry sauna, and wine room. Winter wonderland living paired with world-class summer hiking.",
            "price": 7800000,
            "purpose": "buy",
            "property_type": "Luxury Villa",
            "status": "Pending",
            "address": "780 Red Mountain Road",
            "city": "Aspen",
            "state": "CO",
            "zip_code": "81611",
            "bedrooms": 5,
            "bathrooms": 5.5,
            "area_sqft": 6100,
            "garages": 3,
            "year_built": 2020,
            "featured": False,
            "is_demo": True,
            "amenities": ["Spa & Sauna", "Wine Cellar", "Private Balcony / Terrace", "Central Climate Control", "Custom Walk-in Closets"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Mountain Chalet Exterior"},
                {"url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Cozy Great Room with Fireplace"}
            ]
        },
        {
            "title": "SoHo Cast-Iron Designer Loft",
            "description": "[DEMO LISTING] Located in the heart of SoHo's historic cast-iron district, this voluminous loft boasts 13-foot Corinthian tin ceilings, original exposed brick, massive industrial windows, a minimalist Poliform kitchen, and museum-quality art display walls. Available for long-term lease.",
            "price": 14500,
            "purpose": "rent",
            "property_type": "Modern Apartment",
            "status": "Available",
            "address": "112 Prince Street, Apt 3B",
            "city": "New York",
            "state": "NY",
            "zip_code": "10012",
            "bedrooms": 2,
            "bathrooms": 2.5,
            "area_sqft": 2850,
            "garages": 0,
            "year_built": 2019,
            "featured": True,
            "is_demo": True,
            "amenities": ["Private Elevator", "Central Climate Control", "Chef's Kitchen", "24/7 Security", "Smart Home Automation"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1502005229762-ee1b2da97ba5?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Loft Great Room"},
                {"url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Kitchen & Island"}
            ]
        },
        {
            "title": "Barton Springs Hill Country Haven",
            "description": "[DEMO LISTING] A warm modern Texas hill country estate offering privacy, lush native landscaping, solar energy integration, an outdoor summer kitchen, private pool, and quick access to downtown Austin and Lady Bird Lake.",
            "price": 2450000,
            "purpose": "buy",
            "property_type": "Single Family Home",
            "status": "Available",
            "address": "3200 Westlake Drive",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78746",
            "bedrooms": 4,
            "bathrooms": 4.0,
            "area_sqft": 4350,
            "garages": 3,
            "year_built": 2022,
            "featured": False,
            "is_demo": True,
            "amenities": ["Swimming Pool", "Landscaped Garden", "EV Charging Station", "Smart Home Automation", "Central Climate Control"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Modern Front Elevation"},
                {"url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Rear Patio & Pool"}
            ]
        },
        {
            "title": "Pacific Heights Bay View Residence",
            "description": "[DEMO LISTING] Overlooking the Golden Gate Bridge and San Francisco Bay, this renovated Victorian offers classic period millwork married with ultra-modern Scandinavian interiors, a private roof garden, temperature-controlled wine room, and private garage.",
            "price": 5750000,
            "purpose": "buy",
            "property_type": "Townhouse",
            "status": "Sold",
            "address": "2640 Broadway Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94115",
            "bedrooms": 4,
            "bathrooms": 3.5,
            "area_sqft": 4100,
            "garages": 2,
            "year_built": 2021,
            "featured": False,
            "is_demo": True,
            "amenities": ["Waterfront / Panoramic View", "Private Balcony / Terrace", "Wine Cellar", "Multi-Car Garage"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Victorian Exterior"},
                {"url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80", "is_primary": False, "caption": "Minimalist Interior"}
            ]
        },
        {
            "title": "Emerald Bay Contemporary Townhome",
            "description": "[DEMO LISTING] Elegant urban retreat located in a quiet enclave near Lake Washington. Features a private rooftop terrace with outdoor fire pit, polished concrete floors, smart lighting, and high-efficiency geothermal heating.",
            "price": 6800,
            "purpose": "rent",
            "property_type": "Townhouse",
            "status": "Rented",
            "address": "812 Lakeview Avenue",
            "city": "Seattle",
            "state": "WA",
            "zip_code": "98102",
            "bedrooms": 3,
            "bathrooms": 2.5,
            "area_sqft": 2400,
            "garages": 1,
            "year_built": 2022,
            "featured": False,
            "is_demo": True,
            "amenities": ["Private Balcony / Terrace", "Smart Home Automation", "Central Climate Control"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1200&q=80", "is_primary": True, "caption": "Contemporary Townhome Facade"}
            ]
        }
    ]

    for pdata in demo_properties:
        prop = Property(
            title=pdata["title"],
            description=pdata["description"],
            price=pdata["price"],
            purpose=pdata["purpose"],
            property_type=pdata["property_type"],
            status=pdata["status"],
            address=pdata["address"],
            city=pdata["city"],
            state=pdata["state"],
            zip_code=pdata["zip_code"],
            bedrooms=pdata["bedrooms"],
            bathrooms=pdata["bathrooms"],
            area_sqft=pdata["area_sqft"],
            garages=pdata["garages"],
            year_built=pdata["year_built"],
            featured=pdata["featured"],
            is_demo=pdata["is_demo"],
            contact_name=agent_user.full_name,
            contact_email=agent_user.email,
            contact_phone=agent_user.phone,
            user_id=agent_user.id
        )
        prop.set_amenities_list(pdata["amenities"])
        db.session.add(prop)
        db.session.flush()

        for img_info in pdata["images"]:
            pimg = PropertyImage(
                property_id=prop.id,
                image_url=img_info["url"],
                is_primary=img_info["is_primary"],
                caption=img_info.get("caption", "")
            )
            db.session.add(pimg)

    # Add a sample inquiry to make dashboard inquiries realistic
    sample_prop = Property.query.first()
    if sample_prop:
        inq1 = Inquiry(
            property_id=sample_prop.id,
            name="Jonathan Davies",
            email="jdavies@example.com",
            phone="+1 (555) 438-1920",
            message="We are interested in viewing this property this Saturday afternoon. Are private tours currently available?",
            inquiry_type="Tour Request",
            preferred_date="This Saturday at 2:00 PM",
            status="Pending"
        )
        inq2 = Inquiry(
            property_id=sample_prop.id,
            name="Sophia Lin",
            email="sophia.lin@luxuryinvest.com",
            phone="+1 (555) 882-9901",
            message="Could you provide the HOA disclosure package and recent property tax records?",
            inquiry_type="Information Request",
            status="Contacted"
        )
        db.session.add(inq1)
        db.session.add(inq2)

    db.session.commit()
    print("Seeding complete! Successfully inserted users, properties, and inquiries.")

