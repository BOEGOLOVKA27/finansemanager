# app/routes/transactions.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime
from .models import *

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

from .routes import bp