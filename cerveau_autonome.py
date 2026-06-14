#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import subprocess
import time
import threading
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped

# ==========================================
# CONFIGURATION DE CENTRE DE TRI
# ==========================================
# Tous les objets sont des "déchets" à trier.
BACS = {
    "canette": (2.5, 3.5),          
    "gobelet": (2.5, 3.5),          
    "bouteille_verre": (2.5, 1.5),  
    "bol": (2.5, 1.5),              
    "carton": (2.5, -0.5),          
    "boite_lettres": (2.5, -0.5),   
    "cone_chantier": (2.5, 3.5),    
    "extincteur": (2.5, 1.5)        
}

GAZEBO_MODELS = {
    "canette": ["canette_1", "canette_2", "canette_3", "Coke Can", "Coke Can_0", "Coke Can_1"],
    "gobelet": ["gobelet_1", "gobelet_2", "Plastic Cup", "Plastic Cup_0"],
    "bouteille_verre": ["bouteille_1", "bouteille_2", "Beer", "Beer_0"],
    "bol": ["bol_verre", "Bowl", "Bowl_0"],
    "carton": ["carton_1", "carton_2", "Cardboard Box", "Cardboard Box_0", "Cardboard Box_1"],
    "boite_lettres": ["boite_lettres", "Mailbox", "Mailbox_0"],
    "cone_chantier": ["cone_1", "cone_2", "cone_3", "Construction Cone", "Construction Cone_0", "Construction Cone_1", "Construction Cone_2"],
    "extincteur": ["extincteur_1", "Fire Extinguisher", "Fire Extinguisher_0"]
}

# ==========================================
# NŒUD DE VISION 
# ==========================================
class VisionSensor(Node):
    def __init__(self):
        super().__init__('vision_sensor')
        self.bridge = CvBridge()
        self.model = YOLO("/home/hajar/rtr_ws/best.pt")
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.camera_callback, 10)
        
        self.cible_detectee = False
        self.classe_cible = ""
        self.erreur_x = 0.0 
        self.taille_cible = 0 

    def camera_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            results = self.model(cv_image, conf=0.60, verbose=False)
            
            if len(results[0].boxes) > 0:
                box = results[0].boxes[0]
                classe_detectee = self.model.names[int(box.cls[0])]
                
                # TOUT ce qui est détecté est maintenant une cible légitime
                self.classe_cible = classe_detectee
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                centre_box_x = (x1 + x2) / 2
                
                self.taille_cible = (x2 - x1) * (y2 - y1)
                self.erreur_x = 320.0 - centre_box_x
                self.cible_detectee = True
                
                annotated_frame = results[0].plot()
                # --- On commente l'affichage ---
                # cv2.imshow("Vision Autonome", annotated_frame)
            else:
                self.cible_detectee = False
                # --- On commente l'affichage ---
                # cv2.imshow("Vision Autonome", cv_image)
                
            # --- On commente l'attente graphique ---
            # cv2.waitKey(1)
        except Exception as e:
            pass

# ==========================================
# LA MACHINE À ÉTATS PRINCIPALE
# ==========================================
def main():
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true'])
    
    vision_node = VisionSensor()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(vision_node)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    navigator = BasicNavigator()
    cmd_vel_pub = vision_node.create_publisher(Twist, '/cmd_vel', 10)
    
    print("\n" + "="*50)
    print("SYSTÈME END-TO-END OPÉRATIONNEL (Mode Sans Interface)")
    print("="*50 + "\n")
    
    while rclpy.ok():
        
        # --- ÉTAPE 1 : RECHERCHE ---
        print(" [MODE RECHERCHE] Scan de la zone en cours...")
        msg_vel = Twist()
        while not vision_node.cible_detectee:
            msg_vel.angular.z = 0.3 
            cmd_vel_pub.publish(msg_vel)
            time.sleep(0.1)
            
        msg_vel.angular.z = 0.0
        cmd_vel_pub.publish(msg_vel)
        
        classe = vision_node.classe_cible
        print(f" [CIBLE VERROUILLÉE] Déchet identifié : {classe.upper()}")
        
        # --- ÉTAPE 2 : APPROCHE VISUELLE ---
        print(f" [APPROCHE] Chasse de la cible en cours...")
        
        compteur_securite = 0
        while vision_node.cible_detectee and vision_node.taille_cible < 30000 and compteur_securite < 100:
            msg_vel = Twist()
            msg_vel.linear.x = 0.15 
            msg_vel.angular.z = vision_node.erreur_x * 0.002 
            cmd_vel_pub.publish(msg_vel)
            time.sleep(0.05)
            compteur_securite += 1
            
        msg_vel.linear.x = 0.0
        msg_vel.angular.z = 0.0
        cmd_vel_pub.publish(msg_vel)
        
        # --- ÉTAPE 3 : PRÉHENSION (Aspiration Gazebo) ---
        print("[ACTION] Aspiration du déchet...")
        modeles_possibles = GAZEBO_MODELS.get(classe, [])
        for nom in modeles_possibles:
            cmd = f"gz service -s /world/rtr_world/remove --reqtype gz.msgs.Entity --reptype gz.msgs.Boolean --timeout 1000 --req \"name: '{nom}', type: MODEL\""
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        
        # --- Manœuvre de Dégagement ---
        print("[SÉCURITÉ] Grand recul pour sortir de la zone de collision Nav2...")
        msg_vel = Twist()
        msg_vel.linear.x = -0.20
        cmd_vel_pub.publish(msg_vel)
        time.sleep(3.0) 
        
        msg_vel.linear.x = 0.0
        cmd_vel_pub.publish(msg_vel)
        
        # --- Nettoyage de la carte ---
        print("[NAV2] Nettoyage de la mémoire des obstacles...")
        navigator.clearAllCostmaps()
        time.sleep(1.5) 
        print("Déchet stocké et zone dégagée !")

        # --- ÉTAPE 4 : LIVRAISON ---
        if classe in BACS:
            cible_x, cible_y = BACS[classe]
            print(f" [LIVRAISON] Routage Nav2 vers le bac {classe} ({cible_x}, {cible_y})")
            
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            
            goal_pose.header.stamp.sec = 0
            goal_pose.header.stamp.nanosec = 0
            
            goal_pose.pose.position.x = float(cible_x)
            goal_pose.pose.position.y = float(cible_y)
            goal_pose.pose.orientation.w = 1.0 
            
            navigator.goToPose(goal_pose)
            
            while not navigator.isTaskComplete():
                time.sleep(0.5)
                
            print("[MISSION ACCOMPLIE] Déchet déposé.")
            print("Retour au mode Recherche dans 3 secondes...")
            print("--------------------------------------------")
            time.sleep(3)
        else:
            print(f" Bac inconnu pour la classe {classe}. Je reprends ma patrouille.")

if __name__ == '__main__':
    main()