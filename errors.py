from flask import render_template
from main import main_app, dbsession

@main_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main_app.errorhandler(500)
def internal_error(error):
    dbsession.rollback()
    return render_template('500.html'), 500