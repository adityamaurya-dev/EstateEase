import os
import io
import unittest
from app import create_app
from models import db, User, Property, PropertyImage, Inquiry, Favorite

class EstateEaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def login_demo_agent(self):
        return self.client.get('/demo-login/agent', follow_redirects=True)

    def login_demo_buyer(self):
        return self.client.get('/demo-login/buyer', follow_redirects=True)

    def test_01_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EstateEase', response.data)
        self.assertIn(b'Curated Architectural Living', response.data)
        self.assertIn(b'Featured Residences', response.data)
        print("[PASS] Test 01: Home page loaded successfully with brand and featured properties.")

    def test_02_explore_properties_and_filtering(self):
        # 1. Base list
        response = self.client.get('/properties')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Luxury Properties Portfolio', response.data)

        # 2. Filter by search query
        response_search = self.client.get('/properties?q=Miami')
        self.assertEqual(response_search.status_code, 200)
        self.assertIn(b'Miami Beach', response_search.data)

        # 3. Filter by purpose
        response_rent = self.client.get('/properties?purpose=rent')
        self.assertEqual(response_rent.status_code, 200)
        self.assertIn(b'For Rent', response_rent.data)

        # 4. Filter by property type
        response_villa = self.client.get('/properties?type=Luxury+Villa')
        self.assertEqual(response_villa.status_code, 200)
        self.assertIn(b'Luxury Villa', response_villa.data)

        # 5. Filter by price range
        response_price = self.client.get('/properties?min_price=1000000&max_price=8000000')
        self.assertEqual(response_price.status_code, 200)

        # 6. Sorting
        response_sort_asc = self.client.get('/properties?sort=price_asc')
        self.assertEqual(response_sort_asc.status_code, 200)

        response_sort_desc = self.client.get('/properties?sort=price_desc')
        self.assertEqual(response_sort_desc.status_code, 200)

        # 7. Empty state test
        response_empty = self.client.get('/properties?q=NonExistentPropertyQuery999XYZ')
        self.assertEqual(response_empty.status_code, 200)
        self.assertIn(b'No Matching Properties Found', response_empty.data)
        print("[PASS] Test 02: Explore properties, search, filters, sorting, and empty state verified.")

    def test_03_property_details(self):
        with self.app.app_context():
            prop = Property.query.first()
            prop_id = prop.id
            init_views = prop.views_count or 0

        response = self.client.get(f'/properties/{prop_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Estimated Payment Calculator', response.data)
        self.assertIn(b'Schedule a Private Showing', response.data)

        # Verify views count incremented
        with self.app.app_context():
            updated_prop = db.session.get(Property, prop_id)
            self.assertGreater(updated_prop.views_count, init_views)
        print("[PASS] Test 03: Property details page and view tracking verified.")

    def test_04_auth_and_session(self):
        # 1. Login demo agent
        res = self.login_demo_agent()
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Elena Vance', res.data)

        # 2. Access dashboard
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'Executive Operations Dashboard', res_dash.data)

        # 3. Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b'You have been signed out safely', res_logout.data)

        # 4. Standard Register
        test_email = 'test_new_user@example.com'
        with self.app.app_context():
            existing = User.query.filter_by(email=test_email).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()

        res_reg = self.client.post('/register', data={
            'full_name': 'Test Investor',
            'username': 'test_investor',
            'email': test_email,
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'buyer'
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        print("[PASS] Test 04: Authentication, login, logout, and registration verified.")

    def test_05_property_crud_lifecycle(self):
        # 1. Sign in as agent
        self.login_demo_agent()

        # 2. CREATE Property
        new_title = 'The Grand Obsidian Modernist Pavilion'
        res_create = self.client.post('/properties/create', data={
            'title': new_title,
            'description': 'A stunning modern architectural statement crafted in black granite and glass.',
            'price': '4750000',
            'purpose': 'buy',
            'property_type': 'Luxury Villa',
            'status': 'Available',
            'address': '108 Ocean Crest Path',
            'city': 'Laguna Beach',
            'state': 'CA',
            'zip_code': '92651',
            'country': 'USA',
            'bedrooms': '4',
            'bathrooms': '4.5',
            'area_sqft': '5600',
            'garages': '3',
            'year_built': '2024',
            'amenities': ['Swimming Pool', 'Smart Home Automation', 'Wine Cellar'],
            'custom_image_url': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
            'contact_name': 'Elena Vance',
            'contact_email': 'agent@estateease.com',
            'contact_phone': '+1 555-328-9842'
        }, follow_redirects=True)
        self.assertEqual(res_create.status_code, 200)
        self.assertIn(b'Property listing published successfully', res_create.data)

        with self.app.app_context():
            created_prop = Property.query.filter_by(title=new_title).first()
            self.assertIsNotNone(created_prop)
            prop_id = created_prop.id
            self.assertEqual(created_prop.price, 4750000)

        # 3. EDIT Property
        res_edit = self.client.post(f'/properties/{prop_id}/edit', data={
            'title': new_title + ' (Updated)',
            'description': 'Updated description with even more custom luxury appointments and infinity edge views.',
            'price': '4950000',
            'purpose': 'buy',
            'property_type': 'Luxury Villa',
            'status': 'Pending',
            'address': '108 Ocean Crest Path',
            'city': 'Laguna Beach',
            'state': 'CA',
            'zip_code': '92651',
            'country': 'USA',
            'bedrooms': '5',
            'bathrooms': '5.0',
            'area_sqft': '5800',
            'garages': '3',
            'year_built': '2024',
            'amenities': ['Swimming Pool', 'Spa & Sauna']
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn(b'Property listing updated successfully', res_edit.data)

        # 4. SECURITY CHECK: Unauthorized user cannot edit or delete
        self.client.get('/logout')
        self.login_demo_buyer()  # Marcus Sterling (different user)
        res_unauth_edit = self.client.post(f'/properties/{prop_id}/edit', data={
            'title': 'Hacked Title',
            'description': 'Unauthorized edit attempt.',
            'price': '100',
            'area_sqft': '100',
            'address': 'Fake',
            'city': 'Fake',
            'state': 'Fake',
            'zip_code': '00000'
        }, follow_redirects=True)
        self.assertIn(b'Unauthorized. You can only edit your own listings', res_unauth_edit.data)

        # 5. DELETE Property as owner
        self.client.get('/logout')
        self.login_demo_agent()
        res_delete = self.client.post(f'/properties/{prop_id}/delete', follow_redirects=True)
        self.assertEqual(res_delete.status_code, 200)
        self.assertIn(b'has been permanently removed', res_delete.data)

        with self.app.app_context():
            deleted_check = db.session.get(Property, prop_id)
            self.assertIsNone(deleted_check)
        print("[PASS] Test 05: Property CRUD lifecycle and authorization security verified.")

    def test_06_inquiry_submission_and_dashboard_management(self):
        with self.app.app_context():
            target_prop = Property.query.first()
            prop_id = target_prop.id

        # Submit Inquiry via JSON API
        res_inquiry = self.client.post(f'/api/properties/{prop_id}/inquiry', data={
            'name': 'Lady Eleanor Kensington',
            'email': 'eleanor@kensington-holdings.co.uk',
            'phone': '+44 20 7946 0991',
            'message': 'We wish to arrange a private confidential walkthrough next Tuesday.',
            'inquiry_type': 'Tour Request',
            'preferred_date': 'Tuesday 11:00 AM'
        })
        self.assertEqual(res_inquiry.status_code, 200)
        data = res_inquiry.get_json()
        self.assertTrue(data['success'])

        # Sign in and check dashboard
        self.login_demo_agent()
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'Lady Eleanor Kensington', res_dash.data)
        # 6. Test Multiple File Image Upload
        image_data = io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
        res_upload = self.client.post('/properties/create', data={
            'title': 'Laguna Beach Coastal Modernist Retreat',
            'description': 'Spectacular ocean views with private beach pathway and glass elevator.',
            'price': '5200000',
            'purpose': 'buy',
            'property_type': 'Single Family Home',
            'status': 'Available',
            'address': '221 Ocean Way',
            'city': 'Laguna Beach',
            'state': 'CA',
            'zip_code': '92651',
            'bedrooms': '4',
            'bathrooms': '4.5',
            'area_sqft': '4900',
            'images': (image_data, 'exterior_ocean.png')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res_upload.status_code, 200)

        with self.app.app_context():
            uploaded_prop = Property.query.filter_by(title='Laguna Beach Coastal Modernist Retreat').first()
            self.assertIsNotNone(uploaded_prop)
            self.assertGreater(len(uploaded_prop.images), 0)
            self.assertTrue(uploaded_prop.images[0].image_url.startswith('/static/uploads/properties/'))

            # Clean up
            db.session.delete(uploaded_prop)
            db.session.commit()

        print("[PASS] Test 07: Real binary image upload and local storage verified.")

if __name__ == '__main__':
    unittest.main()
