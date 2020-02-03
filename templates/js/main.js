function onWindowLoad(){
	
	var c = document.getElementById('myCanvas');
	var ctx = c.getContext('2d');
 	var targetCells = ['3,7','1,5','6,2','1,2','4,4'];
	var grid = new SquareGrid(c, 400, 8, 5);
	
	var gridVals = {{ grid_values|tojson }};
	var clickedButtons = {{ clicked_buttons|tojson }};
	var enabledButtons = {{ enabled_buttons|tojson }};
	var gridEnabled = (enabledButtons === "ALL"); 
	
	grid.setButtons(gridVals, gridEnabled);
	for(var i = 0; i<enabledButtons.length; i++){
		grid.enableButtonByID(enabledButtons[i][0], enabledButtons[i][1])
	}
	for(var i = 0; i<clickedButtons.length; i++){
		grid.clickButtonByID(clickedButtons[i][0], clickedButtons[i][1])
	}
}

