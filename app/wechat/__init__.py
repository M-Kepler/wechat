from flask import Blueprint

wechat = Blueprint('wechat', __name__)

from . import views
from .func_plugins import *
