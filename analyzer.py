import os
import json
import logging
from google import genai
from google.genai import types
from config import SYSTEM_PROMPT, GEMINI_MODEL

logger = logging.getLogger(__name__)

class AnalystEngine:
    def __init__(self):
        # We assume the user has GOOGLE_API_KEY exported in their environment
        try:
            self.client = genai.Client()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}. Make sure GOOGLE_API_KEY is set.")
            self.client = None

    def analyze_domain(self, domain_data: dict) -> dict:
        """Analyzes the domain data and screenshot using Gemini."""
        if not self.client:
            return {"analysis": "Error: Gemini API Client not initialized.", "caption": "No caption generated."}

        if domain_data.get("error") or not domain_data.get("screenshot_path"):
            return {"analysis": "Could not analyze due to scanning error or missing screenshot.", "caption": "Site unreachable"}

        screenshot_path = domain_data["screenshot_path"]
        
        # Prepare context from scanner
        context = {
            "url": domain_data["url"],
            "device_emulated": domain_data["device_emulated"],
            "downloads_detected": domain_data["downloads_detected"],
            "suspicious_requests": domain_data["suspicious_requests"]
        }
        
        prompt = (
            f"Here is a screenshot of the website '{domain_data['url']}' visited on a {domain_data['device_emulated']}. "
            f"Additional network context: {json.dumps(context, indent=2)}\n\n"
            "Please provide your analyst description and a short caption for this image following the system instructions. "
            "Output your response strictly in the following JSON format without any markdown code blocks: \n"
            '{\n  "caption": "<short descriptive caption for image>",\n  "analysis": "<detailed analyst description>"\n}'
        )

        try:
            logger.info(f"Uploading file {screenshot_path} to Gemini...")
            # We use the recommended standard file upload for genai
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
            
            # Clean up the file from Gemini storage
            try:
                self.client.files.delete(name=myfile.name)
            except Exception as cleanup_err:
                 logger.debug(f"Could not delete file {myfile.name}: {cleanup_err}")

            try:
                result_json = json.loads(response.text)
                return result_json
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response.text}")
                return {"analysis": response.text, "caption": "Analysis available"}

        except Exception as e:
            logger.error(f"Gemini Analysis failed for {domain_data['url']}: {e}")
            return {"analysis": f"Error during AI analysis: {str(e)}", "caption": "Analysis Error"}
