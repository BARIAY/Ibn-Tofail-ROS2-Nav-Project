import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from rclpy.qos import qos_profile_sensor_data
from ultralytics import YOLO

class VisionClassifier(Node):
    def __init__(self):
        super().__init__('vision_classifier')
        self.bridge = CvBridge()
        self.latest_frame = None 
        
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            qos_profile_sensor_data)
        
        self.get_logger().info('Nœud IA prêt. En attente du flux Gazebo...')

    def listener_callback(self, data):
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Erreur : {e}')

def main(args=None):
    rclpy.init(args=args)
    node = VisionClassifier()
    
    cv2.namedWindow("Camera TurtleBot3 - RTR", cv2.WINDOW_AUTOSIZE)
    
    print("Chargement du cerveau sur mesure (best.pt)...")

    model = YOLO("/home/hajar/rtr_ws/best.pt") 
    print("Modèle chargé ! Démarrage de la détection experte...")
    
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            
            if node.latest_frame is not None:
                frame = node.latest_frame.copy()
                
                # Inférence avec ton modèle. La confiance est remontée à 60% !
                results = model(frame, conf=0.20, verbose=False)
                
                # Dessin automatique des boîtes
                annotated_frame = results[0].plot()
                
                cv2.imshow("Camera TurtleBot3 - RTR", annotated_frame)
                
            cv2.waitKey(1)
            
    except KeyboardInterrupt:
        print("Arrêt demandé par l'utilisateur.")
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
