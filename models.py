"""
Wealth Agent Database Models

SQLAlchemy models for AI Wealth Agent functionality.
Handles user profiles, goals, conversations, and insights.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Float,
    Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from database import Base


class UserProfile(Base):
    """Extended user profile for wealth management."""

    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # Username or external ID

    # Background & Career
    occupation = Column(String(255), nullable=True)
    employer = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)  # medicin_vard, tech, finans, etc.
    years_in_field = Column(Integer, nullable=True)
    education_level = Column(String(100), nullable=True)  # gymnasium, kandidat, master, doktor
    specialization = Column(String(255), nullable=True)
    side_jobs = Column(Text, nullable=True)  # JSON array

    # Skills & Knowledge (JSON)
    skills_json = Column(Text, nullable=True)
    investment_experience = Column(String(50), nullable=True)  # nybörjare, mellan, erfaren, expert
    entrepreneurship_experience = Column(String(50), nullable=True)
    tech_savviness = Column(String(50), nullable=True)  # låg, medel, hög

    # Financial Situation (Encrypted fields - stored as encrypted strings)
    monthly_income_encrypted = Column(Text, nullable=True)
    monthly_expenses_encrypted = Column(Text, nullable=True)
    current_savings_encrypted = Column(Text, nullable=True)
    total_debt_encrypted = Column(Text, nullable=True)
    monthly_debt_payment_encrypted = Column(Text, nullable=True)
    emergency_fund_months = Column(Integer, nullable=True)

    # Investment Profile
    risk_tolerance = Column(String(50), nullable=True)  # konservativ, balanserad, aggressiv
    time_horizon = Column(String(50), nullable=True)  # kort, medel, lång
    investment_interests_json = Column(Text, nullable=True)  # JSON array: aktier, fonder, fastigheter, krypto, etc.

    # Goals Overview
    short_term_goals_json = Column(Text, nullable=True)  # < 1 year
    medium_term_goals_json = Column(Text, nullable=True)  # 1-5 years
    long_term_goals_json = Column(Text, nullable=True)  # 5+ years
    dream_goal = Column(Text, nullable=True)

    # Availability
    hours_per_week_available = Column(Integer, nullable=True)

    # Onboarding Status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=1)  # Current step in wizard

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goals = relationship('WealthGoal', backref='user_profile', lazy='dynamic')
    conversations = relationship('ChatConversation', backref='user_profile', lazy='dynamic')
    insights = relationship('Insight', backref='user_profile', lazy='dynamic')

    def to_dict(self, include_encrypted: bool = False) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'occupation': self.occupation,
            'employer': self.employer,
            'industry': self.industry,
            'years_in_field': self.years_in_field,
            'education_level': self.education_level,
            'specialization': self.specialization,
            'side_jobs': json.loads(self.side_jobs) if self.side_jobs else [],
            'skills': json.loads(self.skills_json) if self.skills_json else {},
            'investment_experience': self.investment_experience,
            'entrepreneurship_experience': self.entrepreneurship_experience,
            'tech_savviness': self.tech_savviness,
            'risk_tolerance': self.risk_tolerance,
            'time_horizon': self.time_horizon,
            'investment_interests': json.loads(self.investment_interests_json) if self.investment_interests_json else [],
            'short_term_goals': json.loads(self.short_term_goals_json) if self.short_term_goals_json else [],
            'medium_term_goals': json.loads(self.medium_term_goals_json) if self.medium_term_goals_json else [],
            'long_term_goals': json.loads(self.long_term_goals_json) if self.long_term_goals_json else [],
            'dream_goal': self.dream_goal,
            'hours_per_week_available': self.hours_per_week_available,
            'emergency_fund_months': self.emergency_fund_months,
            'onboarding_completed': self.onboarding_completed,
            'onboarding_step': self.onboarding_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_encrypted:
            result.update({
                'monthly_income_encrypted': self.monthly_income_encrypted,
                'monthly_expenses_encrypted': self.monthly_expenses_encrypted,
                'current_savings_encrypted': self.current_savings_encrypted,
                'total_debt_encrypted': self.total_debt_encrypted,
                'monthly_debt_payment_encrypted': self.monthly_debt_payment_encrypted,
            })

        return result


class WealthGoal(Base):
    """Financial goal tracking."""

    __tablename__ = 'wealth_goals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # sparande, investering, inkomst, företag, skuld

    # Amount tracking
    target_amount = Column(Float, nullable=True)
    current_amount = Column(Float, default=0.0)
    currency = Column(String(10), default='SEK')

    # Timeline
    deadline = Column(DateTime, nullable=True)
    priority = Column(String(20), default='medel')  # låg, medel, hög

    # Status
    status = Column(String(20), default='aktiv')  # aktiv, pausad, slutförd, avbruten

    # Milestones (JSON array)
    milestones_json = Column(Text, nullable=True)

    # AI-generated insights
    ai_suggestions_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary."""
        progress = 0
        if self.target_amount and self.target_amount > 0:
            progress = min(100, (self.current_amount / self.target_amount) * 100)

        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'currency': self.currency,
            'progress_percent': round(progress, 1),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority,
            'status': self.status,
            'milestones': json.loads(self.milestones_json) if self.milestones_json else [],
            'ai_suggestions': json.loads(self.ai_suggestions_json) if self.ai_suggestions_json else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class ChatConversation(Base):
    """Chat conversation container."""

    __tablename__ = 'chat_conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    title = Column(String(255), nullable=True)  # Auto-generated from first message

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship('ChatMessage', backref='conversation', lazy='dynamic', order_by='ChatMessage.created_at')

    def to_dict(self, include_messages: bool = False) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        result = {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.messages.count() if self.messages else 0,
        }

        if include_messages:
            result['messages'] = [msg.to_dict() for msg in self.messages.all()]

        return result


class ChatMessage(Base):
    """Individual chat message."""

    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('chat_conversations.id'), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)

    # Context tracking (what profile data was used)
    context_used_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'context_used': json.loads(self.context_used_json) if self.context_used_json else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Insight(Base):
    """AI-generated insights and recommendations."""

    __tablename__ = 'wealth_insights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    type = Column(String(50), nullable=False)  # opportunity, tip, alert, report, reminder
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    priority = Column(String(20), default='medel')  # låg, medel, hög
    category = Column(String(50), nullable=True)  # investering, sparande, karriär, etc.

    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    # Action
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary."""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'category': self.category,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'action_url': self.action_url,
            'action_label': self.action_label,
            'metadata': json.loads(self.metadata_json) if self.metadata_json else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }


class RiskToleranceAnswer(Base):
    """Store individual risk tolerance quiz answers."""

    __tablename__ = 'risk_tolerance_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    question_id = Column(Integer, nullable=False)
    answer_value = Column(Integer, nullable=False)  # 1-5 scale typically

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================================
# NEW MODELS FOR COMPLETE WEALTH MANAGEMENT
# ==========================================================================

class NetWorthSnapshot(Base):
    """Track net worth over time for visualization."""

    __tablename__ = 'net_worth_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Snapshot date
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)

    # Assets (encrypted)
    total_assets_encrypted = Column(Text, nullable=True)
    cash_encrypted = Column(Text, nullable=True)
    investments_encrypted = Column(Text, nullable=True)
    real_estate_encrypted = Column(Text, nullable=True)
    other_assets_encrypted = Column(Text, nullable=True)

    # Liabilities (encrypted)
    total_liabilities_encrypted = Column(Text, nullable=True)
    mortgage_encrypted = Column(Text, nullable=True)
    student_loans_encrypted = Column(Text, nullable=True)
    other_debts_encrypted = Column(Text, nullable=True)

    # Net worth (encrypted)
    net_worth_encrypted = Column(Text, nullable=True)

    # Source of data
    source = Column(String(50), default='manual')  # manual, tink, calculated

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'snapshot_date': self.snapshot_date.isoformat() if self.snapshot_date else None,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PortfolioHolding(Base):
    """Track investment portfolio holdings."""

    __tablename__ = 'portfolio_holdings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Holding details
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), nullable=True)
    asset_type = Column(String(50), nullable=False)  # aktie, fond, etf, obligation, krypto, fastighet
    account_type = Column(String(50), nullable=True)  # ISK, KF, AF, tjanstepension

    # Platform
    platform = Column(String(50), nullable=True)  # avanza, nordnet, other

    # Quantity and value
    quantity = Column(Float, nullable=True)
    purchase_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    currency = Column(String(10), default='SEK')

    # Performance
    gain_loss = Column(Float, nullable=True)
    gain_loss_percent = Column(Float, nullable=True)

    # Dates
    purchase_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'ticker': self.ticker,
            'asset_type': self.asset_type,
            'account_type': self.account_type,
            'platform': self.platform,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'current_price': self.current_price,
            'current_value': self.current_value,
            'currency': self.currency,
            'gain_loss': self.gain_loss,
            'gain_loss_percent': self.gain_loss_percent,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


class BudgetCategory(Base):
    """Budget categories for expense tracking."""

    __tablename__ = 'budget_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    name = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    # Budget limits
    monthly_budget = Column(Float, nullable=True)
    is_fixed = Column(Boolean, default=False)  # Fixed vs variable expense

    # Category type
    category_type = Column(String(50), default='expense')  # expense, income, savings

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship('BudgetTransaction', backref='category', lazy='dynamic')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'monthly_budget': self.monthly_budget,
            'is_fixed': self.is_fixed,
            'category_type': self.category_type,
        }


class BudgetTransaction(Base):
    """Individual budget transactions."""

    __tablename__ = 'budget_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('budget_categories.id'), nullable=True)

    description = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # expense, income

    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default='manual')  # manual, tink

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'description': self.description,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'source': self.source,
        }


class Debt(Base):
    """Track individual debts for debt payoff planning."""

    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    debt_type = Column(String(50), nullable=False)  # bolan, studielan, billan, konsumentlan, kreditkort

    # Amounts
    original_amount = Column(Float, nullable=True)
    current_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)  # Annual rate as decimal (0.05 = 5%)

    # Payments
    minimum_payment = Column(Float, nullable=True)
    current_payment = Column(Float, nullable=True)

    # Lender info
    lender = Column(String(255), nullable=True)

    # Status
    status = Column(String(20), default='active')  # active, paid_off

    # Dates
    start_date = Column(DateTime, nullable=True)
    expected_payoff_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'debt_type': self.debt_type,
            'original_amount': self.original_amount,
            'current_balance': self.current_balance,
            'interest_rate': self.interest_rate,
            'minimum_payment': self.minimum_payment,
            'current_payment': self.current_payment,
            'lender': self.lender,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expected_payoff_date': self.expected_payoff_date.isoformat() if self.expected_payoff_date else None,
        }


class Notification(Base):
    """Push notifications and alerts."""

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    notification_type = Column(String(50), nullable=False)  # reminder, alert, achievement, opportunity, tip
    priority = Column(String(20), default='normal')  # low, normal, high, urgent

    # Action
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'action_url': self.action_url,
            'action_label': self.action_label,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class EducationCourse(Base):
    """Education courses and modules."""

    __tablename__ = 'education_courses'

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # investering, budgetering, skatteplanering, foretagande

    difficulty = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    duration_minutes = Column(Integer, nullable=True)

    # Content
    content_json = Column(Text, nullable=True)  # JSON with lessons/chapters
    thumbnail_url = Column(String(500), nullable=True)

    # Status
    is_published = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'duration_minutes': self.duration_minutes,
            'content': json.loads(self.content_json) if self.content_json else [],
            'thumbnail_url': self.thumbnail_url,
            'is_published': self.is_published,
            'order': self.order,
        }


class EducationProgress(Base):
    """Track user progress in education courses."""

    __tablename__ = 'education_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('education_courses.id'), nullable=False, index=True)

    # Progress
    progress_percent = Column(Float, default=0.0)
    completed_lessons_json = Column(Text, nullable=True)  # JSON array of completed lesson IDs

    # Status
    status = Column(String(20), default='not_started')  # not_started, in_progress, completed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Quiz/test scores
    quiz_scores_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'course_id': self.course_id,
            'progress_percent': self.progress_percent,
            'completed_lessons': json.loads(self.completed_lessons_json) if self.completed_lessons_json else [],
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'quiz_scores': json.loads(self.quiz_scores_json) if self.quiz_scores_json else {},
        }


class FIRECalculation(Base):
    """FIRE (Financial Independence, Retire Early) calculations."""

    __tablename__ = 'fire_calculations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # FIRE inputs
    annual_expenses = Column(Float, nullable=True)
    current_savings = Column(Float, nullable=True)
    annual_savings = Column(Float, nullable=True)
    expected_return = Column(Float, default=0.07)  # 7% default
    withdrawal_rate = Column(Float, default=0.04)  # 4% rule

    # FIRE outputs
    fire_number = Column(Float, nullable=True)  # Amount needed for FIRE
    years_to_fire = Column(Float, nullable=True)
    fire_date = Column(DateTime, nullable=True)

    # Scenarios (JSON)
    scenarios_json = Column(Text, nullable=True)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'annual_expenses': self.annual_expenses,
            'current_savings': self.current_savings,
            'annual_savings': self.annual_savings,
            'expected_return': self.expected_return,
            'withdrawal_rate': self.withdrawal_rate,
            'fire_number': self.fire_number,
            'years_to_fire': self.years_to_fire,
            'fire_date': self.fire_date.isoformat() if self.fire_date else None,
            'scenarios': json.loads(self.scenarios_json) if self.scenarios_json else [],
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }


class TaxOptimization(Base):
    """Tax optimization calculations and recommendations."""

    __tablename__ = 'tax_optimizations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    tax_year = Column(Integer, nullable=False)

    # Income details
    employment_income = Column(Float, nullable=True)
    business_income = Column(Float, nullable=True)
    capital_gains = Column(Float, nullable=True)
    dividend_income = Column(Float, nullable=True)

    # Deductions
    deductions_json = Column(Text, nullable=True)  # ROT, RUT, ranta, etc.

    # Account optimization
    isk_recommendation = Column(Text, nullable=True)
    kf_recommendation = Column(Text, nullable=True)

    # 3:12 rules (for business owners)
    rules_312_applicable = Column(Boolean, default=False)
    rules_312_recommendation = Column(Text, nullable=True)

    # Total optimization
    potential_savings = Column(Float, nullable=True)
    recommendations_json = Column(Text, nullable=True)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'tax_year': self.tax_year,
            'employment_income': self.employment_income,
            'business_income': self.business_income,
            'capital_gains': self.capital_gains,
            'dividend_income': self.dividend_income,
            'deductions': json.loads(self.deductions_json) if self.deductions_json else {},
            'isk_recommendation': self.isk_recommendation,
            'kf_recommendation': self.kf_recommendation,
            'rules_312_applicable': self.rules_312_applicable,
            'rules_312_recommendation': self.rules_312_recommendation,
            'potential_savings': self.potential_savings,
            'recommendations': json.loads(self.recommendations_json) if self.recommendations_json else [],
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }


# ==========================================================================
# GAMIFICATION SYSTEM
# ==========================================================================

class Achievement(Base):
    """Achievement definitions for gamification."""

    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Achievement info
    code = Column(String(50), unique=True, nullable=False)  # first_goal, streak_7, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Visual
    icon = Column(String(50), default='trophy')
    badge_color = Column(String(20), default='gold')  # gold, silver, bronze, purple, green

    # Category
    category = Column(String(50), nullable=False)  # savings, investing, learning, streak, milestone

    # Requirements
    requirement_type = Column(String(50), nullable=False)  # count, amount, streak, date
    requirement_value = Column(Float, nullable=True)

    # Rewards
    xp_reward = Column(Integer, default=100)

    # Status
    is_active = Column(Boolean, default=True)
    is_secret = Column(Boolean, default=False)  # Hidden until unlocked

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'badge_color': self.badge_color,
            'category': self.category,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'xp_reward': self.xp_reward,
            'is_secret': self.is_secret,
        }


class UserAchievement(Base):
    """Track which achievements users have earned."""

    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)

    # Progress (for progressive achievements)
    current_progress = Column(Float, default=0)
    target_progress = Column(Float, nullable=True)

    # Status
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)

    # Notification
    is_notified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'achievement_id': self.achievement_id,
            'current_progress': self.current_progress,
            'target_progress': self.target_progress,
            'is_unlocked': self.is_unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
        }


class UserLevel(Base):
    """Track user levels and XP for gamification."""

    __tablename__ = 'user_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), unique=True, nullable=False)

    # Level & XP
    current_level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)

    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)

    # Stats
    total_achievements = Column(Integer, default=0)
    total_goals_completed = Column(Integer, default=0)
    total_lessons_completed = Column(Integer, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'current_level': self.current_level,
            'current_xp': self.current_xp,
            'total_xp': self.total_xp,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'total_achievements': self.total_achievements,
            'total_goals_completed': self.total_goals_completed,
            'total_lessons_completed': self.total_lessons_completed,
        }


class Milestone(Base):
    """Track financial milestones and celebrations."""

    __tablename__ = 'milestones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Milestone type
    milestone_type = Column(String(50), nullable=False)  # net_worth, savings, debt_free, goal
    milestone_value = Column(Float, nullable=False)  # 100000, 500000, 1000000
    milestone_label = Column(String(100), nullable=True)  # "100k", "500k", "Miljonär!"

    # Status
    is_reached = Column(Boolean, default=False)
    reached_at = Column(DateTime, nullable=True)

    # Celebration
    is_celebrated = Column(Boolean, default=False)  # Has user seen celebration?

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'milestone_type': self.milestone_type,
            'milestone_value': self.milestone_value,
            'milestone_label': self.milestone_label,
            'is_reached': self.is_reached,
            'reached_at': self.reached_at.isoformat() if self.reached_at else None,
            'is_celebrated': self.is_celebrated,
        }


# ==========================================================================
# FINANCIAL HEALTH SCORE
# ==========================================================================

class FinancialHealthScore(Base):
    """Track financial health score over time."""

    __tablename__ = 'financial_health_scores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Overall score (0-100)
    total_score = Column(Integer, nullable=False)

    # Component scores (0-100 each)
    savings_score = Column(Integer, nullable=True)  # Emergency fund, savings rate
    debt_score = Column(Integer, nullable=True)  # Debt-to-income, interest rates
    investment_score = Column(Integer, nullable=True)  # Diversification, growth
    budget_score = Column(Integer, nullable=True)  # Spending vs income
    protection_score = Column(Integer, nullable=True)  # Insurance, safety net

    # Breakdown JSON for details
    breakdown_json = Column(Text, nullable=True)

    # Recommendations
    recommendations_json = Column(Text, nullable=True)

    # Comparison
    percentile = Column(Integer, nullable=True)  # Where user ranks vs others

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'total_score': self.total_score,
            'savings_score': self.savings_score,
            'debt_score': self.debt_score,
            'investment_score': self.investment_score,
            'budget_score': self.budget_score,
            'protection_score': self.protection_score,
            'breakdown': json.loads(self.breakdown_json) if self.breakdown_json else {},
            'recommendations': json.loads(self.recommendations_json) if self.recommendations_json else [],
            'percentile': self.percentile,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }


# ==========================================================================
# SUBSCRIPTION MANAGEMENT
# ==========================================================================

class Subscription(Base):
    """Track recurring subscriptions."""

    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Subscription info
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)  # streaming, software, gym, telecom, insurance, other

    # Cost
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='SEK')
    billing_cycle = Column(String(20), default='monthly')  # monthly, yearly, weekly

    # Dates
    start_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    cancellation_date = Column(DateTime, nullable=True)

    # Usage tracking
    usage_frequency = Column(String(20), nullable=True)  # daily, weekly, rarely, never
    last_used = Column(DateTime, nullable=True)

    # Status
    status = Column(String(20), default='active')  # active, cancelled, paused

    # Analysis
    value_score = Column(Integer, nullable=True)  # 1-10, how valuable is this?
    cancel_recommendation = Column(Boolean, default=False)

    # Source
    source = Column(String(50), default='manual')  # manual, tink

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'provider': self.provider,
            'category': self.category,
            'amount': self.amount,
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'usage_frequency': self.usage_frequency,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'status': self.status,
            'value_score': self.value_score,
            'cancel_recommendation': self.cancel_recommendation,
            'source': self.source,
            'monthly_cost': self.amount if self.billing_cycle == 'monthly' else (self.amount / 12 if self.billing_cycle == 'yearly' else self.amount * 4),
        }


# ==========================================================================
# PENSION FORECAST
# ==========================================================================

class PensionForecast(Base):
    """Swedish pension forecast calculations."""

    __tablename__ = 'pension_forecasts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # User inputs
    birth_year = Column(Integer, nullable=True)
    current_salary = Column(Float, nullable=True)
    planned_retirement_age = Column(Integer, default=65)

    # Allmän pension (state pension)
    inkomstpension_monthly = Column(Float, nullable=True)
    premiepension_monthly = Column(Float, nullable=True)
    garantipension_monthly = Column(Float, nullable=True)
    total_allman_pension = Column(Float, nullable=True)

    # Tjänstepension (occupational pension)
    tjanstepension_provider = Column(String(100), nullable=True)  # ITP, SAF-LO, KAP-KL, etc.
    tjanstepension_monthly = Column(Float, nullable=True)
    tjanstepension_capital = Column(Float, nullable=True)

    # Privat pension
    privat_pension_monthly = Column(Float, nullable=True)
    privat_pension_capital = Column(Float, nullable=True)
    isk_savings = Column(Float, nullable=True)
    other_savings = Column(Float, nullable=True)

    # Total forecast
    total_monthly_pension = Column(Float, nullable=True)
    replacement_rate = Column(Float, nullable=True)  # Percentage of current salary

    # Gap analysis
    desired_monthly_income = Column(Float, nullable=True)
    monthly_gap = Column(Float, nullable=True)
    additional_savings_needed = Column(Float, nullable=True)

    # Scenarios JSON
    scenarios_json = Column(Text, nullable=True)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'birth_year': self.birth_year,
            'current_salary': self.current_salary,
            'planned_retirement_age': self.planned_retirement_age,
            'allman_pension': {
                'inkomstpension': self.inkomstpension_monthly,
                'premiepension': self.premiepension_monthly,
                'garantipension': self.garantipension_monthly,
                'total': self.total_allman_pension,
            },
            'tjanstepension': {
                'provider': self.tjanstepension_provider,
                'monthly': self.tjanstepension_monthly,
                'capital': self.tjanstepension_capital,
            },
            'privat_pension': {
                'monthly': self.privat_pension_monthly,
                'capital': self.privat_pension_capital,
                'isk_savings': self.isk_savings,
                'other_savings': self.other_savings,
            },
            'total_monthly_pension': self.total_monthly_pension,
            'replacement_rate': self.replacement_rate,
            'gap_analysis': {
                'desired_income': self.desired_monthly_income,
                'monthly_gap': self.monthly_gap,
                'additional_savings_needed': self.additional_savings_needed,
            },
            'scenarios': json.loads(self.scenarios_json) if self.scenarios_json else [],
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }


# ==========================================================================
# RECURRING TRANSACTIONS
# ==========================================================================

class RecurringTransaction(Base):
    """Track recurring income and expenses."""

    __tablename__ = 'recurring_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('budget_categories.id'), nullable=True)

    # Transaction info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # income, expense

    # Recurrence
    frequency = Column(String(20), default='monthly')  # daily, weekly, biweekly, monthly, yearly
    day_of_month = Column(Integer, nullable=True)  # 1-31 for monthly
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly

    # Dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    next_occurrence = Column(DateTime, nullable=True)
    last_processed = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    auto_create = Column(Boolean, default=True)  # Auto-create budget transactions

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'frequency': self.frequency,
            'day_of_month': self.day_of_month,
            'day_of_week': self.day_of_week,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_occurrence': self.next_occurrence.isoformat() if self.next_occurrence else None,
            'is_active': self.is_active,
            'auto_create': self.auto_create,
        }


# ==========================================================================
# REPORTS
# ==========================================================================

class FinancialReport(Base):
    """Weekly and monthly financial reports."""

    __tablename__ = 'financial_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Report type
    report_type = Column(String(20), nullable=False)  # weekly, monthly, yearly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Summary metrics
    total_income = Column(Float, nullable=True)
    total_expenses = Column(Float, nullable=True)
    net_savings = Column(Float, nullable=True)
    savings_rate = Column(Float, nullable=True)

    # Net worth change
    net_worth_start = Column(Float, nullable=True)
    net_worth_end = Column(Float, nullable=True)
    net_worth_change = Column(Float, nullable=True)

    # Goals progress
    goals_progress_json = Column(Text, nullable=True)

    # Category breakdown
    expense_breakdown_json = Column(Text, nullable=True)
    income_breakdown_json = Column(Text, nullable=True)

    # Insights and recommendations
    insights_json = Column(Text, nullable=True)
    highlights_json = Column(Text, nullable=True)  # Key achievements/concerns

    # Comparison
    vs_previous_period_json = Column(Text, nullable=True)

    # Email status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'summary': {
                'total_income': self.total_income,
                'total_expenses': self.total_expenses,
                'net_savings': self.net_savings,
                'savings_rate': self.savings_rate,
            },
            'net_worth': {
                'start': self.net_worth_start,
                'end': self.net_worth_end,
                'change': self.net_worth_change,
            },
            'goals_progress': json.loads(self.goals_progress_json) if self.goals_progress_json else [],
            'expense_breakdown': json.loads(self.expense_breakdown_json) if self.expense_breakdown_json else {},
            'income_breakdown': json.loads(self.income_breakdown_json) if self.income_breakdown_json else {},
            'insights': json.loads(self.insights_json) if self.insights_json else [],
            'highlights': json.loads(self.highlights_json) if self.highlights_json else [],
            'vs_previous': json.loads(self.vs_previous_period_json) if self.vs_previous_period_json else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==========================================================================
# USER PREFERENCES (Theme, etc.)
# ==========================================================================

class UserPreferences(Base):
    """User preferences including theme, notifications, etc."""

    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), unique=True, nullable=False)

    # Theme
    theme = Column(String(20), default='dark')  # dark, light, auto
    accent_color = Column(String(20), default='indigo')

    # Notifications
    email_weekly_report = Column(Boolean, default=True)
    email_monthly_report = Column(Boolean, default=True)
    email_goal_reminders = Column(Boolean, default=True)
    email_insights = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)

    # Display
    currency = Column(String(10), default='SEK')
    date_format = Column(String(20), default='YYYY-MM-DD')
    number_format = Column(String(20), default='sv-SE')

    # Privacy
    show_amounts = Column(Boolean, default=True)  # Show/hide amounts on dashboard

    # Language
    language = Column(String(10), default='sv')

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'theme': self.theme,
            'accent_color': self.accent_color,
            'email_weekly_report': self.email_weekly_report,
            'email_monthly_report': self.email_monthly_report,
            'email_goal_reminders': self.email_goal_reminders,
            'email_insights': self.email_insights,
            'push_notifications': self.push_notifications,
            'currency': self.currency,
            'date_format': self.date_format,
            'number_format': self.number_format,
            'show_amounts': self.show_amounts,
            'language': self.language,
        }


# ==========================================================================
# PARTNER SHARING
# ==========================================================================

class PartnerInvite(Base):
    """Partner/family sharing invitations."""

    __tablename__ = 'partner_invites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Invite details
    invite_email = Column(String(255), nullable=False)
    invite_code = Column(String(50), unique=True, nullable=False)
    invite_role = Column(String(20), default='viewer')  # viewer, editor, admin

    # Status
    status = Column(String(20), default='pending')  # pending, accepted, declined, expired
    accepted_by_profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=True)

    # Permissions
    can_view_accounts = Column(Boolean, default=True)
    can_view_goals = Column(Boolean, default=True)
    can_view_budget = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)

    # Dates
    expires_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'invite_email': self.invite_email,
            'invite_role': self.invite_role,
            'status': self.status,
            'can_view_accounts': self.can_view_accounts,
            'can_view_goals': self.can_view_goals,
            'can_view_budget': self.can_view_budget,
            'can_edit': self.can_edit,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
        }


class SharedAccess(Base):
    """Track active partner/family sharing relationships."""

    __tablename__ = 'shared_access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    partner_profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Role and permissions
    role = Column(String(20), default='viewer')
    can_view_accounts = Column(Boolean, default=True)
    can_view_goals = Column(Boolean, default=True)
    can_view_budget = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'owner_profile_id': self.owner_profile_id,
            'partner_profile_id': self.partner_profile_id,
            'role': self.role,
            'can_view_accounts': self.can_view_accounts,
            'can_view_goals': self.can_view_goals,
            'can_view_budget': self.can_view_budget,
            'can_edit': self.can_edit,
            'is_active': self.is_active,
        }


# ==========================================================================
# INCOME SOURCES
# ==========================================================================

class IncomeSource(Base):
    """Track multiple income sources."""

    __tablename__ = 'income_sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Source info
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # salary, freelance, rental, dividend, interest, side_hustle, pension, other
    employer = Column(String(255), nullable=True)

    # Amount
    amount = Column(Float, nullable=False)
    frequency = Column(String(20), default='monthly')  # monthly, yearly, weekly, one_time
    is_gross = Column(Boolean, default=True)  # Before or after tax

    # Passive income flag
    is_passive = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        monthly = self.amount if self.frequency == 'monthly' else (
            self.amount / 12 if self.frequency == 'yearly' else
            self.amount * 4 if self.frequency == 'weekly' else self.amount
        )
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'source_type': self.source_type,
            'employer': self.employer,
            'amount': self.amount,
            'frequency': self.frequency,
            'monthly_amount': monthly,
            'yearly_amount': monthly * 12,
            'is_gross': self.is_gross,
            'is_passive': self.is_passive,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
        }


# ==========================================================================
# EMERGENCY FUND
# ==========================================================================

class EmergencyFund(Base):
    """Track emergency fund / buffert."""

    __tablename__ = 'emergency_funds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), unique=True, nullable=False)

    # Goal
    target_months = Column(Integer, default=6)  # How many months of expenses
    monthly_expenses = Column(Float, nullable=True)  # For calculation
    target_amount = Column(Float, nullable=True)  # Calculated or manual

    # Current status
    current_amount = Column(Float, default=0)
    account_name = Column(String(255), nullable=True)  # Where is it stored

    # Automation
    monthly_contribution = Column(Float, default=0)
    auto_transfer = Column(Boolean, default=False)

    # Progress
    last_updated = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        target = self.target_amount or (self.monthly_expenses * self.target_months if self.monthly_expenses else 0)
        progress = (self.current_amount / target * 100) if target > 0 else 0
        months_covered = (self.current_amount / self.monthly_expenses) if self.monthly_expenses and self.monthly_expenses > 0 else 0

        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'target_months': self.target_months,
            'monthly_expenses': self.monthly_expenses,
            'target_amount': target,
            'current_amount': self.current_amount,
            'account_name': self.account_name,
            'monthly_contribution': self.monthly_contribution,
            'auto_transfer': self.auto_transfer,
            'progress_percent': min(100, progress),
            'months_covered': months_covered,
            'amount_remaining': max(0, target - self.current_amount),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


# ==========================================================================
# SAVINGS CHALLENGES
# ==========================================================================

class Challenge(Base):
    """Predefined savings challenges."""

    __tablename__ = 'challenges'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Challenge info
    code = Column(String(50), unique=True, nullable=False)  # 52_week, no_spend_week, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)

    # Type
    challenge_type = Column(String(50), nullable=False)  # savings, spending_reduction, income_boost

    # Duration
    duration_days = Column(Integer, nullable=True)
    duration_weeks = Column(Integer, nullable=True)

    # Target
    target_amount = Column(Float, nullable=True)  # Total to save
    weekly_targets_json = Column(Text, nullable=True)  # For progressive challenges

    # Difficulty
    difficulty = Column(String(20), default='medium')  # easy, medium, hard

    # Rewards
    xp_reward = Column(Integer, default=500)
    badge_icon = Column(String(50), default='trophy')

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'challenge_type': self.challenge_type,
            'duration_days': self.duration_days,
            'duration_weeks': self.duration_weeks,
            'target_amount': self.target_amount,
            'weekly_targets': json.loads(self.weekly_targets_json) if self.weekly_targets_json else [],
            'difficulty': self.difficulty,
            'xp_reward': self.xp_reward,
            'badge_icon': self.badge_icon,
        }


class ChallengeProgress(Base):
    """Track user progress in challenges."""

    __tablename__ = 'challenge_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey('challenges.id'), nullable=False)

    # Status
    status = Column(String(20), default='active')  # active, completed, abandoned

    # Dates
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Progress
    current_week = Column(Integer, default=1)
    current_day = Column(Integer, default=1)
    total_saved = Column(Float, default=0)
    progress_json = Column(Text, nullable=True)  # Weekly/daily progress

    # Streak
    current_streak = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'challenge_id': self.challenge_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_week': self.current_week,
            'current_day': self.current_day,
            'total_saved': self.total_saved,
            'progress': json.loads(self.progress_json) if self.progress_json else [],
            'current_streak': self.current_streak,
        }


# ==========================================================================
# BROKER CONNECTIONS
# ==========================================================================

class BrokerConnection(Base):
    """Connection to brokers like Avanza/Nordnet."""

    __tablename__ = 'broker_connections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Broker info
    broker = Column(String(50), nullable=False)  # avanza, nordnet, degiro
    account_id = Column(String(100), nullable=True)
    account_name = Column(String(255), nullable=True)

    # Connection status
    status = Column(String(20), default='disconnected')  # connected, disconnected, error
    last_sync = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # OAuth tokens (encrypted)
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'broker': self.broker,
            'account_id': self.account_id,
            'account_name': self.account_name,
            'status': self.status,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'error_message': self.error_message,
        }


# ==========================================================================
# SPENDING ANOMALIES
# ==========================================================================

class SpendingAnomaly(Base):
    """Detected spending anomalies."""

    __tablename__ = 'spending_anomalies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Anomaly details
    anomaly_type = Column(String(50), nullable=False)  # high_spending, unusual_category, new_merchant, recurring_increase
    severity = Column(String(20), default='medium')  # low, medium, high

    # Transaction details
    category = Column(String(100), nullable=True)
    merchant = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=True)

    # Comparison
    average_amount = Column(Float, nullable=True)
    deviation_percent = Column(Float, nullable=True)

    # Message
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    detected_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'category': self.category,
            'merchant': self.merchant,
            'amount': self.amount,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'average_amount': self.average_amount,
            'deviation_percent': self.deviation_percent,
            'title': self.title,
            'description': self.description,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
        }


# ==========================================================================
# SCENARIOS (What-if)
# ==========================================================================

class Scenario(Base):
    """What-if financial scenarios."""

    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Scenario info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(50), nullable=False)  # income_change, expense_change, investment, debt, retirement

    # Input parameters (JSON)
    parameters_json = Column(Text, nullable=True)

    # Results (JSON)
    results_json = Column(Text, nullable=True)

    # Comparison to current
    impact_monthly = Column(Float, nullable=True)
    impact_yearly = Column(Float, nullable=True)
    impact_fire_years = Column(Float, nullable=True)

    # Favorites
    is_favorite = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'description': self.description,
            'scenario_type': self.scenario_type,
            'parameters': json.loads(self.parameters_json) if self.parameters_json else {},
            'results': json.loads(self.results_json) if self.results_json else {},
            'impact_monthly': self.impact_monthly,
            'impact_yearly': self.impact_yearly,
            'impact_fire_years': self.impact_fire_years,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==========================================================================
# FAMILY MEMBERS
# ==========================================================================

class FamilyMember(Base):
    """Family members for shared budgeting."""

    __tablename__ = 'family_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False, index=True)

    # Member info
    name = Column(String(255), nullable=False)
    relationship = Column(String(50), nullable=False)  # spouse, child, parent, other
    birth_year = Column(Integer, nullable=True)

    # Financial info
    has_income = Column(Boolean, default=False)
    monthly_income = Column(Float, nullable=True)
    monthly_allowance = Column(Float, nullable=True)  # For children

    # Access
    has_app_access = Column(Boolean, default=False)
    linked_user_id = Column(Integer, nullable=True)

    # Budget allocation
    budget_percent = Column(Float, nullable=True)  # % of family budget

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'relationship': self.relationship,
            'birth_year': self.birth_year,
            'has_income': self.has_income,
            'monthly_income': self.monthly_income,
            'monthly_allowance': self.monthly_allowance,
            'has_app_access': self.has_app_access,
            'budget_percent': self.budget_percent,
            'is_active': self.is_active,
        }
