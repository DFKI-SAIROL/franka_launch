# franka_launch

Launch files and configs for Franka FR3 robots (single and bimanual setups).

## Launch files

| File | Purpose |
|---|---|
| `example.launch.py` | Main entry point — launches one or both arms |
| `franka.launch.py` | Core Franka bringup (used by example) |
| `gripper.launch.py` | Launches a gripper independently |

## Launching the robot

```bash
ros2 launch franka_launch example.launch.py \
    robot_config_file:=dfki_bimanual \
    spawn_franka_left:=false \
    spawn_franka_right:=true \
    use_fake_hardware:=true
```

Config files are in `config/` (e.g. `dfki_bimanual.yaml`).

## Launching a gripper

Grippers are launched separately. Currently supported: Franka gripper and Robotis RH-P12-RN-A.

```bash
ros2 launch franka_launch gripper.launch.py arm_prefix:=franka_right
```

Test the Robotis gripper with a joint trajectory command (position range: 0.0–1.1):

```bash
ros2 topic pub --once /franka_right/gripper/gripper_controller/joint_trajectory \
    trajectory_msgs/msg/JointTrajectory \
    "{joint_names: ['franka_right_rh_r1'], points: [{positions: [0.5], time_from_start: {sec: 1, nanosec: 0}}]}"
```
