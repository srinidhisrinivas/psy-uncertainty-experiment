
function arrayToRGB(array){
	return "rgb("+array[0]+","+array[1]+","+array[2]+")";
}
function hexToDecimal(hex){
	var dec=0;
	var hexMap = {A: 10, B: 11, C: 12, D: 13, E: 14, F: 15};
	for(var i = 0; i < hex.length; i++){
		var digit = hex.charAt(i);
		var exp = hex.length - i - 1;

		var digitValue = parseInt(String(digit), 16);
		dec += digitValue * Math.pow(16, exp);
	}
	return dec;
}
function hexToRGB(hex){
	var r = hex.substring(0,2);
	var g = hex.substring(2,4);
	var b = hex.substring(4);

	return "rgb("+hexToDecimal(r)+","+hexToDecimal(g)+","+hexToDecimal(b)+")";
}
var rgbToHex = function (rgb) { 
  var hex = Number(rgb).toString(16);
  if (hex.length < 2) {
       hex = "0" + hex;
  }
  return hex;
};
var fullColorHex = function(r,g,b) {   
  var red = rgbToHex(r);
  var green = rgbToHex(g);
  var blue = rgbToHex(b);
  return red+green+blue;
};
// Returns a single rgb color interpolation between given rgb color
// based on the factor given; via https://codepen.io/njmcode/pen/axoyD?editors=0010
function interpolateColor(color1, color2, factor) {
    if (arguments.length < 3) { 
        factor = 0.5; 
    }
    var result = color1.slice();
    for (var i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
    }
    return result;
};
// My function to interpolate between two colors completely, returning an array
function interpolateColors(color1, color2, steps) {
    var stepFactor = 1 / (steps - 1),
        interpolatedColorArray = [];

    color1 = color1.match(/\d+/g).map(Number);
    color2 = color2.match(/\d+/g).map(Number);

    for(var i = 0; i < steps; i++) {
        interpolatedColorArray.push(interpolateColor(color1, color2, stepFactor * i));
    }

    return interpolatedColorArray;
}
