from flask import jsonify, request, Blueprint
from flask_login import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

from .Categories import api_bp 
from .Transaction import api_bp
from .Task import api_bp
from .api import api_bp