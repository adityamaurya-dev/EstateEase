# EstateEase — Luxury Real Estate Listing Platform

EstateEase is a modern, premium full-stack real estate listing application built with **Python Flask**, **SQLite (via SQLAlchemy)**, **Tailwind CSS**, and **Lucide Icons**.

Inspired by premier luxury architectural brokerages, it provides full-fledged property management (CRUD), rich gallery management, interactive mortgage calculators, real-time lead and tour inquiry handling, live search and filtering, animated KPI dashboards, and secure role-based authentication.

---

## 🌟 Key Features

### 1. Modern Design & Luxury Aesthetics
- **Color Palette**: Deep Navy (`#0B1528`), Crisp White, Warm Beige (`#FBF9F5`, `#F3EFE6`), and Champagne Gold (`#C59B27`) accents.
- **Editorial Typography**: Plus Jakarta Sans paired with serif accents for architectural luxury.
- **Micro-Interactions**: Scroll-triggered animations, card hover elevation, image zoom, animated counters, and toast notifications.
- **Mobile Responsive**: Custom navigation drawer and touch-friendly layouts.
- **Reduced-Motion Support**: Respects `@media (prefers-reduced-motion: reduce)`.

### 2. Complete Property Management (CRUD)
- **Create**: Multi-section submission form with client and server-side validation, multi-image upload with live drag-and-drop preview, and an amenities checklist.
- **Read**: Rich details view with photo switcher, specifications overview (beds, baths, sq ft, year built), amenities badges, and interactive showing requests.
- **Update**: Pre-filled edit form with granular cover photo assignment and photo deletion controls.
- **Delete**: Permanent removal of property and uploaded photos with modal confirmation safeguard.

### 3. Advanced Search, Filtering & Sorting
- **Keyword & Location**: Search across title, description, address, city, state, and zip code.
- **Purpose**: Toggle between *For Sale* (Buy) and *For Rent* (Lease).
- **Property Types**: Filter by *Luxury Villa*, *Penthouse*, *Single Family Home*, *Modern Apartment*, *Townhouse*, etc.
- **Price & Specs**: Min/max price sliders/inputs, minimum bedrooms, minimum bathrooms.
- **Sorting**: Newest listings, Price Low-to-High, Price High-to-Low, Largest Living Area, and Most Bedrooms.
- **Informative Empty States**: Clean state with a one-click filter reset.

### 4. Interactive Financials & Inquiries
- **Interactive Mortgage Calculator**: Dynamic monthly payment computation including principal, interest, property taxes, and home insurance.
- **Private Tour & Inquiry System**: Direct lead routing to the property's listing agent with immediate feedback.

### 5. Live Operations Dashboard
- **Real Database KPI Counters**: Total properties, Available, Pending escrow, Sold, Rented, and Total Inquiries.
- **Lead Management**: Real-time showing requests and contact status updates (*Pending*, *Contacted*, *Resolved*).
- **Portfolio Breakdown**: Visual asset distribution bar.

---

## 👥 Demo Accounts (One-Click Sign In)

For evaluation, demo accounts are pre-seeded in the database:

| Role | Email | Password | Features |
|---|---|---|---|
| **Luxury Agent** | `agent@estateease.com` | `password123` | Full portfolio management, edit/delete permissions, inquiry tracking |
| **Private Buyer** | `buyer@estateease.com` | `password123` | Save favorites, submit showing requests |
| **Administrator** | `admin@estateease.com` | `password123` | Global management over all listings and leads |

*Quick login buttons are also available directly on the `/login` page.*

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.14 + Flask 3.1
- **Database**: SQLite with pure-Python SQLAlchemy ORM (`estateease.db`)
- **Authentication**: Flask-Login + Werkzeug secure password hashing
- **Styling**: Tailwind CSS + Custom Design System (`static/css/main.css`)
- **Icons**: Lucide Icons CDN
- **Testing**: Python `unittest` suite (`tests/test_full_suite.py`)

---

## 🚀 Running the Application

1. **Start the Flask Development Server**:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. **Run the Test Suite**:
   ```bash
   python -m unittest tests/test_full_suite.py
   ```
