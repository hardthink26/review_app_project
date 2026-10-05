from flask import jsonify, render_template, request
from . import main 
from datetime import datetime

@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'not found'}), 404
    return render_template('404.html',current_time=datetime.utcnow()), 404 


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=datetime.utcnow()), 500 
