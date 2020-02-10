
//grid width and height
class SquareGrid{
	constructor(canvas, h, numCells, p, trialData){
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
	

	createButton(gridL, gridT, idx, idy, step, gridVals, maxVal, gridEnabled, trialData){

		var button = document.createElement('button');
		button.setAttribute('class', 'unmoused');
		button.style.width = step + 0.1 + "px";
		button.style.height = step + 0.1 + "px" ;
		button.style.position = "absolute";
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
		button.addEventListener('click', function(e){
			//alert(gridVals);
			var clickData = {trialData: trialData, buttonClick: e.target.id, realClick: e.isTrusted};
			$.post("/postmethod", {
				javascript_data: JSON.stringify(clickData)
			});
			e.target.style.visibility = "hidden";

			var div = document.getElementById("div"+idx+","+idy);
			
			if(trialData['type'] === 'trial' && clickData.realClick){
				location.href = '/'+trialData.pid+'/'+trialData['type']+'/'+(trialData.num+1);
				return 0;
			}
			
			
			function colorDiv(div, maxVal){
				var val = parseFloat(gridVals[idx+','+idy]);
				div.innerText = val;
				var fRatio = (maxVal - val) / maxVal;
				//alert(fRatio);
				var color = rygbColorMap.getColor(fRatio).rgb();
				//alert(color);
				div.style['box-sizing'] = "border-box";
				div.style.border = "2px solid grey";
				div.style['background-color'] = color;
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
		button.style.position = "absolute";
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
		var body = document.getElementById("content");
		var arr = Object.values(gridVals);
		var maxVal = Math.max(...arr);

		for(var idx = 0; idx < this.numCells; idx++){
			for(var idy = 0; idy < this.numCells; idy++){
				
				body.appendChild(this.createDiv(gridL, gridT, idx, idy, step));

				body.appendChild(this.createButton(gridL, gridT, idx, idy, step, gridVals,maxVal, gridEnabled, this.trialData));
			}			
			
		}
	}
}

