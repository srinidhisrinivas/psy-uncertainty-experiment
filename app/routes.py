from app import app 
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
	return app.root_path;
	return render_template('layouts/base.html', 
		scripts = [
			{'src': '/static/jpalette.min.js'}, 
			{'src': '/static/main.js'},
			{'src': '/static/colors.js'} ]);