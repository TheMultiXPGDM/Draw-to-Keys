<p align="center"> 
  <img width="256" height="256" alt="icon" src="/Assets/draw2keys_icon.png" />
</p>

<h1 align="center">
    Draw to Keys
</h1>

A simple addon that allows you to convert space charts drawn with the annotation tool into keyframes.

---

## Features

### Draw the path, then draw the timing
You sketch two things in the 3D viewport using annotation strokes (the grease pencil tool):
- A main path (the route you want an object to follow).
- Several dash strokes crossing that path (these mark where and when the object should stop).

### Auto-convert intersections into keyframes
The addon finds all the spots where your dash strokes cross the main path. It then moves your selected object (or bone) to those exact spots, one by one, and creates a location keyframe for each crossing.

### Control the speed of the motion
You decide how much time passes between each crossing:
- Set the Frame Step (e.g., "1 frame apart" for snappy movement, or "5 frames apart" for slower pacing).
- Choose the Start Frame for the first keyframe (or just use the current frame).

### Choose which axes move
You can decide which axes of an object (or bone) are keyframed. Already animated X and Y axes? only leave Z axis enable to make a 3D movement.

### Additional value property (advanced users)
Optionally, you can record the exact distance traveled along the main path into a custom property (stroke_value). This lets you drive other things—like scale, color, or shape keys—based on how far the object has progressed.

### Choose the curve interpolation
Set the type of animation curve between keyframes:
- Constant (snap/jump).
- Linear (mechanical, straight transitions).
- Bezier (smooth, organic motion).

Or leave it as the scene default.

---
## Examples

### A ball following a sequence of drawn paths
![Example 1, a ball following a sequence of drawn paths](/Assets/example1.gif)

---

## Known Limitations

### Coplanarity dependency
The addon expects you to draw the dashes as near to the main path as possible (or draw the dashes in the same plane) to find the intersections. Drawing at some axial direction is highly encouraged.

### Lack of annotation editing
The built-in Blender annotation system lacks of enough tools to edit the annotations like eliminate/move certain strokes or move the keyframes. Making the addon work with the grease pencil objects is under consideration.

---

## Compatbility
main branch tested on: 5.1.0
