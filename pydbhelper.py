import sqlite3

"""

This class helps write the collected subject data to a SQLite Database.

Receives data in the units of JSON objects called `clickData`, each of 
which is generated every time a tile is acted upon. So, even for the same trial,
there will be 3 objects of clickData incoming if there are inputs to 3 tiles
in the grid to be registered.

"""
class DBHelper:
	def __init__(self, dbfile):
		self.con = sqlite3.connect(dbfile, check_same_thread=False);
		self.cursor = self.con.cursor();
		self.click_data_queue = [];
	def clear_data_tables(self):
		self.cursor.execute('DELETE FROM DATA');
		self.cursor.execute('DELETE FROM SAMPLES');
		self.con.commit();

	# Add the data to a queue
	def queue_click_data(self, clickData):
		self.click_data_queue.append(clickData);

	# Add all the updates from the queued data to the database
	def dump_queue(self):
		for clickData in self.click_data_queue:
			self.update_trial_data(clickData);

		self.click_data_queue = [];

	# Update the respective row of the table with the incoming click data
	def update_trial_data(self,clickData):

		trialData = clickData['trialData'];
		pid = trialData['pid'];
		trialType = trialData['type'];
		trialNum = trialData['num'];
		trialStartTime = trialData['start_time'];
		sampleno = trialData['sample_no'];
		self.cursor.execute('SELECT * FROM DATA WHERE pid=? AND trial_type=? AND trial_num=?', (int(pid), trialType, int(trialNum)));
		query = self.cursor.fetchall();

		if len(query) > 0:
			print("Found row");
		else:
			print("Creating row");
			self.cursor.execute('INSERT INTO DATA (pid, trial_type, trial_num, start_time, sample_no) VALUES (?, ?, ?, ?, ?)',\
								 (int(pid), trialType, int(trialNum), str(trialStartTime), int(sampleno)));

		print('SELECT inp_idx_1, inp_idx_2, inp_idx_3 FROM DATA \
							WHERE pid={} AND trial_type={} AND trial_num={}'.format(int(pid), trialType, int(trialNum)))
		self.cursor.execute('SELECT inp_idx_1, inp_idx_2, inp_idx_3 FROM DATA \
							WHERE pid=? AND trial_type=? AND trial_num=?', (int(pid), trialType, int(trialNum)));

		query = self.cursor.fetchall();
		
		row = query[0];
		num_none = list(row).count(None);
		insert_idx = 4 - num_none;
		
		
		if clickData['action'] == 'input':
			idx_col = 'inp_idx_' + str(insert_idx);
			val_col = 'inp_val_' + str(insert_idx);
			self.cursor.execute('UPDATE DATA SET {} = ?, {}=? WHERE \
				pid=? AND trial_type=? AND trial_num=?'.format(idx_col, val_col), (clickData['targetID'], clickData['value'],\
					int(pid), trialType, int(trialNum)));

		elif clickData['action'] == 'select':
			if 'end_time' in trialData:
				self.cursor.execute('UPDATE DATA SET selected_idx = ?, end_time=? WHERE \
					pid=? AND trial_type=? AND trial_num=?', (clickData['targetID'], trialData['end_time'], int(pid), trialType, int(trialNum)));
			else:
				self.cursor.execute('UPDATE DATA SET selected_idx = ? WHERE \
					pid=? AND trial_type=? AND trial_num=?', (clickData['targetID'], int(pid), trialType, int(trialNum)));
		
		elif clickData['action'] == 'end':
			self.cursor.execute('UPDATE DATA SET end_time = ? WHERE \
				pid=? AND trial_type=? AND trial_num=?', (trialData['end_time'], int(pid), trialType, int(trialNum)));

		self.con.commit();
		return;

		


