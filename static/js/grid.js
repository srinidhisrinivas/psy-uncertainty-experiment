 
/**

This class contains all the functionality of the grid with the buttons and the underlying
surface. This communicates mostly with `main.js` but also sends HTML POST requests to the
back-end when certain actions are taken on the tiles in the grid.

**/


class SquareGrid{
	constructor(canvas, h, numCells, p, trialData, inputEnabledButtons){
		if(h===undefined){
			h = 400;
		}
		if(numCells===undefined){
			numCells = 8;
		}
		if(p===undefined){
			p = 5;
		}
		this.canvas = canvas;
		this.h = h;
		this.w = h;
		this.p = p;
		this.numCells = numCells;
		this.canvas.height = h;
		this.canvas.width = h;
		this.trialData = trialData;
		this.inputsValid = {};
		this.inputsSelected = {};

		for(var i = 0; i < inputEnabledButtons.length; i++){
			this.inputsValid[inputEnabledButtons[i][0] + ',' + inputEnabledButtons[i][1]] = 0;
			this.inputsSelected[inputEnabledButtons[i][0] + ',' + inputEnabledButtons[i][1]] = 0;
		}
		this.maxVal = 0;
	}
	draw(){
		//alert(this.gridVals);
		var context = this.canvas.getContext('2d');
		var bw = this.h - 1 - 2*this.p;
		var bh = bw;
		var step = bw / this.numCells;
		//size of canvas
		for (var x = 0; x <= bw; x += step) {
	        context.moveTo(0.5 + x + this.p, this.p);
	        context.lineTo(0.5 + x + this.p, bh + this.p);
	    }


	    for (var x = 0; x <= bh; x += step) {
	        context.moveTo(this.p, 0.5 + x + this.p);
	        context.lineTo(bw + this.p, 0.5 + x + this.p);
	    }

	    context.strokeStyle = "black";
	    context.stroke();
	    return 0;
	}
	disableButton(button){
		button.style['background-color'] = "#d3d3d3";
		button.style['border'] = "none";
		button.disabled = true;
	}
	clickButton(button){
		this.enableButton(button);
		button.click();
	}
	clickButtonByID(idx, idy){
		var button = document.getElementById(idx+","+idy);
		this.clickButton(button);
	}
	enableButton(button){
		button.style['background-color'] = "white";
		button.style.border = "2px solid grey";
		button.disabled = false;
	}
	enableButtonByID(idx, idy){
		var button = document.getElementById(idx+","+idy);
		this.enableButton(button);
	}
	enableButtonInputByID(idx, idy){
		var button = document.getElementById(idx+","+idy);
		this.enableButtonInput(button);		
	}
	hideInputByID(idx, idy){
		var input = document.getElementById('input'+''+idx+","+idy);
		this.hideInput(input)
	}
	hideInput(input){
		input.hidden = true;
	}
	lockInputByID(idx, idy){
		var input = document.getElementById('input'+''+idx+","+idy);
		this.lockInput(input)
	}
	lockInput(input){
		var id_ = input.id.substring(input.id.search('[0-9]'));
		input.readOnly = true;
		
	}
	changeTextColorByID(idx, idy, color){
		var div = document.getElementById('div'+''+idx+","+idy);
		div.style['border'] = "3px solid grey";
		//div.style.color = color;
		//div.style['font-size'] = 24+'pt';
		div.style['font-weight'] = 700;
	}
	enableSelectionByID(idx, idy, targetSelections, button){
		var input = document.getElementById('input'+''+idx+","+idy);
		this.enableSelection(input, targetSelections, button);
	}
	selectInputByID(id_, grid){
		var inpId = 'input' + id_;
		var divId = 'div' + id_;
		var input = document.getElementById(inpId);
		var div = document.getElementById(divId);
		
		var enabledInputs = Object.keys(grid.inputsSelected);
		for(var i = 0; i < enabledInputs.length; i++){
			grid.deselectInputByID(enabledInputs[i], grid);
		}
		div.style.border = '3px solid #66ff00';
		div.style.background = '#66ff00';
		div.style.color = '#66ff00';
		//input.style['font-size'] = 24+'pt';
		grid.inputsSelected[id_] = 1;
	}
	deselectInputByID(id_, grid){
		var inpId = 'input' + id_;
		var divId = 'div' + id_;
		var input = document.getElementById(inpId);
		var div = document.getElementById(divId);
		var enabledInputs = Object.keys(grid.inputsSelected);

		div.style.border = '3px solid black';
		div.style.background = div.getAttribute('data-color');
		div.style.color = 'black';
		//input.style['font-size'] = 18+'pt';


		grid.inputsSelected[id_] = 0;
	}
	enableSelection(input, targetSelections, button){
		var inputsSelected = this.inputsSelected;
		var selector = this.selectInputByID;
		var deselector = this.deselectInputByID;
		var grid = this;
		var id_ = input.id.substring(input.id.search('[0-9]'));
		var div = document.getElementById('div'+id_);
		div.innerText = input.value;
		input.value = '';
		input.hidden = true;
		
		div.addEventListener('click', function(e){
			if(inputsSelected[id_] === 1){
				deselector(id_, grid);
			} else {
				selector(id_, grid);
			}

			function getKeyByValue(object, value) {
			  return Object.keys(object).find(key => object[key] === value);
			}

			if(Object.values(inputsSelected).reduce(function(acc, val){ return acc + val; }, 0) === targetSelections){
				button.disabled = false;
				var selectedidx = getKeyByValue(inputsSelected, 1);
				var selectedval = document.getElementById("div"+selectedidx).innerText;
				document.getElementById('binstruction').innerText = "You are about to waive estimate " + selectedval + ". Click \'Next\' to continue."; 
			} else {
				button.disabled = true;
				document.getElementById('binstruction').innerText = "Select ONE estimate to waive."
			}
		});
	}

	reportInputByID(idx, idy){
		var input = document.getElementById('input'+''+idx+","+idy);
		var inputData = {trialData: this.trialData, action: 'input', value: input.value, targetID: input.id, userGenerated: true};
		$.post("/postmethod", {
			javascript_data: JSON.stringify(inputData)
		});
	}
	giveFeedback(idx, idy, trueVal){
		var id_ = idx+','+idy;
		var p = document.createElement('div');
		p.class = 'feedbackBox';
		p.id = 'feedback'+id_;
		var input = document.getElementById('input'+id_);
		var div = document.getElementById('div'+id_);
		var button = document.getElementById(id_);
		var body = document.getElementById('gridlayer');
		var buttonWidth = parseFloat(button.style.width.substring(0,button.style.width.indexOf('p')));
		var buttonLeft = parseFloat(button.style.left.substring(0,button.style.left.indexOf('p')));
		p.innerText = input.value;
		p.style.left = (buttonLeft + buttonWidth - 15) + 'px';

		var buttonTop = parseFloat(button.style.top.substring(0,button.style.top.indexOf('p')));
		p.style.top = (buttonTop - 15) + 'px';
		p.style.position = 'fixed';
		p.style.border = '2px solid black';
		p.style['background-color'] = 'white';
		p.style['font-weight'] = 1000;
		p.style['font-family'] = 'Consolas';
		p.style.opacity = 0.85;
		p.style.margin = '2px';
		p.style.padding = '2px';
		p.style.width = '20px';
		p.style['border-radius'] = '10px 10px 10px 0px';

		div.style.border = '3px solid black';

		

		body.appendChild(p); 
	}

	enableButtonInput(button){
		button.style.visibility = "hidden";
		this.clickButton(button);
		var buttonRect = button.getBoundingClientRect();
		var inp = document.createElement('input');
		var div = document.getElementById('div'+button.id);
		inp.id = 'input'+button.id;
		inp.type = 'number';
		inp.min = '0';
		inp.max = '99';
		inp.maxlength = 2;
		inp.style.position = 'fixed';
		var buttonLeft = parseFloat(button.style.left.substring(0,button.style.left.indexOf('p')));
		var buttonTop = parseFloat(button.style.top.substring(0,button.style.top.indexOf('p')));
		inp.style.left = (buttonLeft) + 'px';
		inp.style.top = (buttonTop + 2) + 'px';
		inp.style.outline = 'none';
		var buttonWidth = parseFloat(button.style.width.substring(0,button.style.width.indexOf('p')));
		var buttonHeight = parseFloat(button.style.height.substring(0,button.style.height.indexOf('p')));
		var inpWidth = buttonWidth;
		var inpHeight = buttonHeight;
		
		inp.style.width = inpWidth + 'px';
		inp.style.height = inpHeight + 'px';

		inp.style.background = 'transparent';
		inp.style.border = 'none';
		div.style.border = '3px solid black';
		div.style['background-color'] = '#FFFF9E'
		div.innerText = "";

		inp.style['font-family'] = "Bahnschrift";

		inp.style['font-weight'] = 350;
		inp.style['font-size'] = 18+"pt";
		inp.style['text-align'] = "center";
		
		inp.style['vertical-align'] =  'middle';
		
		var body = document.getElementById('gridlayer');

		body.appendChild(inp);
		function colorDiv(div, currentVal, maxVal){
			if(currentVal === ''){
				div.style['background-color'] = '#FFFF9E';
			} else {
				var val = parseFloat(currentVal);
				var fRatio = (maxVal - val) / maxVal;
				
				var color = redColorMap.getColor(fRatio).rgb();
				//alert(color);
				div.setAttribute('data-color', color);
				div.style['background-color'] = color;
			}
		}
		var maxVal = this.maxVal;
		var inputsValid = this.inputsValid;
		inp.addEventListener('input', function(e){
			
			e.target.value = e.target.value.replace(/[^0-9]*/g,'');
			var idx = e.target.id.substring(e.target.id.search('[0-9]'));
			var divIdx = "div" + idx;
			if (!e.target.value || isNaN(e.target.value)){
				e.target.value = '';
			}
			var div = document.getElementById(divIdx);
			if ((""+e.target.value).length > 2){
				e.target.value = e.target.value.slice(0, 2);	
			} 
			if ((""+e.target.value).includes(".")){
				alert('here');
				e.target.value = e.target.value.slice(0,-1);
			}
			if(e.target.value && !isNaN(e.target.value)){
				inputsValid[idx] = 1;
			} else {
				inputsValid[idx] = 0;
			}
			
			var vals = Object.values(inputsValid);
			if(vals.every(function(val) { return val === 1; })){
				document.getElementById('continueButton').disabled = false;
				

			} else {
				document.getElementById('continueButton').disabled = true;
				
			}
			colorDiv(div, e.target.value, maxVal);
		});

	}
	clickAllButtons(){
		for(var i = 0; i < this.numCells; i++){
			for(var j = 0; j < this.numCells; j++){
				this.clickButtonByID(i,j);
			}
		}
	}
	createButton(gridL, gridT, idx, idy, step, gridVals, maxVal, gridEnabled, trialData){

		var button = document.createElement('button');
		button.setAttribute('class', 'unmoused');
		button.style.width = step + 0.1 + "px";
		button.style.height = step + 0.1 + "px" ;
		button.style.position = 'fixed';
		button.style.left = gridL + idx * (step + this.p - 1.45) + "px";
		button.style.top = gridT + idy * (step + this.p - 1.45) + "px";

		//button.innerText = this.numCells * idx + idy + 1;
		button.id = idx+','+idy;
		//alert('er');
		//alert(button.id);
		button.style.color = "red";
		//alert("button.id");
		button.style.background = "white";
		button.style.border = "2px solid grey";
		button.style.outline = "none";

		if(!gridEnabled){
			this.disableButton(button);
		}
		/**
		button.addEventListener('mouseover', function(e){
			e.target.setAttribute('class', 'moused');
			e.target.style['background-color'] = "#FF0000";
			e.target.style.border = "2px solid #8b0000";
			
		});
		button.addEventListener('mouseout', function(e){
			e.target.setAttribute('class', 'unmoused');
			e.target.style['background-color'] = "#FFFFFF";
			e.target.style.border = "2px solid grey";
		
		});
		**/
		button.addEventListener('click', function(e){
			//alert(gridVals);
			var clickData = {trialData: trialData, action: 'click', value: gridVals[e.target.id], targetID: e.target.id, userGenerated: e.isTrusted};
			if(clickData.userGenerated){
				$.post("/postmethod", {
					javascript_data: JSON.stringify(clickData)
				});
			}
				
			
			e.target.style.visibility = "hidden";
			var div = document.getElementById("div"+idx+","+idy);
			
			if(trialData['type'] === 'trial' && clickData.realClick){
				location.href = '/'+trialData.pid+'/'+trialData['type']+'/'+(trialData.num+1);
				return 0;
			}
			if(clickData.realClick){
				var continueButton = document.getElementById('continueButton');
				continueButton.disabled = false;
			}
			
			
			function colorDiv(div, maxVal){
				var val = parseFloat(gridVals[idx+','+idy]);
				div.innerText = val;
				var fRatio = (maxVal - val) / maxVal;
				//alert(fRatio);
				var color = redColorMap.getColor(fRatio).rgb();
				//alert(color);
				div.style['box-sizing'] = "border-box";
				div.style.border = "2px solid grey";
				div.style['background-color'] = color;
				div.setAttribute('data-color', color);

			}
			colorDiv(div, maxVal);
		
		});
		//this.clickButton(button);
		
		return button;

	}
	
	createDiv(gridL, gridT, idx, idy, step){
		var button = document.createElement('div');
		button.style.width = step + 0.1 + "px";
		button.style.height = step + 0.1+"px" ;
		button.style.position = 'fixed';
		button.style.left = gridL + idx * (step + this.p - 1.45) + "px";
		button.style.top = gridT + idy * (step + this.p - 1.45) + "px";
		button.style['text-align'] = "center";
		
		button.style['vertical-align'] =  'middle';
		button.style['line-height'] =  step + "px";
		button.setAttribute('onselectstart', 'return false');
		button.id = "div"+idx+","+idy;
		var div = button;
		div.style['background-color'] = "#FFFF9E";
		div.style['font-family'] = "Bahnschrift";

		div.style['font-weight'] = 350;
		div.style['font-size'] = 18+"pt";

		return button;
	}

	setButtons(gridVals, gridEnabled){

		var rect = this.canvas.getBoundingClientRect();
		var gridL = rect.left + this.p + 3;
		var gridT = rect.top + this.p + 3;
		var bw = this.h - 1 - 2*this.p;
		var step = bw / this.numCells - 3.5;
		var body = document.getElementById("gridlayer");
		var arr = Object.values(gridVals);
		var maxVal = Math.max(...arr);
		this.maxVal = maxVal;

		for(var idx = 0; idx < this.numCells; idx++){
			for(var idy = 0; idy < this.numCells; idy++){
				
				body.appendChild(this.createDiv(gridL, gridT, idx, idy, step));

				body.appendChild(this.createButton(gridL, gridT, idx, idy, step, gridVals,maxVal, gridEnabled, this.trialData));
			}			
			
		}
	}
	
}

