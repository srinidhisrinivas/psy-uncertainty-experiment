
function createFirstTrainInputAnno(inpID){
	
	var id_ = "#" + "input" + inpID[0] + "," + inpID[1];
	var firstTrainAnnoChain = new Anno([{
		target: '#instButton',
		position: 'top',
		content: 'Click this button for a pop-up of the instructions at any time.'
	},{
		target: "#headerText",
		position: 'right',
		content: 'This is an empty cell. Click in this cell and enter the value that you think would be in here.'
	}]);
	return firstTrainAnnoChain;		

}



/*
, {
		target: "#continueButton",
		position: 'top',
		content: 'Once you\'ve entered your predictions for every empty cell, click Check here'
	}] */