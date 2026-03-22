import os
from typing import Dict, Any
import json
import cv2
import numpy as np

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("WARNING: google.generativeai package not found. Run 'pip install google-generativeai'")


class CrowdSafetyLLM:
    """
    Core Agentic Execution Layer - Step 6 & 7.
    Combines the raw Anonymized Frame with structured JSON telemetry (velocity,
    density, anomalies) to generate a Human-Readable Risk Assessment and Action Plan.
    """
    def __init__(self, api_key: str = None):
        # Hardcoding the provided hackathon API key
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "AIzaSyBgAzwFSZcx_Fp28P7BCOqxH72kH2FeZFI")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_scene(self, anonymized_frame: np.ndarray, telemetry_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Takes the heavily structured JSON outputs from core/anomaly.py and core/risk.py
        and passes it alongside the anonymized visual to a VLM (Vision Language Model).
        """
        if not self.model:
            return {
                "reasoning": "[Mock] Simulated Cynefin probing. The density in Gateway A is rapidly increasing while average velocity has dropped by 30%, indicating a severe flow conflict.",
                "description": "[Mock] High density observed near Gateway A causing critical slowdowns.",
                "risk_level": "High",
                "action": "[Mock] Reroute inbound foot traffic to Gate B and broadcast delay warnings."
            }
            
        # Encode frame as JPEG byte array for Gemini
        success, buffer = cv2.imencode('.jpg', anonymized_frame)
        if not success:
            raise ValueError("Could not encode image")
            
        image_part = {
            "mime_type": "image/jpeg",
            "data": buffer.tobytes()
        }
        
        system_prompt = """
        You are an expert Security & Crowd Flow Analyst operating under the Cynefin Management Framework.
        You will receive an image of the live CCTV feed (faces are blurred for privacy) and a JSON payload of live instrumentation parameters (risk scores, detected anomalies, average velocity).
        
        TASK:
        Act as the ultimate Causal Inference Engine. Synthesize the visual crowd density with the objective telemetry data to prevent a crowd crush or severe bottleneck.
        
        OUTPUT FORMAT:
        You must output EXACTLY valid JSON matching the following schema:
        {
            "reasoning": "A 1-2 sentence chain-of-thought analyzing the hard telemetry against the visual evidence to establish causal inference.",
            "description": "A 1-sentence concise description of the crowd state suitable for an operator.",
            "risk_level": "Low" | "Medium" | "High" | "Critical",
            "action": "The highly specific, prescriptive operational command (e.g., 'Deploy staff to Gate B', 'Broadcast platform delay warning to Zone 2')."
        }
        """

        user_message = f"Live Telemetry Data from Core Sensors:\n```json\n{json.dumps(telemetry_data, indent=2)}\n```\n\nAnalyze the image and metrics to provide the security action plan."

        try:
            response = self.model.generate_content(
                [system_prompt, image_part, user_message],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            content = response.text
            return json.loads(content)
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "reasoning": "Failed to connect or parse response from Gemini API.",
                "description": "API Connection Error.",
                "risk_level": "Unknown",
                "action": "Check API key and network connection."
            }
