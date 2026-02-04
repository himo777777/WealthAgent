"""
Wealth Agent Routes - Standalone Version
"""

import json
import logging
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, request, jsonify, session,
    redirect, url_for, g
)

from database import db_session
from models import UserProfile, WealthGoal, ChatConversation, ChatMessage, Insight

logger = logging.getLogger(__name__)

wealth_bp = Blueprint('wealth_agent', __name__, url_prefix='')


# ==========================================================================
# AUTHENTICATION (Simple session-based)
# ==========================================================================

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('wealth_agent.login'))
        g.current_user = session.get('user_id')
        g.user_profile = get_or_create_profile()
        return f(*args, **kwargs)
    return decorated_function


def get_or_create_profile():
    """Get or create user profile."""
    user_id = session.get('user_id')
    if not user_id:
        return None

    profile = db_session.query(UserProfile).filter_by(user_id=user_id).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db_session.add(profile)
        db_session.commit()

    return profile


# ==========================================================================
# AUTH ROUTES
# ==========================================================================

@wealth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Demo mode - accept demo/demo1234
        if username == 'demo' and password == 'demo1234':
            session['user_id'] = username
            session['user_name'] = 'Demo User'
            return redirect(url_for('wealth_agent.index'))

        # For simplicity, accept any username/password
        if username and password:
            session['user_id'] = username
            session['user_name'] = username.title()
            return redirect(url_for('wealth_agent.index'))

        return render_template('login.html', error='Ange användarnamn och lösenord')

    return render_template('login.html')


@wealth_bp.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('wealth_agent.login'))


# ==========================================================================
# PAGE ROUTES
# ==========================================================================

@wealth_bp.route('/dashboard/')
@wealth_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard."""
    profile = g.user_profile

    if not profile.onboarding_completed:
        return redirect(url_for('wealth_agent.onboarding'))

    goals = db_session.query(WealthGoal).filter_by(
        profile_id=profile.id, status='aktiv'
    ).all()

    return render_template(
        'dashboard.html',
        profile=profile.to_dict() if hasattr(profile, 'to_dict') else {},
        goals=[g.to_dict() for g in goals] if goals else []
    )

# Alias for backwards compatibility
dashboard = index


@wealth_bp.route('/onboarding')
@login_required
def onboarding():
    """Onboarding wizard."""
    return render_template(
        'onboarding.html',
        profile=g.user_profile.to_dict() if hasattr(g.user_profile, 'to_dict') else {},
        current_step=g.user_profile.onboarding_step if g.user_profile else 0
    )


@wealth_bp.route('/chat')
@login_required
def chat():
    """AI Chat interface."""
    profile = g.user_profile
    if not profile.onboarding_completed:
        return redirect(url_for('wealth_agent.onboarding'))

    return render_template('chat.html', profile=profile.to_dict())


@wealth_bp.route('/profile')
@login_required
def profile_page():
    """Profile page."""
    return render_template('profile.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/goals')
@login_required
def goals():
    """Goals page."""
    profile = g.user_profile
    if not profile.onboarding_completed:
        return redirect(url_for('wealth_agent.onboarding'))

    all_goals = db_session.query(WealthGoal).filter_by(profile_id=profile.id).all()
    return render_template('goals.html', profile=profile.to_dict(), goals=[g.to_dict() for g in all_goals])


@wealth_bp.route('/millionaire')
@login_required
def millionaire():
    """Millionaire calculator."""
    return render_template('millionaire.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/budget')
@login_required
def budget():
    """Budget page."""
    return render_template('budget.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/portfolio')
@login_required
def portfolio():
    """Portfolio page."""
    return render_template('portfolio.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/fire')
@login_required
def fire():
    """FIRE calculator."""
    return render_template('fire.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/challenges')
@login_required
def challenges_page():
    """Challenges/achievements page."""
    return render_template('challenges.html', profile=g.user_profile.to_dict())


@wealth_bp.route('/settings')
@login_required
def settings():
    """Settings page."""
    return render_template('settings.html', profile=g.user_profile.to_dict())


# ==========================================================================
# API ROUTES
# ==========================================================================

@wealth_bp.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get user profile."""
    return jsonify({'success': True, 'profile': g.user_profile.to_dict()})


@wealth_bp.route('/api/profile', methods=['POST', 'PUT'])
@login_required
def api_update_profile():
    """Update user profile."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data'}), 400

    profile = g.user_profile

    # Update allowed fields
    allowed_fields = [
        'occupation', 'employer', 'industry', 'years_in_field',
        'education_level', 'specialization', 'investment_experience',
        'monthly_income', 'monthly_expenses', 'current_savings',
        'risk_profile', 'financial_goals_summary', 'onboarding_completed',
        'onboarding_step'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(profile, field, data[field])

    profile.updated_at = datetime.utcnow()
    db_session.commit()

    return jsonify({'success': True, 'profile': profile.to_dict()})


@wealth_bp.route('/api/onboarding/complete', methods=['POST'])
@login_required
def api_complete_onboarding():
    """Mark onboarding as complete."""
    profile = g.user_profile
    profile.onboarding_completed = True
    profile.onboarding_step = 99
    profile.updated_at = datetime.utcnow()
    db_session.commit()

    return jsonify({'success': True})


@wealth_bp.route('/api/goals', methods=['GET'])
@login_required
def api_get_goals():
    """Get all goals."""
    goals = db_session.query(WealthGoal).filter_by(profile_id=g.user_profile.id).all()
    return jsonify({'success': True, 'goals': [g.to_dict() for g in goals]})


@wealth_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    """Create a new goal."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data'}), 400

    goal = WealthGoal(
        profile_id=g.user_profile.id,
        type=data.get('type', 'general'),
        name=data.get('name', 'Nytt mål'),
        target_amount=data.get('target_amount', 0),
        current_amount=data.get('current_amount', 0),
        target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None,
        priority=data.get('priority', 'medel')
    )

    db_session.add(goal)
    db_session.commit()

    return jsonify({'success': True, 'goal': goal.to_dict()}), 201


@wealth_bp.route('/api/dashboard/summary', methods=['GET'])
@login_required
def api_dashboard_summary():
    """Get dashboard summary data."""
    profile = g.user_profile

    return jsonify({
        'success': True,
        'summary': {
            'net_worth': profile.net_worth or 0,
            'monthly_savings': profile.monthly_savings or 0,
            'savings_rate': profile.savings_rate or 0,
            'goals_count': db_session.query(WealthGoal).filter_by(
                profile_id=profile.id, status='aktiv'
            ).count()
        }
    })
