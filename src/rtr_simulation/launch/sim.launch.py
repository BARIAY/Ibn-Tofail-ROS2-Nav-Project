import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_share = get_package_share_directory('rtr_simulation')
    tb3_share = get_package_share_directory('turtlebot3_description')


    set_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(tb3_share, '..')
    )

    # Charger Wrapper
    xacro_file = os.path.join(pkg_share, 'urdf', 'tb3_harmonic.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Charger le monde avec les déchets Gazebo Fuel
    world_file = os.path.join(pkg_share, 'worlds', 'rtr_environment.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'{world_file} -r '}.items()
    )

    # 4. Faire apparaître le robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'turtlebot3',
                   '-z', '0.1'],
        output='screen'
    )

    # 4. Faire apparaître le robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'turtlebot3',
                   '-z', '0.1'],
        output='screen'
    )

    # 5. LE PONT VIDÉO (Gazebo -> ROS2)
    bridge_camera = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],  # <-- Le fameux slash est de retour !
        output='screen'
    )

    return LaunchDescription([
        set_model_path,
        node_robot_state_publisher,
        gazebo,
        spawn_entity
    ])
