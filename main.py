from flask import Flask, render_template, url_for, jsonify, request
import os
import math
import numpy as np
import json

app = Flask(__name__);
app._static_folder_ = os.path.abspath('templates/static');
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
               for root_path, dirs, files in os.walk(folder)
               for f in files))

@app.route('/')
@app.route('/index')
def index():
	
	return render_template('layouts/index.html');

@app.route('/trial/<trial_num>')
def render_trial(trial_num):
	return render_template('layouts/grid.html',
		trial_num = trial_num, 
		scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/main.js')},
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'} ]);

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data'];

    id_ = json.loads(jsdata);
    targets = id_['target'];
    print(targets);

    return jsonify(get_val_dict(id_['numCells'], targets));

def get_cell_val(idx, idy):
	val = abs(float('%.1f'%(np.sin(idx * idy))));
	val = idx*idy;

	grid = np.linspace(-600, 600, 10000);
	x = vec_to_buck(grid, 8, idx);
	y = vec_to_buck(grid, 8, idy);
	xx, yy = np.meshgrid(x, y);

	z = griewank(xx,yy);
	val = abs(int(np.mean(z)));
	
	return val;

def get_val_dict(num_cells, targets):
	val_dict = {}
	for i in range(num_cells):
		for j in range(num_cells):
			idx = str(i)+','+str(j);
			if idx in targets:
				val_dict[idx] = get_cell_val(i, j);

	return val_dict;

def vec_to_buck(vec, nbucks, buckid):
	vec_size = len(vec);
	num_per_buck = math.ceil(vec_size/nbucks);
	
	for i in range(nbucks):
		start = i * num_per_buck;

		idx = np.arange(start, start+num_per_buck-1, 1).astype(int);
		if idx[-1] > vec_size-1:
			idx = np.arange(start, vec_size, 1).astype(int)
		if i == buckid:
			return vec[idx];

def griewank(x,y):
	t1 = (x**2)/4000 + (y**2)/4000;
	t2 = np.cos(x) * np.cos(y / np.sqrt(2));
	return t1 - t2 + 1;

if __name__ == '__main__':
	test = np.arange(0, 100, 1);
	for i in range(8):
		print(vec_to_buck(test, 8, i));
