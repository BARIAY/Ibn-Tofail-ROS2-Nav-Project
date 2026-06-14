# Ibn Tofail ROS 2 Autonomous Waste Sorting Robot

[![ROS 2](https://img.shields.io/badge/ROS2-Jazzy_Jalisco-blue?style=flat&logo=ros)](https://docs.ros.org/en/jazzy/index.html)
[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange?style=flat)](https://gazebosim.org/home)
[![Python](https://img.shields.io/badge/Python-3.12-yellow?style=flat&logo=python)](https://www.python.org/)

Ce projet est développé dans le cadre du module de **Systèmes Temps Réel (STR)** par l'équipe **RTR Real-Time Rangers**. L'objectif est de concevoir un robot mobile capable d'identifier, de classifier et de trier des déchets de manière autonome dans un environnement simulé. 

Le projet explore l'intégration de l'Intelligence Artificielle avec des contraintes de programmation en temps réel strictes via le framework ROS 2.

##  L'Équipe (RTR Real-Time Rangers)
Projet académique de fin d'études d'ingénierie réalisé au sein du département de technologie de l'**Université Ibn Tofail** (Filière : Master Intelligence Artificielle et Objets Connectés).

* **TAFTAF Aya** * **BOUIH Hajar** * **BARI Aymane** ---

## Caractéristiques Principales

* **Navigation & Routage (Nav2) :** Utilisation de l'API `BasicNavigator` (**Nav2 Simple Commander**) pour planifier des trajectoires optimales et fluides vers les bacs de tri.
* **Perception IA Temps Réel (Firm RTS) :** Intégration d'un modèle **YOLOv8 Nano** ré-entraîné pour classifier et localiser les déchets (Recyclables vs Dangereux) via le flux caméra.
* **Asservissement Visuel (Hard RTS) :** Phase d'approche finale gérée par un contrôleur proportionnel direct sur les moteurs (`/cmd_vel`) pour éviter les collisions physiques avec les objets.
* **Gestion Dynamique des Costmaps :** Purge systématique de la mémoire d'obstacles de Nav2 (`clearAllCostmaps()`) dès qu'un déchet est collecté.
* **Interaction Physique Virtuelle :** Aspiration du modèle 3D du déchet par appels système asynchrones à l'API de services de Gazebo.

---

## Architecture de l'Espace de Travail

L'espace de travail (`rtr_ws`) respecte scrupuleusement les standards de développement ROS 2 :

```text
rtr_ws/                                  # Racine du workspace ROS 2
│
├── best.pt                              # Poids du modèle YOLOv8 ré-entraîné (PyTorch)
├── cerveau_autonome.py                  # Script principal : Vision, FSM et Routage
├── dataset_collector.py                 # Utilitaire de collecte de données
├── ma_carte.yaml                        # Configuration de la carte statique 2D
├── ma_carte.pgm                         # Image 2D de la baie de tri
│
└── src/                                 # Répertoire des packages sources
    └── rtr_simulation/                  # Package principal de la simulation
        ├── package.xml                  # Manifeste des dépendances
        ├── CMakeLists.txt               # Instructions de build CMake
        ├── launch/
        │   └── sim.launch.py            # Allumage global (Robot + Gazebo + Rviz2)
        └── worlds/
            └── rtr_world.sdf            # Environnement 3D (Murs, bacs, déchets)

## Installation (Prérequis)
OS : Ubuntu 24.04 LTS (Noble Numbat)
ROS Version : ROS 2 Jazzy Jalisco
Simulateur : Gazebo Harmonic

pip3 install ultralytics opencv-python cv-bridge --user --break-system-packages

## Exécution du Système

## 1. Lancement de la Simulation
cd ~/rtr_ws
source install/setup.bash
ros2 launch rtr_simulation sim.launch.py

## 2. Activation du Pont de Communication (Bridge)
ros2 run ros_gz_bridge parameter_bridge \
/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock \
/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan \
/model/turtlebot3/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry \
/model/turtlebot3/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V \
/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist \
/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image \
--ros-args -r /model/turtlebot3/odometry:=/odom -r /model/turtlebot3/tf:=/tf

## 3. Démarrage de la Stack de Navigation (Nav2)
ros2 launch nav2_bringup bringup_launch.py use_sim_time:=true map:=/home/hajar/rtr_ws/ma_carte.yaml

## 4. Initialisation de la Pose du Robot (AMCL)
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -4.0, y: 0.3, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}"

## 5. Lancement du Nœud de Vision IA
python3 ~/rtr_ws/src/rtr_vision/rtr_vision/vision_classifier.py

## 6. Activation du Cerveau Autonome
python3 ~/rtr_ws/cerveau_autonome.py
