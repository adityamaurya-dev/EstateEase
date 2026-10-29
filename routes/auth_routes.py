from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_home'))

    if request.method == 'POST':
        email_or_user = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email_or_user or not password:
            flash('Please enter both username/email and password.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.email == email_or_user) | (User.username == email_or_user)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.dashboard_home'))
        else:
            flash('Invalid username/email or password. Please try again.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'agent')
        phone = request.form.get('phone', '').strip()

        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('A valid email address is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if User.query.filter_by(username=username).first():
            errors.append('Username is already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email is already registered.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', form_data=request.form)

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
            role=role if role in ['agent', 'buyer', 'admin'] else 'agent'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to EstateEase.', 'success')
        return redirect(url_for('dashboard.dashboard_home'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out safely.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Allows one-click login for demonstration and review purposes."""
    if role == 'agent':
        user = User.query.filter_by(email='agent@estateease.com').first()
    elif role == 'buyer':
        user = User.query.filter_by(email='buyer@estateease.com').first()
    else:
        user = User.query.filter_by(email='agent@estateease.com').first()

    if user:
        login_user(user)
        flash(f'Logged in as {user.full_name} ({user.role.title()}) for demo testing.', 'success')
        return redirect(url_for('dashboard.dashboard_home'))
    
    flash('Demo user not found. Database will be seeded.', 'warning')
    return redirect(url_for('auth.login'))

