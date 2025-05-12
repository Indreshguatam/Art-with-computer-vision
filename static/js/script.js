let canvas;
function setup() {
  canvas = createCanvas(500, 400);
  canvas.parent('canvas-container');
  background(255);
}
function draw() {
  if (mouseIsPressed) {
    stroke(0);
    strokeWeight(2);
    line(mouseX, mouseY, pmouseX, pmouseY);
  }
}
