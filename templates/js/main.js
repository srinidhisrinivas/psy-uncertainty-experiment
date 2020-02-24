function onWindowLoad(){
	trialStartTime = Date.now();
	var c = document.getElementById('myCanvas');
	var ctx = c.getContext('2d');
 	var trialNum = {{ trial_num }};
 	var trialType = {{ trial_type|tojson }};
 	var pid = {{ pid }};
 	var trialData = {
 		type: trialType,
 		num: trialNum,
 		pid: pid
 	};

	var gridVals = {{ grid_values|tojson }};
	var clickedButtons = {{ clicked_buttons|tojson }};
	var enabledButtons = {{ enabled_buttons|tojson }};
	var gridEnabled = (enabledButtons === "ALL"); 
	try{
		var grid = new SquareGrid(c, 450, 8, 5, trialData, enabledButtons);
	}
	catch(e){
		alert(e);
	}
	
	grid.setButtons(gridVals, gridEnabled);
	for(var i = 0; i<enabledButtons.length; i++){
		grid.enableButtonInputByID(enabledButtons[i][0], enabledButtons[i][1])
	}
	for(var i = 0; i<clickedButtons.length; i++){
		grid.clickButtonByID(clickedButtons[i][0], clickedButtons[i][1])
	}
	var continueButton = document.getElementById('continueButton');
	if(trialType == 'trial'){
		var nextButton = document.getElementById('nextButton');
		nextButton.addEventListener('click', function(e){
			var selectedIdx = "0,0";

			for(var i=0; i<enabledButtons.length; i++){
				idx = enabledButtons[i][0]+','+ enabledButtons[i][1];
				if(grid.inputsSelected[idx] === 1){
					selectedIdx = idx;
				}
			}
			var inputData = {trialData: trialData, action: 'select', value: document.getElementById('input'+idx).value, targetID: idx, userGenerated: true};
			$.post("/postmethod", {
				javascript_data: JSON.stringify(inputData)
			});
		})
	}
	continueButton.addEventListener('click', function(e){
		var button = e.target;
		button.disabled = true;
		var nextButton = document.getElementById('nextButton');
		for(var i = 0; i<enabledButtons.length; i++){
			
			grid.reportInputByID(enabledButtons[i][0], enabledButtons[i][1]);
			if(trialType === 'train'){
				//grid.clickButtonByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.lockInputByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.giveFeedback(enabledButtons[i][0], enabledButtons[i][1], gridVals[enabledButtons[i][0] + "," + enabledButtons[i][1]]);
			} else {
				grid.lockInputByID(enabledButtons[i][0], enabledButtons[i][1]);
				grid.enableSelectionByID(enabledButtons[i][0], enabledButtons[i][1], 1, nextButton)
			}
			
		}
		
		if(trialType === 'train') {
			nextButton.disabled = false;
		}
		document.getElementById('instructionText').innerText = {{ next_instructions|tojson }};
	});
}

