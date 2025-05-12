function setup() {
    let canvas = createCanvas(800, 500);
    canvas.parent('canvas-container');
    background(255);
  }
  
  function draw() {
    if (mouseIsPressed) {
      stroke(0);
      strokeWeight(4);
      line(pmouseX, pmouseY, mouseX, mouseY);
    }
  }
  