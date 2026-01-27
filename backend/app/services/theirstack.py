import requests
from typing import List, Optional
from app.core.config import settings

class TheirStackService:
    BASE_URL = "https://api.theirstack.com/v1"

    def __init__(self):
        self.api_key = settings.THEIRSTACK_API_KEY

    def search_jobs(
        self, 
        job_title_patterns: List[str] = [], 
        locations: List[str] = [],
        remote: Optional[bool] = None,
        limit: int = 10
    ) -> List[dict]:
        """
        Search for jobs using TheirStack API.
        """
        if not self.api_key:
            print("Warning: THEIR_STACK_API_KEY is not set.")
            return []

        url = f"{self.BASE_URL}/jobs/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "limit": limit,
            "posted_at_max_age_days": 30, # Default to last 30 days
            "job_title_or": job_title_patterns,
            # For locations, TheirStack uses country codes or location patterns. 
            # Ideally we'd map "New York" to a pattern or exact match.
            # Using job_location_pattern_or for flexible matching if locations provided
            "job_location_pattern_or": locations if locations else []
        }
        
        if remote:
            payload["remote"] = True

        print(f"DEBUG: TheirStack Request: URL={url}, Payload={payload}")

        try:
            response = requests.post(url, json=payload, headers=headers)
            # response.raise_for_status() # Let's see the error if any
            print(f"DEBUG: TheirStack Response Status: {response.status_code}")
            print(f"DEBUG: TheirStack Response Body: {response.text[:500]}...") # Print first 500 chars
            
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs from TheirStack: {e}")
            if response:
                print(response.text)
            return []

theirstack_service = TheirStackService()
