from flask import Blueprint

bp = Blueprint('search', __name__, static_folder='static/search/')
from app.search import search2
from app.search import construction
