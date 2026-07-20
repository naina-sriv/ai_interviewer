import os
import json
from typing import Dict, Optional
from models.interview import InterviewSession

class SessionStore:
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL")
        self.redis_client = None
        self.local_dict: Dict[str, InterviewSession] = {}

        if self.redis_url:
            import redis
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                print("Connected to Redis successfully.")
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")
                self.redis_client = None

    def save_session(self, session: InterviewSession):
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"session:{session.session_id}",
                    86400,
                    session.model_dump_json()
                )
                return
            except Exception as e:
                print(f"Redis save failed, using local storage: {e}")
        self.local_dict[session.session_id] = session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        if self.redis_client:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                if data:
                    return InterviewSession.model_validate_json(data)
            except Exception as e:
                print(f"Redis get failed, using local storage: {e}")
        return self.local_dict.get(session_id)

# Global instance
session_store = SessionStore()
