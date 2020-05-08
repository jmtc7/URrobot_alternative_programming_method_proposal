# Alternative programming method for UR robotic arms
This project's objective is not to create a real full-operative alternative to the current programming methods for industrial robots but to propose an idea developing a Proof of Concept to show that this approach could have potential.

The project has 2 main parts:
* **3D-printable case** to contain and protect the Raspberry Pi, a camera, a distance sensor and a fan. It also makes it possible to attach the whole system to the UR robot wirst.
* **Python scripts** to program the robot and make it able to replay the teached movements. The robot has to be running its own (simple) program to move according the Modbus TCP-received messages.

Demos of the target segmentation (color and shape filtered) and of the final results (target tracking and following and trajectory reproduction) are available in the following **YouTube videos**:

[![Target segmentation demo](multimedia/demo_videos/demo_targetDetection.gif)](https://www.youtube.com/watch?v=7s4_1wDeRGM&list=PLBYQePjTMEGEnVe6FjThMmySTzwtxLX1B&index=1)

[![Results demo](multimedia/demo_videos/demo_results.gif)](https://www.youtube.com/watch?v=rEhbCNIjvR4&list=PLBYQePjTMEGEnVe6FjThMmySTzwtxLX1B&index=2)

NOTE: This project was developed during my internship at [CFZ Cobots](https://cfzcobots.com/), in Elche (Spain), and submitted in a competition of applications designed for/with Universal Robots robotic arms.


## Documentation and usage
### Documentation
An exhaustive documentation of all the project can be found in the [project report](https://github.com/jmtc7/URrobot_alternative_programming_method_proposal/blob/master/documentation/report.pdf). A shorter version of it is in the [project presentation](https://github.com/jmtc7/URrobot_alternative_programming_method_proposal/blob/master/documentation/presentation.pdf). Even both of them are in Spanish, the next README sections are an overview of the project in English.

### Usage
In order to use this project, an Universal Robots robotic arm is needed, as well as a tool similar to the one proposed (with a camera and a distance sensor connected to a Raspberry Pi. The robot must be executing the [proposed robot program](https://github.com/jmtc7/URrobot_alternative_programming_method_proposal/tree/master/source_code/ur_program). Note that it is advisable to lower the robot velocity from the command pallete to be able to do a first test run safely. The tool must be connected to the robot so that it can write in its registers via Modbus TCP. Finally, a target will be needed, which consists in a green triangle that can be sticked in the tool which have to be followed.

Once having everything setted up as explained, the *programar.py* script should be executed in the tool. It will make the robot follow the target and store the corrections in a file named *correcciones.txt*. Once the desired trajectory is finished, the execution of this script must be stopped. Next, the robot can be moved to the desired point where we want it to start the trajectory and execute the *reproducir.py* script in the tool, which will read the corrections file and make the robot perform the programmed movements relative to the chosen start position.


## 3D case
I started attaching just the Raspberry and a camera to the wirst of the robot using flanges and adhesive tape to make some initial test and trials. I then developed a really simple 3D printed mounting that made it possible a more solid (yet **provisional**) attach between the robot and the two devices mentioned before. This mounting was composed by this two plates:
<p align="center">
  <img src="/multimedia/3d_case/older_versions/v1_downView.png" width="330" /> 
  <img src="/multimedia/3d_case/older_versions/v1_upperView.png" width="400" />
</p>

Then, after advancing with the code, I started designing a **final version of a new case**. It will be adapted to the needs I met during the developement (such as including a distance sensor) and, obviously, will include general improvements such as a more aesthetic finish, more protection, ventilation, better and more solid coupling:
<p align="center">
  <img src="/multimedia/3d_case/real_full_downView.jpg" width="400" />
  <img src="/multimedia/3d_case/real_bottomPlate_empty.jpg" width="400" />
</p>

<p align="center">
  <img src="/multimedia/3d_case/full_separated.png" width="500" /> 
</p>


## Scripts
### Software in the tool
As mentioned in the introduction, in the tool, two Python scripts will be executed in the Raspberry Pi: *programar.py* and *reproducir.py*, both of them contained in the *source_code* folder.

* ***programar.py*** tracks the centroid of the biggest green triangle perceived by the camera. I convert to HSV, threshold and use the Ramer-Douglas-Peucker algorithm to classify shapes. Then, the neeeded cartesian corrections to center the centroid in the frame are calculated. Finally, they are sent to the robot (which will solve the inverse-kinematics to reach the new target) and written into a corrections file named *correcciones.txt* that will be used by the other script to reproduce the trajectory..

* ***reproducir.py***. This script does the same as *programar.py* but substituting the computer vision and corrections calculation for just reading a line of the corrections file *correcciones.txt*. The aquired data is then sent to the robot so that it will behave as it did during the programming phase.

### Software in the robot
Appart of these scripts runned on the tool, the robot has to be always processing the messages that it receive via Modbus TCP. This is done by the **7_4_pruebas_modbus** program, also contained in the *source_code* folder. This program will get the correction provided by the tool software using the robot's Modbus TCP registers and move the arm accordingly.
