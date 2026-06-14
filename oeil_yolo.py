#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class OeilIntelligent(Node):
    def __init__(self):
        super().__init__('oeil_yolo_node')
        self.bridge = CvBridge()
        
        self.get_logger().info(" Chargement du réseau de neurones YOLOv8...")
        # On charge TON modèle entraîné (vérifie que le chemin est correct)
        self.model = YOLO('/home/hajar/rtr_ws/best.pt') 
        self.get_logger().info(" IA chargée ! J'ouvre les yeux...")

        # Abonnement au flux vidéo du robot Waffle
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

    def image_callback(self, msg):
        try:
            # 1. Convertir l'image ROS (capteur) en image exploitable par OpenCV/YOLO
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 2. Faire l'inférence : l'IA cherche les déchets
            # verbose=False permet de ne pas spammer le terminal
            results = self.model(cv_image, verbose=False) 
            
            # 3. Dessiner les "Bounding Boxes" (boîtes englobantes) et les labels
            annotated_frame = results[0].plot()
            
            # 4. Afficher le résultat en direct
            cv2.imshow("Vision du Robot (YOLOv8)", annotated_frame)
            cv2.waitKey(1)
            
            # (Bonus) Extraire ce qu'il a vu pour la future prise de décision
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                if confidence > 0.60: # Si l'IA est sûre à plus de 60%
                    self.get_logger().info(f" Déchet repéré : {class_name} (Confiance: {confidence:.2f})")
            
        except Exception as e:
            self.get_logger().error(f"Erreur de vision : {e}")

def main(args=None):
    rclpy.init(args=args)
    node = OeilIntelligent()
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
