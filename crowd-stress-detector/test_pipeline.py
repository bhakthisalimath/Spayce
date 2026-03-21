import cv2
import time
from core.detector import PersonDetector, draw_detections
from core.llm_agent import CrowdSafetyLLM

# Hardcode a mock telemetry payload mimicking anomaly.py/risk.py
MOCK_TELEMETRY = {
    "current_risk_score": 0.85,
    "zone_anomalies": [
        {"zone_id": "Gateway A", "density_anomaly": True, "flow_conflict": True}
    ],
    "average_velocity": -1.2, # Slowed down significantly
    "predicted_risk_10s": 0.95
}

def test_agent_pipeline():
    print("Initializing Pipeline...")
    detector = PersonDetector("yolov8n.pt")
    llm = CrowdSafetyLLM() # Uses mock unless OPENAI_API_KEY is exported
    
    print("Grabbing sample frame for test...")
    video_path = r"data\sample_videos\4sec_GOOD_ANGLE_demo.mp4"
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    
    if not ret:
        print(f"Could not read test video: {video_path}")
        return
    
    print("Step 2: YOLO Person Detection...")
    start_t = time.time()
    detections = detector.detect_people(frame)
    
    print(f"Step 3 & 4: Privacy Face Blurring ({len(detections)} people)...")
    anonymized_frame = draw_detections(frame, detections, anonymize=True)
    
    # Save local image to verify blur works visually
    cv2.imwrite("test_anonymized_output.jpg", anonymized_frame)
    print(f"--> Wrote test frame to test_anonymized_output.jpg (Open it to see the blur!)")
    
    print("Step 6: LLM Execution Layer Synthesis...")
    llm_result = llm.analyze_scene(anonymized_frame, MOCK_TELEMETRY)
    
    print("\n===========================")
    print(" 🤖 LLM HACKATHON OUTPUT ")
    print("===========================")
    print(f"📝 Description: {llm_result.get('description', 'N/A')}")
    print(f"⚠️  Risk Level: {llm_result.get('risk_level', 'N/A')}")
    print(f"🛠️  Command/Action: {llm_result.get('action', 'N/A')}")
    print("===========================\n")
    
if __name__ == '__main__':
    test_agent_pipeline()
