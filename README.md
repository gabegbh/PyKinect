# PyKinect
Mixed reality IOT input through Kinect Depth Sensor tracking in python

## Concept
I created this project when I realized that the largest pain point in the IOT/Smart Home space was the time and complexity of using a phone app or specific voice commands to a home assistant. Phone apps have always taken me longer to use than a light switch on a wall, and voice commands get incredibly frustrating when you forget a specific phrase or the name of a specific device. The limitation of physical switches is of course their position and immutability. Personally, my Smart Home is always evolving, adding devices, changing their functions or altering groupings. This is where PyKinect comes in.

## Function
PyKinect was designed to provide a 100% scalable, changable, and customizable input method. The Kinect Sensor can be placed anywhere it will fit, and provides a very detailed depth map of a doorway, wall, or any room you choose. With the ability to create custom sliders and buttons, your smart home controls can be hovering anywhere in the range of the sensor. When your hand, head, arm or any other creative object passes through these virtual input zones, the slider or button is updated through a center-of-gravity calculation returning the value of the slider or button, 0-100 or pressed or unpressed. Auto Calibration features elevate the input zone 1-3 inches off the surface behind it, and allow simple and convenient gesture inputs, however with more control you can place input zones anywhere in space with the proper coordinate inputs. Future development aims to simplify that process.

## Connections
Currently, the PyKinect communicated via socket connections to any device or microcontroller that it points to, though with tweaking, any connection method or system integration would be possible. In the demo below, I have the Kinect reading the input of a vertical slider, outputting a 1-100 value to an ESP32 SBC running a string of LEDs which turn on or off to the value of the slider.
