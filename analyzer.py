import os
import json
import logging
from PIL import Image
from google import genai
from google.genai import types
from config import SYSTEM_PROMPT, GEMINI_MODEL, REPORTS_DIR

logger = logging.getLogger(__name__)

class AnalystEngine:
    def __init__(self):
        try:
            self.client = genai.Client()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}. Make sure GOOGLE_API_KEY is set.")
            self.client = None
            
        self.crops_dir = os.path.join(REPORTS_DIR, "screenshots", "crops")
        os.makedirs(self.crops_dir, exist_ok=True)

    def crop_evidence(self, original_path: str, domain_name: str, indicators: list) -> list:
        processed_indicators = []
        try:
            with Image.open(original_path) as img:
                width, height = img.size
                
                for idx, indicator in enumerate(indicators):
                    box = indicator.get("bounding_box_1000")
                    if box and len(box) == 4 and box != [0,0,0,0]:
                        # Normalize coordinates
                        ymin, xmin, ymax, xmax = box
                        # convert 0-1000 bounds to pixel values
                        # box format array: [ymin, xmin, ymax, xmax] 
                        # PIL crop format: (left, upper, right, lower) -> (px_xmin, px_ymin, px_xmax, px_ymax)
                        px_xmin = int((xmin / 1000.0) * width)
                        px_ymin = int((ymin / 1000.0) * height)
                        px_xmax = int((xmax / 1000.0) * width)
                        px_ymax = int((ymax / 1000.0) * height)
                        
                        try:
                            cropped_img = img.crop((px_xmin, px_ymin, px_xmax, px_ymax))
                            crop_filename = f"{domain_name}_evidence_{idx}.png"
                            crop_path = os.path.join(self.crops_dir, crop_filename)
                            cropped_img.save(crop_path)
                            indicator["local_crop_path"] = crop_path
                        except Exception as crop_err:
                            logger.error(f"Failed to crop image for {domain_name} at index {idx}: {crop_err}")
                            indicator["local_crop_path"] = None
                    else:
                        indicator["local_crop_path"] = None
                        
                    processed_indicators.append(indicator)
        except Exception as file_err:
             logger.error(f"Failed to open original screenshot {original_path} for cropping: {file_err}")
             return indicators
             
        return processed_indicators

    def analyze_domain(self, domain_data: dict, domain_name: str) -> dict:
        """Analyzes the domain data and screenshot using Gemini."""
        if not self.client:
            return {"executive_summary": "Error: Gemini API Client not initialized.", "technical_analysis": "", "threat_indicators": []}

        if domain_data.get("error") or not domain_data.get("screenshot_path"):
            return {"executive_summary": "Could not analyze due to scanning error or missing screenshot.", "technical_analysis": "", "threat_indicators": []}

        screenshot_path = domain_data["screenshot_path"]
        
        context = {
            "url": domain_data["url"],
            "device_emulated": domain_data["device_emulated"],
            "downloads_detected": domain_data["downloads_detected"],
            "suspicious_requests": domain_data["suspicious_requests"]
        }
        
        prompt = (
            f"Here is a screenshot of the website '{domain_data['url']}' visited on a {domain_data['device_emulated']}. "
            f"Additional network context: {json.dumps(context, indent=2)}\n\n"
            "Please provide your analyst description strictly following the SYSTEM_PROMPT. "
            "Output your response strictly as raw JSON matching the required schema. Do NOT include markdown code blocks like ```json."
        )

        try:
            logger.info(f"Uploading file {screenshot_path} to Gemini...")
            myfile = self.client.files.upload(file=screenshot_path)
            
            logger.info(f"Generating content for {domain_data['url']}...")
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Content(role="user", parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_uri(file_uri=myfile.uri, mime_type="image/png"),
                    ])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            try:
                self.client.files.delete(name=myfile.name)
            except Exception as cleanup_err:
                 logger.debug(f"Could not delete file {myfile.name}: {cleanup_err}")

            raw_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            
            try:
                result_json = json.loads(raw_text)
                
                # Crop images based on bounding boxes
                if "threat_indicators" in result_json and isinstance(result_json["threat_indicators"], list):
                    result_json["threat_indicators"] = self.crop_evidence(
                        screenshot_path, domain_name, result_json["threat_indicators"]
                    )
                    
                return result_json
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response for {domain_name}. Raw text: {raw_text}")
                return {"executive_summary": "Parsing Error", "technical_analysis": raw_text, "threat_indicators": []}

        except Exception as e:
            logger.error(f"Gemini Analysis failed for {domain_data['url']}: {e}")
            return {"executive_summary": f"Error during AI analysis: {str(e)}", "technical_analysis": "", "threat_indicators": []}
