import os
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr # Import draw_ocr if needed for visualization
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PaddleOcrProcessor:
    """Enhanced OCR with PaddleOCR."""

    def __init__(self, languages=['en', 'he'], use_gpu=False): # Default languages
        """Initialize the PaddleOCR processor.

        Args:
            languages (list): List of language codes (e.g., 'en', 'ch', 'he').
                              See PaddleOCR docs for supported languages.
            use_gpu (bool): Whether to use GPU for inference.
        """
        lang_string = ','.join(languages)
        logger.info(f"Initializing PaddleOCR with languages: {lang_string}, GPU: {use_gpu}")
        try:
            # Initialize PaddleOCR engine
            # use_angle_cls=True helps with rotated text
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang_string, use_gpu=use_gpu)
            logger.info("PaddleOCR initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}", exc_info=True)
            # Consider raising an exception or setting a flag indicating failure
            self.ocr = None

    def process_image(self, image_input):
        """Process an image (path, numpy array, or bytes) with PaddleOCR.

        Args:
            image_input: Path to image file, numpy array (OpenCV format BGR), or image bytes.

        Returns:
            str: Extracted text concatenated from results.
                 Returns empty string if OCR failed or no text found.
        """
        if self.ocr is None:
            logger.error("PaddleOCR is not initialized. Cannot process image.")
            return ""

        extracted_text = ""
        try:
            # Perform OCR
            # The result is a list of lists, e.g., [[box, (text, confidence)], ...]
            result = self.ocr.ocr(image_input, cls=True)

            if result and result[0]: # Check if result is not None and not empty
                # Extract text from the result structure
                txts = [line[1][0] for line in result[0]]
                extracted_text = "\n".join(txts)
                logger.debug(f"PaddleOCR extracted {len(txts)} lines of text.")
            else:
                 logger.warning("PaddleOCR returned no results for the image.")


        except Exception as e:
            logger.error(f"Error during PaddleOCR processing: {e}", exc_info=True)
            # Return empty string on error

        return extracted_text

    def process_image_file(self, image_path: str) -> str:
         """Convenience method to process an image file from its path."""
         if not os.path.exists(image_path):
              logger.error(f"Image file not found: {image_path}")
              return ""
         return self.process_image(image_path)

    def process_pil_image(self, pil_image: Image.Image) -> str:
         """Convenience method to process a PIL Image object."""
         # Convert PIL Image (RGB) to OpenCV format (BGR) numpy array
         cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
         return self.process_image(cv_image)

    def process_image_bytes(self, image_bytes: bytes) -> str:
         """Convenience method to process image bytes."""
         try:
              # Convert bytes to numpy array
              nparr = np.frombuffer(image_bytes, np.uint8)
              cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
              if cv_image is None:
                   logger.error("Failed to decode image bytes.")
                   return ""
              return self.process_image(cv_image)
         except Exception as e:
              logger.error(f"Error processing image bytes: {e}", exc_info=True)
              return ""

# Example Usage (can be run standalone for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Create a dummy image path for testing (replace with a real image path)
    dummy_image_path = 'test_image.png'
    if not os.path.exists(dummy_image_path):
         # Create a simple black image if it doesn't exist
         try:
              img = Image.new('RGB', (600, 150), color = 'black')
              # Add some text (requires Pillow with font support)
              # from PIL import ImageDraw, ImageFont
              # d = ImageDraw.Draw(img)
              # font = ImageFont.truetype("arial.ttf", 15) # Requires font file
              # d.text((10,10), "Hello PaddleOCR", fill=(255,255,0), font=font)
              img.save(dummy_image_path)
              logger.info(f"Created dummy image: {dummy_image_path}")
         except Exception as e:
              logger.error(f"Could not create dummy image: {e}. Please provide a real image path.")
              dummy_image_path = None


    if dummy_image_path:
        # Initialize with English and Hebrew
        ocr_processor = PaddleOcrProcessor(languages=['en', 'he'])

        if ocr_processor.ocr: # Check if initialized successfully
            logger.info(f"Processing image: {dummy_image_path}")
            text_result = ocr_processor.process_image_file(dummy_image_path)

            print("\n--- OCR Result ---")
            print(text_result)
            print("------------------")
        else:
            print("PaddleOCR failed to initialize. Cannot run example.")

        # Clean up dummy image
        # os.remove(dummy_image_path)