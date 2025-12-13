from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from flask import jsonify, request, Blueprint
from .models import db
from flask_login import current_user, login_required
from .models import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

bp = Blueprint('categories', __name__, url_prefix='/categories')

from .routes import bp
from .api import api_bp
