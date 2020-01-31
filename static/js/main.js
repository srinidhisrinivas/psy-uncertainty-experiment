
function onWindowLoad(){
	
	var c = document.getElementById('myCanvas');
	var ctx = c.getContext('2d');
 	var targetCells = ['3,7','1,5','6,2','1,2','4,4']
	var grid = new SquareGrid(c, 400, 8, 5);
	//var gridVals = {{ grid_values }};
	grid.draw();
	$.post("/postmethod", {
			javascript_data: JSON.stringify({numCells: grid.numCells, target: JSON.stringify(targetCells)})
		}, function(data, status){
			grid.setButtons(data);
			grid.enableButtonByID(3,7);
			grid.enableButtonByID(1,5);
			grid.enableButtonByID(6,2);
			grid.clickButtonByID(1,2);
			grid.clickButtonByID(4,4);
		});
	//grid.draw();
	
	
}