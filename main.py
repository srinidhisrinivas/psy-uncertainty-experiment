from flask import Flask, render_template, url_for, jsonify, request, redirect
import os
import math
import numpy as np
import json

app = Flask(__name__);
app._static_folder_ = os.path.abspath('templates/static');
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


NUM_TRAIN = 5;
NUM_TRIAL = 5;

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
               for root_path, dirs, files in os.walk(folder)
               for f in files))

@app.route('/')
@app.route('/index')
def index():
	
	instructions = 'instructions';
	return render_template('layouts/index.html',
		page_title = 'Experiment Name',
		body_text = instructions,
		button_dest = '/train/1',
		button_text = 'Begin Training'
		);

@app.route('/end')
def render_end():
	instructions = 'thank you for participating owo';
	return render_template('layouts/index.html',
		page_title = 'End',
		body_text = instructions,
		button_dest = '/',
		button_text = 'Restart'
		);

@app.route('/trial/<trial_num>')
def render_trial(trial_num):
	if int(trial_num) > NUM_TRIAL:
		return redirect('/end');

	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'} ],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = get_val_dict(8),
		enabled_buttons = [(3,7),(1,5), (6,2)],
		clicked_buttons = [(1,2), (4,4)],
		title_text = 'Trial',
		trial_type = 'trial');

@app.route('/trialbegin')
def render_trialbegin():
	instructions = 'instructions before trial begins';
	return render_template('layouts/index.html',
		page_title = 'Training Phase Complete',
		body_text = instructions,
		button_dest = '/trial/1',
		button_text = 'Begin Trials'
		);

@app.route('/train/<trial_num>')
def render_train(trial_num):

	if int(trial_num) > NUM_TRAIN:
		return redirect('/trialbegin');

	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'} ],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = get_val_dict(8),
		enabled_buttons = "ALL",
		clicked_buttons = [],
		title_text = 'Training Phase',
		trial_type = 'train');

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

	grid = np.linspace(-5, 5, 10000);
	x = vec_to_buck(grid, 8, idx);
	y = vec_to_buck(grid, 8, idy);
	xx, yy = np.meshgrid(x, y);

	z = griewank(xx,yy);
	val = abs(int(np.mean(z)));
	val = abs(float('%.1f'%(np.mean(z))))
	return val;

def get_val_dict(num_cells):
	if os.path.isfile('valdict.json'):
		with open('valdict.json', 'r') as f_in:
			return json.load(f_in);

	val_dict = {}
	for i in range(num_cells):
		for j in range(num_cells):
			idx = str(i)+','+str(j);
			val_dict[idx] = get_cell_val(i, j);

	with open('valdict.json', 'w') as f_out:
		f_out.write(json.dumps(val_dict));

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
