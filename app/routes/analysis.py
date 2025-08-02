from flask import Blueprint, render_template

bp = Blueprint('analysis', __name__)

@bp.route('/')
def index():
    """Main page for document analysis"""
    return render_template('index.html') 