from flask import (render_template, request, redirect, url_for, flash, 
                   Blueprint, session, current_app)
from werkzeug.security import generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
import secrets
from werkzeug.security import check_password_hash
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ChangeLoginForm, ChangeEmailForm, ChangePasswordForm
from datetime import datetime, timedelta
from app import db, mail
from flask_mail import Message
from config import config
from .models import * 
from sqlalchemy import func, extract
from flask_login import UserMixin



bp_profile = Blueprint('profile', __name__)
bp_auth = Blueprint('auth', __name__)


from .routes_auth import bp as bp_auth
from .routes_profile import bp as bp_profile