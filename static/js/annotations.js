
function createFirstTrainInputAnno(inpID){
	
	var id_ = "#" + "div" + inpID[0] + "," + inpID[1];
	alert(id_);
	var firstTrainAnnoChain = new Anno([{
		target: '#instButton',
		position: 'top',
		content: 'Click this button for a pop-up of the instructions at any time.'
	},{
		target: '#div0,0',
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