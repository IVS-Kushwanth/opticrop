from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db, login_manager
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')
    role = request.form.get('role', 'farmer')

    if not name or not email or not password:
        flash('All fields are required.', 'danger')
        return render_template('auth/register.html')

    if password != confirm:
        flash('Passwords do not match.', 'danger')
        return render_template('auth/register.html')

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return render_template('auth/register.html')

    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'danger')
        return render_template('auth/register.html')

    user = User(name=name, email=email, role=role if role in ('farmer', 'researcher', 'admin') else 'farmer')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        flash(f'Welcome back, {user.name}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
def profile():
    if not session.get('user_id'):
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    predictions = user.predictions if user else []
    return render_template('dashboard/index.html', user=user, predictions=predictions[:5])
