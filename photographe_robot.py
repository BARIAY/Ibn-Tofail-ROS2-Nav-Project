#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from datetime import datetime

class PhotographeNode(Node):
    def __init__(self):
        super().__init__('photographe_node')
        self.bridge = CvBridge()
        
        # Création automatique du dossier pour ton dataset
        self.save_dir = os.path.expanduser('~/rtr_ws/dataset_gazebo/images')
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.get_logger().info("=========================================")
        self.get_logger().info(f" Appareil photo en ligne !")
        self.get_logger().info(f" Les images seront dans : {self.save_dir}")
        self.get_logger().info(" Règle d'or : Garde la fenêtre vidéo sélectionnée")
        self.get_logger().info(" Appuie sur la touche 's' pour prendre une photo")
        self.get_logger().info("=========================================")

        # Abonnement aux yeux du Waffle
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        
        self.image_count = 0

    def image_callback(self, msg):
        try:
            # Conversion pour OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Affichage de la fenêtre
            cv2.imshow("Viseur du Robot (Appuie sur 's' pour shooter)", cv_image)
            
            # Capture de la touche pressée (avec un délai de 1ms pour ne pas figer l'image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                # Création d'un nom de fichier unique basé sur l'heure exacte
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = os.path.join(self.save_dir, f"capture_{timestamp}.jpg")
                
                # Sauvegarde sur le disque dur
                cv2.imwrite(filename, cv_image)
                self.image_count += 1
                self.get_logger().info(f" Clic ! Photo #{self.image_count} sauvegardée.")
                
        except Exception as e:
            self.get_logger().error(f"Erreur de conversion vidéo : {e}")

def main(args=None):
    rclpy.init(args=args)
    node = PhotographeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
