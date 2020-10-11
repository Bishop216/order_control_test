import logging
from flask import Blueprint

logger = logging.getLogger(__file__)
bp = Blueprint('store', __name__, url_prefix='/store')
