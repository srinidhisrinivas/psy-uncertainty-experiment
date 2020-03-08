from flask import Flask, render_template, url_for, jsonify, request, redirect
import os
import math
import numpy as np
import json
import random

app = Flask(__name__);
app._static_folder_ = os.path.abspath('templates/static');
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

GRID_SIZE = 8;
NUM_TRAIN = 5;
NUM_TRIAL = 5;

distance_fraction = 0.5;
current_max_uncertainty_idx = "0,0";
gridpoints = []
clicked_buttons = [];
enabled_buttons = [];
input_enabled_buttons = [];

for i in range(GRID_SIZE):
	for j in range(GRID_SIZE):
		gridpoints.append((i,j));
def get_rand_gridpoints_list(size=3):
	res = [];
	idx = np.random.randint(0, GRID_SIZE ** 2,size);
	for id_ in idx:
		res.append(gridpoints[id_]);

	return res;

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
               for root_path, dirs, files in os.walk(folder)
               for f in files))

@app.route('/')
@app.route('/index')
def index():
	pid = random.randint(0, 1000);
	print('/%d/train/1'%(pid));
	instructions = '';
	with open(url_for('static', filename='txt/maininstructions.txt')[1:], 'r') as f:
		for line in f:
			instructions += line;

	return render_template('layouts/index.html',
		page_title = 'Experiment Name',
		body_text = instructions,
		button_dest = '/%d/train/1'%(pid),
		button_text = 'Begin Training'
		);

@app.route('/<int:pid>/end')
def render_end(pid):
	instructions = 'thank you for participating owo';
	return render_template('layouts/index.html',
		page_title = 'End',
		body_text = instructions,
		button_dest = '/',
		button_text = 'Restart'
		);

@app.route('/<int:pid>/trial/<trial_num>')
def render_trial(trial_num, pid):
	if int(trial_num) > NUM_TRIAL:
		return redirect('/%d/end'%(pid));
	instructions = 'Enter your predictions for the values in the empty locations. \n\nClick \'Continue\' to continue.';
	next_instructions = 'Select one of your predictions to waive. \n\n Click \'Next\' to continue.';
	gridvals, enabled_buttons, clicked_buttons = get_trial();
	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'} ],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = gridvals,
		enabled_buttons = enabled_buttons,
		clicked_buttons = clicked_buttons,
		title_text = 'Trial',
		trial_type = 'trial', 
		pid = pid,
		instructions = instructions,
		next_instructions = next_instructions);

@app.route('/<int:pid>/trialbegin')
def render_trialbegin(pid):
	instructions = '';
	with open(url_for('static', filename='txt/traininstructions.txt')[1:], 'r') as f:
		for line in f:
			instructions += line;
	return render_template('layouts/index.html',
		page_title = 'Training Phase Complete',
		body_text = instructions,
		button_dest = '/%d/trial/1'%(pid),
		button_text = 'Begin Trials'
		);

@app.route('/<int:pid>/train/<trial_num>')
def render_train(trial_num, pid):
	if int(trial_num) > NUM_TRAIN:
		return redirect('/%d/trialbegin'%(pid));

	instructions = 'Enter your predictions for the values in the empty locations. \n\nClick \'Check\' to continue.';
	next_instructions = 'Here are the actual values of the boxes you filled in. \n\nClick \'Next\' to continue.';
	gridvals, enabled_buttons, clicked_buttons = get_trial();
	print(type(gridvals["0,3"]));
	print(type(enabled_buttons[0][0]));
	print(type(clicked_buttons[0]));

	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'} ],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = gridvals,
		enabled_buttons = enabled_buttons,
		clicked_buttons = clicked_buttons,
		title_text = 'Training Phase',
		trial_type = 'train',
		pid = pid,
		instructions = instructions,
		next_instructions = next_instructions);
"""
@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data'];

    id_ = json.loads(jsdata);
    targets = id_['target'];
    print(targets);

    return jsonify(get_val_dict(id_['numCells'], targets));
"""
@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data'];

    click_data = json.loads(jsdata);
    
    print("\n{}\n".format(click_data));

    return "0";

def get_cell_val(idx, idy):
	val = abs(float('%.1f'%(np.sin(idx * idy))));
	val = idx*idy;

	grid = np.linspace(-5, 5, 10000);
	x = vec_to_buck(grid, 8, idx);
	y = vec_to_buck(grid, 8, idy);
	xx, yy = np.meshgrid(x, y);

	z = griewank(xx,yy);
	val = abs(int(55*np.mean(z)));
	#val = abs(float('%.1f'%(np.mean(z))))
	return val;

def listidx_to_stringidx(listidx):
	return str(listidx[0] + "," + listidx[1]);


def gridvals_to_dict(gridvals):
	valdict = {};
	for i in range(len(gridvals)):
		for j in range(len(gridvals[0])):
			valdict[str(i) + "," + str(j)] = gridvals[i][j];

	return valdict;

def scalar_to_2dindex(idx, n):
	idx1 = int(idx / n);
	idx2 = (idx % n).item();
	return (idx1, idx2);

def assemble_trial(filename):
	json_dict = {};
	print(filename);
	if os.path.isfile(filename):
		with open(filename, 'r') as f_in:
			json_dict = json.load(f_in);

	revealed_idx = json_dict['revealed_idx'];
	json_dict['revealed_idx'] = revealed_idx;
	uncertainty_variance = json_dict['uncertainty_variance'];
	gridvals = gridvals_to_dict(json_dict['gridvals']);
	variances = np.array(json_dict['variances']);

	clicked_buttons = [(idx[0],idx[1]) for idx in revealed_idx];
	
	for idx in clicked_buttons:
		variances[idx] = np.inf;

	print(variances);
	enabled_buttons = [];

	# picking lowest variance point at random
	min_var = np.min(variances);
	min_idx, min_idy = np.where(variances == min_var);
	randi = np.random.randint(len(min_idx));
	# print(min_var);
	# print(min_idx[randi], min_idy[randi]);
	enabled_buttons.append((int(min_idx[randi]), int(min_idy[randi])));

	# picking highest variance point at random
	variances = np.where(variances == np.inf, np.NINF, variances)
	max_var = np.max(variances);
	max_idx, max_idy = np.where(variances == max_var);
	randi = np.random.randint(len(max_idx));
	enabled_buttons.append((int(max_idx[randi]), int(max_idy[randi])));

	# picking intermediate variance point at random
	int_var = distance_fraction * (max_var - min_var);
	variances = np.where(variances == np.NINF, np.inf, variances)
	print(int_var)
	distance = np.abs(variances - min_var - int_var);
	print(distance);
	int_idx, int_idy = np.where(distance == np.min(distance));
	randi = np.random.randint(len(int_idx));
	enabled_buttons.append((int(int_idx[randi]), int(int_idy[randi])));

	return gridvals, enabled_buttons, clicked_buttons;


def get_trial():
	file_num = np.random.randint(1,6);
	filename = 'valdicts/sample{}.json'.format(file_num);
	gridvals, enabled_buttons, clicked_buttons = assemble_trial(filename);
	return gridvals, enabled_buttons, clicked_buttons;

def get_val_dict(num_cells):
	val_dict = np.random.randint(1,6);
	filename = "valdicts/valdict{}.json".format(val_dict);
	if os.path.isfile(filename):
		with open(filename, 'r') as f_in:
			return json.load(f_in);

	val_dict = {}
	for i in range(num_cells):
		for j in range(num_cells):
			idx = str(i)+','+str(j);
			val_dict[idx] = get_cell_val(i, j);

	with open('valdict.json', 'w') as f_out:
		f_out.write(json.dumps(val_dict));

	print(max(val_dict.values()));
	print(min(val_dict.values()));
	print('\n');
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
