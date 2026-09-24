#  Copyright (c) 2025 Franka Robotics GmbH
#  Modified for Dynamic Configuration Architecture
############################################################################

import os
import sys
import logging
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

package_share = get_package_share_directory('franka_launch')
utils_path = os.path.join(package_share, '..', '..', 'lib', 'franka_launch', 'utils')
sys.path.append(os.path.abspath(utils_path))
from launch_utils import (  # noqa: E402
    load_overrides,
    load_yaml,
    merge_overrides,
    resolve_bool_override,
)

logging.root.setLevel(logging.INFO)


def generate_robot_nodes(context):
    nodes = []
    # loads dfki_bimanual.yaml
    config_file = LaunchConfiguration('robot_config_file').perform(context)
    print(config_file)

    configs = load_yaml(config_file)
    overrides_file = LaunchConfiguration('overrides_file').perform(context)
    overrides = load_overrides(overrides_file)

    spawn_franka_left = resolve_bool_override(
        overrides,
        'spawn_franka_left',
        LaunchConfiguration('spawn_franka_left').perform(context),
        True,
    )
    spawn_franka_right = resolve_bool_override(
        overrides,
        'spawn_franka_right',
        LaunchConfiguration('spawn_franka_right').perform(context),
        True,
    )
    use_fake_hardware = resolve_bool_override(
        overrides,
        'use_fake_hardware',
        LaunchConfiguration('use_fake_hardware').perform(context),
        False,
    )

    spawn_robots = []
    if spawn_franka_left:
        spawn_robots.append('franka_left')
    if spawn_franka_right:
        spawn_robots.append('franka_right')

    for item_name, config in configs.items():
        if item_name in spawn_robots:
            print('Spawn', item_name)
            config = merge_overrides(config, overrides_file, item_name)
            namespace = config['namespace']

            launch_kwargs = {
                'robot_config': str(config['robot_config']),
                'namespace': str(namespace),
                'robot_ip': str(config['robot_ip']),
                'use_fake_hardware': str(use_fake_hardware).lower(),
                'overrides_file': overrides_file,
            }
            if 'end_effector_frame' in config:
                launch_kwargs['end_effector_frame'] = str(config['end_effector_frame'])
            if 'gripper_port' in config:
                launch_kwargs['gripper_port'] = str(config['gripper_port'])

            nodes.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        PathJoinSubstitution(
                            [FindPackageShare('franka_launch'), 'launch', 'franka.launch.py']
                        )
                    ),
                    launch_arguments=launch_kwargs.items(),
                )
            )
    rviz_file = os.path.join(
        get_package_share_directory('franka_launch'), 'rviz', 'visualize_franka.rviz'
    )
    nodes.append(
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['--display-config', rviz_file, '-f', 'world'],
        )
    )

    return nodes


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'robot_config_file',
                default_value=PathJoinSubstitution(
                    [FindPackageShare('franka_launch'), 'config', 'dfki_bimanual.yaml']
                ),
                description='Path to the dynamic robot configuration file to load',
            ),
            DeclareLaunchArgument(
                'spawn_franka_left',
                default_value='',
                description='Spawn franka left (defaults to overrides file, then true)',
            ),
            DeclareLaunchArgument(
                'spawn_franka_right',
                default_value='',
                description='Spawn franka right (defaults to overrides file, then true)',
            ),
            DeclareLaunchArgument(
                'use_fake_hardware',
                default_value='',
                description='Use fake hardware (defaults to overrides file, then false)',
            ),
            DeclareLaunchArgument(
                'overrides_file',
                default_value='',
                description='Path to a robot_overrides.yaml that overrides per-arm config keys',
            ),
            OpaqueFunction(function=generate_robot_nodes),
        ]
    )
