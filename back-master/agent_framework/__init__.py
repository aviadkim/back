"""
מסגרת סוכנים חכמים לניתוח מסמכים פיננסיים
"""

import logging
import os

logger = logging.getLogger(__name__)

# ייבוא הסוכנים החכמים
try:
    from .coordinator import AgentCoordinator
    logger.info("Agent framework initialized successfully")
except ImportError as e:
    logger.warning(f"Failed to import agent framework components: {e}")

# התחלת יצירת מופע גלובלי של מתאם הסוכנים
__coordinator_instance = None

def get_coordinator():
    """
    קבלת מופע גלובלי של מתאם הסוכנים
    
    Returns:
        AgentCoordinator: המופע הגלובלי של מתאם הסוכנים
    """
    global __coordinator_instance
    
    if __coordinator_instance is None:
        # טעינת קובץ הגדרות אם קיים
        models_config = {
            "default": os.environ.get("DEFAULT_MODEL", "gemini"),
            "available": ["gemini", "llama", "mistral"]
        }
        
        try:
            __coordinator_instance = AgentCoordinator(models_config)
            logger.info("Global agent coordinator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize global agent coordinator: {e}")
            # יצירת מופע דמה למצבי שגיאה
            __coordinator_instance = AgentCoordinator({
                "default": "fallback",
                "available": ["fallback"]
            })
    
    return __coordinator_instance
