function onWindowLoad(){
	
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

	var grid = new SquareGrid(c, 400, 8, 5, trialData, enabledButtons.length);
	grid.setButtons(gridVals, gridEnabled);
	for(var i = 0; i<enabledButtons.length; i++){
		grid.enableButtonInputByID(enabledButtons[i][0], enabledButtons[i][1])
	}
	for(var i = 0; i<clickedButtons.length; i++){
		grid.clickButtonByID(clickedButtons[i][0], clickedButtons[i][1])
	}
}

