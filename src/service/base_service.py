from typing import Dict, Any


from src.utils.logger import Logger


logger = Logger.setup()


class BaseService:
    def __init__(self):
        pass

    async def initialize(self):
        pass

    async def start(self):
        pass

    async def close(self):
        pass


    async def process_message(self, message_data: Dict[str, Any]):
        """Process the received message from converted-text-topic-test-v1"""
        try:
            logger.info(f"Processing message: {message_data}")
            
            # Extract message fields if available
            text_content = message_data.get('text_content', '')            
        except Exception as e:
            logger.error(f"Error processing message data: {e}", exc_info=True)
            raise e
    
    async def process_text_content(self, text_content: str):
        """Process the text content"""
        try:
            logger.info(f"Processing text content: {text_content}")
        except Exception as e:
            logger.error(f"Error processing text content: {e}", exc_info=True)
            raise e