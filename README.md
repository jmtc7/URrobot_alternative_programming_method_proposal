# URrobot_alternative_programming_method_proposal
This project's objective is not to create a real full-operative alternative to the current programming methods for industrial robots but to propose an idea developing a minimal prototype to show that it is could be a possible alternative.

The project has 2 main parts:
* **3D-printable case** to contain and protect the Raspberry Pi, a camera, a distance sensor and a fan. It also makes it possible to attach the whole system to the UR robot wirst
* Python **scripts** to program the robot and make it able to replay the teached movements

# 3D case
I started attaching just the Raspberry and a camera to the wirst of the robot using flanges and adhesive tape to make some initial test and trials. I then developed a really simple 3D printed mounting that made it possible a more solid (yet provisional) attach between the robot and the two devices mentioned before. This mounting was composed by this two plates:
<p float="left">
  <img src="/multimedia/3d_case/older_versions/v1_upperView.png" width="100" />
  <img src="/multimedia/3d_case/older_versions/v1_downView.png" width="100" /> 
</p>
![upper_view](https://github.com/jmtc7/URrobot_alternative_programming_method_proposal/blob/master/multimedia/3d_case/older_versions/v1_upperView.png "Upper view") ![down_view](https://github.com/jmtc7/URrobot_alternative_programming_method_proposal/blob/master/multimedia/3d_case/older_versions/v1_downView.png "Down view")

Then, after advancing with the code, I started designing a final version of a new case. It will be adapted to the needs I met during the developement (such as including a distance sensor) and, obviously, will include general improvements such as a more aesthetic finish, more protection, ventilation, better and more solid coupling:

