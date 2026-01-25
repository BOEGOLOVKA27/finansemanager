from .. import api_bp
from flask_jwt_extended import create_access_token
from flask_login import login_user
from datetime import timedelta
from flask import request, jsonify, redirect

from flask import request, jsonify, redirect
from flask_jwt_extended import create_access_token
from flask_login import login_user
from app.modules.User.models import User
from .main import api_bp 