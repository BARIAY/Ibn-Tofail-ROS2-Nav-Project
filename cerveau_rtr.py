#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import time

def main():
    # Initialisation de ROS 2
    rclpy.init()
    
    # Création du "Commander" qui va parler à Nav2
    navigator = BasicNavigator()

    print(" Attente de l'activation de Nav2...")
    navigator.waitUntilNav2Active()
    print(" Cerveau en ligne. Début de la Mission de Tri.")

    # ==========================================
    # ÉTAPE 1 : ALLER CHERCHER LA CANETTE
    # ==========================================
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    
    # Coordonnées D'APPROCHE (juste devant la canette)
    goal_pose.pose.position.x = 1.0  # <-- MODIFIÉ ICI (1.0 au lieu de 1.5)
    goal_pose.pose.position.y = 0.3
    goal_pose.pose.orientation.w = 1.0 

    print(" ORDRE : Navigation vers Canette 1 [Point d'approche X: 1.0, Y: 0.3]")
    navigator.goToPose(goal_pose)

    # Boucle d'attente pendant que le robot roule
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        # On pourrait afficher la distance restante ici si besoin
        pass

    # Vérification du résultat
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print(" SUCCÈS : Arrivé sur la canette.")
        print(" [Action Matérielle] : Aspiration virtuelle en cours...")
        time.sleep(3) # Simulation du temps de ramassage
        print(" Canette sécurisée dans le robot !")
    else:
        print(" ÉCHEC : Impossible d'atteindre la canette.")
        return # On stoppe la mission

    # ==========================================
    # ÉTAPE 2 : LIVRER AU BAC PLASTIQUE (JAUNE)
    # ==========================================
    drop_pose = PoseStamped()
    drop_pose.header.frame_id = 'map'
    drop_pose.header.stamp = navigator.get_clock().now().to_msg()
    
    # Coordonnées du drop-off (Bac Jaune)
    drop_pose.pose.position.x = 3.5
    drop_pose.pose.position.y = 3.5
    # w=1.0 signifie que le robot regardera vers l'Est (face au mur des bacs)
    drop_pose.pose.orientation.w = 1.0 

    print(" ORDRE : Transport vers le Bac Plastique [X: 3.5, Y: 3.5]")
    navigator.goToPose(drop_pose)

    while not navigator.isTaskComplete():
        pass

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print(" SUCCÈS : Arrivé devant le bac de tri.")
        print(" [Action Matérielle] : Dépôt virtuel en cours...")
        time.sleep(2)
        print(" MISSION ACCOMPLIE : Déchet trié avec succès !")
    else:
        print(" ÉCHEC : Impossible d'atteindre le bac.")

    # Fin du programme
    rclpy.shutdown()

if __name__ == '__main__':
    main()
