
/**

Main JavaScript functionality of the web application. Controls all the logic of the 
front-end. Back-end sends information to front-end by loading HTML templates with
dynamic variables. Back-end returns information to front-end using HTML POST requests.

This script is reloaded every time a new trial is started, and controls the operation
of the trial functionalities from start of the trial to end of the trial.
**/

function onWindowLoad(){

	trialStartTime = Date.now();
	var c = document.getElementById('myCanvas');
	var ctx = c.getContext('2d');

	// Receive trial information from back-end using Jinja templates
 	var trialNum = {{ trial_num }};
 	var trialType = {{ trial_type|tojson }};
 	var pid = {{ pid }};
 	var sampleno = {{ sampleno }};
 	var trialData = {
 		sample_no: sampleno,
 		start_time: trialStartTime.toString(),
 		type: trialType,
 		num: trialNum,
 		pid: pid
 	};

	var gridVals = {{ grid_values|tojson }};
	var clickedButtons = {{ clicked_buttons|tojson }};
	var enabledButtons = {{ enabled_buttons|tojson }};

	// Special case to display all of the grid values for 
	// 	debugging purposes
	var gridEnabled = (enabledButtons === "ALL"); 
	
	// Create a new SquareGrid object
	try{
		var grid = new SquareGrid(c, 450, 8, 5, trialData, enabledButtons);
	}
	catch(e){
		alert(e);
	}


	// Initialize the grid with the values of each tile 
	grid.setButtons(gridVals, gridEnabled); 

	// Enable the input for the tiles that require input value
	for(var i = 0; i<enabledButtons.length; i++){
		grid.enableButtonInputByID(enabledButtons[i][0], enabledButtons[i][1])
	}

	// Reveal the tiles that need to be revealed
	for(var i = 0; i<clickedButtons.length; i++){
		grid.changeTextColorByID(clickedButtons[i][0], clickedButtons[i][1], "#002366");
		grid.clickButtonByID(clickedButtons[i][0], clickedButtons[i][1]);
	}
	var continueButton = document.getElementById('continueButton');
	
	// Show the annotations for the instructions (currently not working)
	if(trialType === 'train' && trialNum === 1){
	
		var ann = createFirstTrainInputAnno(enabledButtons[0])
		ann.show();
	}
		
	// If in trial, report the additional information about which of the 
	// 		inputs was selected to be discarded
	if(trialType === 'trial'){

		var nextButton = document.getElementById('nextButton');
		nextButton.addEventListener('click', function(e){
			var selectedIdx = "0,0";
			for(var i=0; i<enabledButtons.length; i++){
				var idx = enabledButtons[i][0]+','+ enabledButtons[i][1];
				if(grid.inputsSelected[idx] === 1){
					selectedIdx = idx;
				}
			}
			trialData['end_time'] = Date.now().toString();

			var inputData = {trialData: trialData, action: 'select', value: document.getElementById('div'+selectedIdx).innerText, targetID: idx, userGenerated: true};
			$.post("/postmethod", {
				javascript_data: JSON.stringify(inputData)
			});
		});
	}

	// When the inputs are complete, give feedback in training condition or 
	// 	enable selection of inputs in trial condition
	continueButton.addEventListener('click', function(e){
		var button = e.target;
		button.disabled = true;
		var nextButton = document.getElementById('nextButton');
		if(trialType === 'train'){
			grid.clickAllButtons();
		}
		for(var i = 0; i<enabledButtons.length; i++){
			
			grid.reportInputByID(enabledButtons[i][0], enabledButtons[i][1]);
			if(trialType === 'train'){
				//grid.clickButtonByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.hideInputByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.lockInputByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.giveFeedback(enabledButtons[i][0], enabledButtons[i][1], gridVals[enabledButtons[i][0] + "," + enabledButtons[i][1]]);
			} else {
				grid.lockInputByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.enableSelectionByID(enabledButtons[i][0], enabledButtons[i][1], 1, nextButton)
				document.getElementById('binstruction').innerText = 'Select ONE estimate to waive.'
			}
			
		}
		
		if(trialType === 'train') {
			nextButton.disabled = false;
			// Send post to signify end of trial
			trialData['end_time'] = Date.now().toString();
			var inputData = {trialData: trialData, action: 'end'};
			$.post("/postmethod", {
				javascript_data: JSON.stringify(inputData)
			});
		}
		document.getElementById('instructionText').innerText = {{ next_instructions|tojson }};

		
	}); 
	// Get the modal
	var modal = document.getElementById("myModal");

	// Get the button that opens the modal
	var btn = document.getElementById("instButton");

	// Get the <span> element that closes the modal
	var span = document.getElementById("close");

	// When the user clicks on the button, open the modal
	btn.onclick = function() {
	  modal.style.display = "block";
	}

	// When the user clicks on <span> (x), close the modal
	span.onclick = function() {
	  modal.style.display = "none";
	}

	// When the user clicks anywhere outside of the modal, close it
	window.onclick = function(event) {
	  if (event.target == modal) {
	    modal.style.display = "none";
	  }
	}
}

