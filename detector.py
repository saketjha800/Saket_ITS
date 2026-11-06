import cv2
import numpy as np
import random
from ultralytics import YOLO

class TrafficDetector:
    def __init__(self, model_path='model/yolov8n.pt'):
        self.model = YOLO(model_path)
        self.issued_chalans = set()
        
    def process_frame(self, frame, frame_number):
        # Conf=0.25 aur imgsz=416 par fast aur accurate detection
        results = self.model.track(frame, persist=True, stream=False, verbose=False, conf=0.25, imgsz=416)
        
        emergency_detected = False
        chalan_records = []
        frame_vehicles = 0
        frame_emergencies = 0
        
        annotated_frame = results[0].plot()
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls].lower()
                    
                    # Vehicle classes check (car, motorcycle, bus, truck, bicycle)
                    if cls in [1, 2, 3, 5, 7] or any(v in class_name for v in ['car', 'bus', 'truck', 'motorcycle', 'vehicle']):
                        track_id = int(box.id[0]) if box.id is not None and box.id.nelement() > 0 else random.randint(1000, 9999)
                        frame_vehicles += 1
                        
                        # Coordinates nikalein bounding box ke liye
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # --- RED LIGHT / EMERGENCY BEACON DETECTION LOGIC ---
                        # Vehicle ke upper half (roof area) mein red color check karenge (ambulance ki top red light ke liye)
                        h, w, _ = frame.shape
                        roi_y1 = max(0, y1)
                        roi_y2 = max(0, min(h, y1 + int((y2 - y1) * 0.4))) # top 40% area of vehicle
                        roi_x1 = max(0, x1)
                        roi_x2 = max(0, min(w, x2))
                        
                        is_emergency = False
                        if roi_y2 > roi_y1 and roi_x2 > roi_x1:
                            vehicle_roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
                            hsv = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2HSV)
                            
                            # Red color range in HSV
                            lower_red1 = np.array([0, 120, 70])
                            upper_red1 = np.array([10, 255, 255])
                            lower_red2 = np.array([170, 120, 70])
                            upper_red2 = np.array([180, 255, 255])
                            
                            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                            red_mask = mask1 | mask2
                            
                            # Agar roof par red pixels kaafi zyada hain, toh matlab emergency light jal rahi hai
                            red_pixel_count = cv2.countNonZero(red_mask)
                            if red_pixel_count > 15: # threshold for red light detection
                                is_emergency = True
                        
                        # Fallback keyword check
                        if 'ambulance' in class_name or 'emergency' in class_name:
                            is_emergency = True
                            
                        if is_emergency:
                            emergency_detected = True
                            frame_emergencies += 1
                            # Visual highlight for emergency vehicle on annotated frame
                            cv2.putText(annotated_frame, "EMERGENCY LIGHT DETECTED", (x1, max(20, y1 - 10)), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            
                        seed_val = int(str(track_id)) if str(track_id).isdigit() else 100
                        random.seed(seed_val)
                        mock_speed = random.randint(80, 145)
                        
                        # Over-speeding chalan logic for normal vehicles
                        if not is_emergency and mock_speed > 130:
                            if track_id not in self.issued_chalans:
                                self.issued_chalans.add(track_id)
                                chalan_records.append({
                                    "Vehicle": class_name.capitalize(),
                                    "Vehicle ID": f"ID-{track_id}",
                                    "Speed": f"{mock_speed} km/h",
                                    "Limit": "130 km/h",
                                    "Fine": "₹2,000",
                                    "Status": "Issued"
                                })
                                
        return annotated_frame, frame_vehicles, frame_emergencies, emergency_detected, chalan_records