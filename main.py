"""

Main app file. To use app, do the following:

- Navigate to app directory

- [Windows CMD] set %FLASK_APP%=main.py

- flask run

- open 'localhost:5000' in browser


The experiment consists of an instruction phase; a training phase with a certain 
number of training trials, where subjects are acquainted with the task and the 
experiment; and then a test phase with a certain number of test trials, which is
the main part of the experiment and the data to be collected.

"""


from flask import Flask, render_template, url_for, jsonify, request, redirect
import os
import math
import numpy as np
import json
import random
import sqlite3
from pydbhelper import DBHelper

app = Flask(__name__);
app._static_folder_ = os.path.abspath('templates/static');
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Specify size of grid, number of training phases, number of trial phases
GRID_SIZE = 8;
NUM_TRAIN = 5;
NUM_TRIAL = 5;
dbhelp = DBHelper('./data.db');

# Specify the distance fraction, use explained later
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


"""
 Routes are defined in the main file, right here

 Routing specifies what happens when the user of the web-app is directed to 
 the page with the given URL

"""

# Route: "Index" - Starting Page - What happens when the app is first opened
@app.route('/')
@app.route('/index')
def index():
	# Generate a random subject ID; this would ideally be replaced by value from an input
	#  field that collects the subject ID
	pid = random.randint(0, 1000);
	
	
	# Open the file containing instructions
	instructions = '';
	with open(url_for('static', filename='txt/maininstructions.txt')[1:], 'r') as f:
		for line in f:
			instructions += line;

	# Flask uses Jinja templating to dynamically load html files with custom information
	# This is the method to pass variables to html files
	# `render_template` loads the html template with the passed values and serves it to 
	# 		the client

	# index.html is a template which displays a title, text, and has a single button
	# 

	# render the index template with initial task instructions and with the destination
	# 	of the button when clicked, which reroutes to /<pid>/train/1 (see route: Training Trial)
	# 	to start the training phase
	return render_template('layouts/index.html',
		page_title = 'Experiment - Terrain Scout',
		body_text = instructions,
		button_dest = '/%d/train/1'%(pid),
		button_text = 'Begin Training'
		);

# Route: "Training Trial" - loads a training trial with the `trial_num` <= `NUM_TRAIN`
@app.route('/<int:pid>/train/<trial_num>')
def render_train(trial_num, pid):
	# Write any collected data to database
	dbhelp.dump_queue();

	# If the required number of training trials have been presented, move on to the 
	# 	trial phase (see route: "Trial Begin")
	if int(trial_num) > NUM_TRAIN:
		return redirect('/%d/trialbegin'%(pid));

	instructions = 'Enter your predictions for the height of the terrain in the empty locations. \n\nClick \'Check\' to continue.';
	next_instructions = 'Here is the actual terrain, along with your estimates for the \
						terrain height at those locations, shown in the bubble. \n\nClick \'Next\' to continue.';

	# Generate a random trial from the available trials created beforehand
	sampleno, gridvals, enabled_buttons, clicked_buttons = get_trial();

	background = '';
	with open(url_for('static', filename='txt/maininstructions.txt')[1:], 'r') as f:
		for line in f:
			background += line;

	# Render the template for the grid page. This contains information about
	# 	the values of each tile in the grid, which ones are to be revealed,
	# 	and which ones are to take a user input. The button on this grid
	#	page will redirect to '/<pid/train/<trial_num+1>' to load the next trial,
	#	which will reroute to this same function to repeat the loading for the
	#	new training session, or will go to the trial phase if number of training
	# 	sessions has been surpassed.
	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		sampleno = int(sampleno),
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': url_for('static', filename='js/annotations.js')}],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = gridvals,
		enabled_buttons = enabled_buttons,
		clicked_buttons = clicked_buttons,
		title_text = 'Training: Terrain',
		trial_type = 'train',
		pid = pid,
		instructions = instructions,
		next_instructions = next_instructions,
		background = background);


# Route: "Trial Begin" - loads an information page that the trial phase is about to begin
@app.route('/<int:pid>/trialbegin')
def render_trialbegin(pid):
	# Write any collected data to database
	dbhelp.dump_queue();

	instructions = '';
	with open(url_for('static', filename='txt/traininstructions.txt')[1:], 'r') as f:
		for line in f:
			instructions += line;

	# render the index template with test task instructions and with the destination
	# 	of the button when clicked, which reroutes to /<pid>/trial/1 (see route: Test Trial)
	# 	to start the trial phase
	return render_template('layouts/index.html',
		page_title = 'Training Phase Complete',
		body_text = instructions,
		button_dest = '/%d/trial/1'%(pid),
		button_text = 'Begin Trials'
		);

# Route: "Test Trial" - loads a test trial with the `trial_num` <= `NUM_TRIALS`
@app.route('/<int:pid>/trial/<trial_num>')
def render_trial(trial_num, pid):
	# Write any collected data to database
	dbhelp.dump_queue();
	
	# If the required number of trials have been presented, move on to the 
	# 	end screen (see route: "End")
	if int(trial_num) > NUM_TRIAL:
		return redirect('/%d/end'%(pid));
	instructions = 'Enter your predictions for the height of the terrain in the empty locations. \n\nClick \'Continue\' to continue.';
	next_instructions = 'Select one of your predictions to waive. \n\n Click \'Next\' to continue.';

	# Generate a random trial
	sampleno, gridvals, enabled_buttons, clicked_buttons = get_trial();
	background = '';

	# Load the grid
	with open(url_for('static', filename='txt/traininstructions.txt')[1:], 'r') as f:
		for line in f:
			background += line;
	return render_template('layouts/grid.html',
		trial_num = int(trial_num), 
		sampleno = int(sampleno),
		static_scripts = [
			{'src': url_for('static', filename='js/jpalette.min.js')}, 
			{'src': url_for('static', filename='js/colors.js')},
			{'src': url_for('static', filename='js/grid.js')},
			{'src': url_for('static', filename='js/annotations.js')}],
		template_scripts = [
			{'src': "js/main.js"} ],
		grid_values = gridvals,
		enabled_buttons = enabled_buttons,
		clicked_buttons = clicked_buttons,
		title_text = 'Test: Terrain',
		trial_type = 'trial', 
		pid = pid,
		instructions = instructions,
		next_instructions = next_instructions,
		background = background);


"""
 Route: "End" - returns information signifying the end of the experiment
"""

@app.route('/<int:pid>/end')
def render_end(pid):
	# Write any collected data to database
	dbhelp.dump_queue();

	instructions = 'Thank you for participating.';
	return render_template('layouts/index.html',
		page_title = 'End',
		body_text = instructions,
		button_dest = '/',
		button_text = 'Restart'
		);

"""
The web app uses HTML POST requests to return information about the 
participant input to the server. This method collects that information
received in the form of a JSON, parses it, and converts that data into
information that can be stored in a database.

"""
@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data'];

    click_data = json.loads(jsdata);
    
    print("\n{}\n".format(click_data));

    dbhelp.queue_click_data(click_data);

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


"""
Loads trial information from a JSON file and assembles that data
into the appropriate trial variables.

Invoked only to fulfill the purpose of `get_trial()`

See `gp/gp_sample.py` for creation of the files that are read in 
this method

"""
def assemble_trial(filename):

	# Load JSON data file
	json_dict = {};

	if os.path.isfile(filename):
		with open(filename, 'r') as f_in:
			json_dict = json.load(f_in);

	# Read the grid indices of the tiles whose values are to be revealed
	revealed_idx = json_dict['revealed_idx'];
	json_dict['revealed_idx'] = revealed_idx;

	# These values are then revealed by simulating a button click,
	# 	which is the general method of revealing the value of a tile
	#	as defined by the SquareGrid class in `./static/js/grid.js`
	clicked_buttons = [(idx[0],idx[1]) for idx in revealed_idx];


	uncertainty_variance = json_dict['uncertainty_variance'];
	
	# Read the values of the underlying grid surface at each tile
	gridvals = gridvals_to_dict(json_dict['gridvals']);

	# Read the uncertainty at each grid point of the Gaussian Process
	# 	posterior trained on the revealed values 
	variances = np.array(json_dict['variances']);

	# Use the variances to decide which of the grid buttons are to 
	# 	be revealed for user input. Three tiles are to be revealed - 
	#	lowest uncertainty, highest uncertainty, and one with uncertainty
	# 	between the latter two, the distance of this from the extreme
	# 	uncertainty points is defined by `distance_fraction`
	for idx in clicked_buttons:
		variances[idx] = np.inf;

	enabled_buttons = [];

	# Picking a point with the lowest variance, i.e., lowest uncertainty
	#	according to the Gaussian Process posterior
	min_var = np.min(variances);
	min_idx, min_idy = np.where(variances == min_var);
	randi = np.random.randint(len(min_idx));
	enabled_buttons.append((int(min_idx[randi]), int(min_idy[randi])));

	
	# Picking a point with the highest variance, i.e., highest uncertainty
	#	according to the Gaussian Process posterior
	variances = np.where(variances == np.inf, np.NINF, variances)
	max_var = np.max(variances);
	max_idx, max_idy = np.where(variances == max_var);
	randi = np.random.randint(len(max_idx));
	enabled_buttons.append((int(max_idx[randi]), int(max_idy[randi])));

	# Picking a point with intermediate variance between the highest and
	#	lowest uncertainty values, depending on `distance_fraction`
	# `distance_fraction` of 0.5 means intermediate value has uncertainty
	#	halfway between max and min uncertainty
	int_var = distance_fraction * (max_var - min_var);
	variances = np.where(variances == np.NINF, np.inf, variances)
	distance = np.abs(variances - min_var - int_var);
	int_idx, int_idy = np.where(distance == np.min(distance));
	randi = np.random.randint(len(int_idx));
	enabled_buttons.append((int(int_idx[randi]), int(int_idy[randi])));

	# TODO: Save the enabled buttons and true uncertainty values to
	#	 	database, save by trial, create new columns

	return gridvals, enabled_buttons, clicked_buttons;

"""
Generates a random trial, whether for training or for testing.

Loads preset trials from ./valdicts directory, which each contains
information about the values in each of the grid squares (`gridvals`), which of 
the grid squares are to be revealed (`clicked_buttons`), and which
of the grid squares are to be enabled for user input (`enabled_buttons`)

Files in the ./valdicts directory are generated by `gp/gp_sample.py`

"""
def get_trial():

	# Load a file with preset values
	sampleno = np.random.randint(7,11);
	filename = 'valdicts/sample{}.json'.format(sampleno);

	# Convert the JSON file to appropriate trial variables
	gridvals, enabled_buttons, clicked_buttons = assemble_trial(filename);

	# Return trial variables
	return sampleno, gridvals, enabled_buttons, clicked_buttons;

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
	app.run();
	test = np.arange(0, 100, 1);
	for i in range(8):
		print(vec_to_buck(test, 8, i));
