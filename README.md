# Autonomous Waste Sorting Robot (ROS 2 Jazzy)

## 1. Présentation du Projet
Ce projet est développé dans le cadre du module de Systèmes Temps Réel par l'équipe **RTR Real-Time Rangers**. L'objectif est de concevoir un robot mobile capable d'identifier, de classifier et de trier des déchets de manière autonome dans un environnement simulé.

Le projet explore l'intégration de l'Intelligence Artificielle (Machine Learning) avec des contraintes de programmation en temps réel strictes via le framework ROS 2.

## 2. L'Équipe (RTR Real-Time Rangers)
* **TAFTAF Aya** 
* **BOUIH Hajar** 
* **BARI Aymane**


## 3. Architecture Logicielle
L'architecture est découpée en plusieurs nœuds pour garantir la prédictibilité et le respect des échéances (deadlines):
* **Vision & AI (Python) :** Classification des déchets (Recyclable vs Dangereux) via un modèle de reconnaissance d'objets (Firm RTS).
* **Navigation & Control (C++) :** Gestion du mouvement et arrêt de précision (Hard RTS) pour éviter les collisions physiques avec les objets.
* **Monitoring (C++) :** Surveillance de l'état du robot (Batterie et diagnostics) via le bridge Gazebo.



## 4. Installation
### Prérequis
* **OS :** Ubuntu 24.04 LTS (Noble Numbat)
* **ROS Version :** ROS 2 Jazzy Jalisco
* **Simulateur :** Gazebo Sim

### Configuration du Workspace
```bash
# Création de l'arborescence
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone du dépôt officiel
git clone [https://github.com/BARIAY/Ibn-Tofail-ROS2-Nav-Project.git](https://github.com/BARIAY/Ibn-Tofail-ROS2-Nav-Project.git) .

# Installation des dépendances
cd ~/ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```
## 5. Compilation et Lancement
### Build
```Bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### Exécution
Lancer la simulation (Gazebo) :
```Bash
gz sim diff_drive.sdf
```

Lancer le nœud de monitoring :
```Bash
ros2 run robot_monitor monitor_node
```
## 6. Livrables et Calendrier 


Project Proposal : Document de 1-2 pages détaillant les objectifs.


GitHub Repository : Code source complet et historique des commits.


Final Report : Rapport détaillé de 10-20 pages sur l'efficacité du modèle ML et les performances temps réel.


Demo & Presentation : Présentation de 10-15 minutes incluant une démonstration.
