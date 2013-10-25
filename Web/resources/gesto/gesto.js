
window.onload = init;

function init() {
	navigator.getUsermedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || undefined;

	if(navigator.getUsermedia) {
		navigator.getUsermedia({video: true}, function (stream) {
			
			window.webcamStream = stream;

			processFrame();
		}, function() {
			alert('Error');
		});
	} else {
		alert('Switch to a different browser!!');
	}
}

function processFrame () {
	var videoElement = document.createElement("video");
	videoElement.style.display = "none";
	videoElement.autoplay = true;
	videoElement.src = window.URL.createObjectURL(window.webcamStream);
	console.log(videoElement);
	document.getElementsByTagName("body")[0].appendChild(videoElement);
	videoElement.addEventListener("canplay",drawOnCanvas);
}

function drawOnCanvas () {
	var canvasElement = document.createElement("canvas");
	var videoElement = document.getElementsByTagName("video")[0];
	var videoWidth = videoElement.videoWidth;
	var videoHeight = videoElement.videoHeight;
	var canvasWidth = videoWidth > 320 ? 320: videoWidth;
	var canvasHeight = videoHeight > 240 ? 240: videoHeight;
	canvasElement.width = canvasWidth;
	canvasElement.height = canvasHeight;
	var canvasContext = canvasElement.getContext("2d");
	var previousImageData;
	var active = false;
	var frameCount = 14;
	var currentImageData = canvasContext.createImageData(canvasWidth, canvasHeight);
	var timerId = setInterval(analyzeframe, 1000/30);
	var nextElement = document.querySelector('.next');
	var prevElement = document.querySelector('.prev');


	function analyzeframe()	{
		previousImageData = currentImageData;
		canvasContext.drawImage(videoElement, 0, 0, videoWidth, videoHeight, 0, 0, canvasWidth, canvasHeight);
		var imageData = canvasContext.getImageData(0, 0, canvasWidth, canvasHeight);
		currentImageData = imageData;
		var pixelChange = checkForPixelChange(previousImageData, currentImageData);

		if(!active) {
			if(Math.abs(pixelChange) > 15000) {
				active =true;
				frameCount = 8;
				originalPixelChange = pixelChange;

			}
		}
		if(active) {
			if(frameCount <= 0) {
				active = false;
			}
			else
			{
				frameCount--;
				if(originalPixelChange > 0) {
					if(pixelChange < -10000){
						//alert('right');
						//nextElement.dispathEvent('click');
						$('.prev').trigger('click');
						
						active = false;
					}

				}
				else {
					if(pixelChange > 15000) {
						//alert('left');
						//prevElement.dispathEvent('click');
						$('.next').trigger('click');
						active=false;
					}
				}
			}
		}

	}

	function checkForPixelChange (previousImageData, currentImageData) {
		var preData = previousImageData.data;
		var curData = currentImageData.data;
		var pixelChange=0;
		var dataLength = preData.length;
		for (var i=0; i < dataLength; i += 4) {
			
			if(Math.abs(preData[i] - curData[i]) > 30) {
			
				pixelChange += ((i/4) % canvasWidth) - (canvasWidth/2);					
			}
		}
		
		return pixelChange;
	}
}
