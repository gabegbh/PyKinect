# PyKinect
Mixed reality IOT input through Kinect Depth Sensor tracking in python

## Concept
I created this project when I realized that the largest pain point in the IOT/Smart Home space was the time and complexity of using a phone app or specific voice commands to a home assistant. Phone apps have always taken me longer to use than a light switch on a wall, and voice commands get incredibly frustrating when you forget a specific phrase or the name of a specific device. The limitation of physical switches is of course their position and immutability. Personally, my Smart Home is always evolving, adding devices, changing their functions or altering groupings. This is where PyKinect comes in.

## Function
PyKinect was designed to provide a 100% scalable, changable, and customizable input method. The Kinect Sensor can be placed anywhere it will fit, and provides a very detailed depth map of a doorway, wall, or any room you choose. With the ability to create custom sliders and buttons, your smart home controls can be hovering anywhere in the range of the sensor. When your hand, head, arm or any other creative object passes through these virtual input zones, the slider or button is updated through a center-of-gravity calculation returning the value of the slider or button, 0-100 or pressed or unpressed. Auto Calibration features elevate the input zone 1-3 inches off the surface behind it, and allow simple and convenient gesture inputs, however with more control you can place input zones anywhere in space with the proper coordinate inputs. Future development aims to simplify that process.

## Connections
Currently, the PyKinect communicated via socket connections to any device or microcontroller that it points to, though with tweaking, any connection method or system integration would be possible. In the demo below, I have the Kinect reading the input of a vertical slider, outputting a 1-100 value to an ESP32 SBC running a string of LEDs which turn on or off to the value of the slider.

## Demo
1. The virtual slider is positioned about 1 inch from the wall, and responds very quickly and accurately to my hand passing through.
![Slider Demo](https://user-images.githubusercontent.com/24580466/173914263-dde46d36-ea45-4fa3-823c-a219f3e3a07a.gif)

2. Since the slider is located in reference to the wall, any forground (or background) movement does not interfere with it or activate it.
![Depth Demo](https://user-images.githubusercontent.com/24580466/173915212-60c8a31e-28b4-4589-b00b-0b1b4aa25778.gif)

3. As the slider is activated, the script sends a packet to the Espressif SBC controlling the closet lighting. Future work includes speeding up the flow of information between the script and ESP32, making the animations smoother.
![Lights Demo](https://user-images.githubusercontent.com/24580466/173915578-d4c6dc96-abf5-4126-81a9-d752e51f6f10.gif)

4. Final demo of utility and simplicity of using gesture sliders over traditional 
![Final Demo](https://user-images.githubusercontent.com/24580466/173925438-89c4622f-b87e-40bf-ab4e-275424814f1d.gif)

5. Speed test against using a phone app (middle), and using a home assistant voice command, showing at least 4x faster operation with PyKinect system.

    ![Speed demo](https://user-images.githubusercontent.com/24580466/173942515-97ba4590-2e92-4e64-b397-1c7ceb937ff6.gif)
