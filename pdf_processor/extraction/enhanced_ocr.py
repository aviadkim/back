import os
import tempfile
import logging
import pytesseract
from pdf2image import convert_from_path
import boto3
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)

class EnhancedOCR:
    """Enhanced OCR capabilities with multiple backends."""

    def __init__(self, config=None):
        """Initialize the OCR processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.engine = self.config.get('ocr_engine', 'local')
        self.default_language = self.config.get('default_language', 'eng')
        self.additional_languages = self.config.get('additional_languages', ['heb'])

        # AWS Textract config
        self.aws_textract_key = self.config.get('aws_textract_key', '')
        self.aws_region = self.config.get('aws_region', 'us-east-1')
        self.aws_access_key = self.config.get('aws_access_key_id', '')
        self.aws_secret_key = self.config.get('aws_secret_access_key', '')

        # Google Vision config
        self.google_vision_key = self.config.get('google_vision_key', '')

        logger.info(f"Initialized EnhancedOCR with engine: {self.engine}")

    def process_image(self, image, language=None):
        """Process an image with OCR.

        Args:
            image: PIL Image object or path to image
            language: Language code (e.g., 'eng', 'heb', 'auto')

        Returns:
            Extracted text
        """
        if language is None:
            language = self.default_language

        # Convert path to image if necessary
        if isinstance(image, str):
            image = Image.open(image)

        # Determine OCR engine to use
        if self.engine == 'local':
            return self._process_with_tesseract(image, language)
        elif self.engine == 'aws_textract':
            return self._process_with_aws_textract(image)
        elif self.engine == 'google_vision':
            return self._process_with_google_vision(image)
        else:
            logger.warning(f"Unknown OCR engine: {self.engine}, falling back to tesseract")
            return self._process_with_tesseract(image, language)

    def process_pdf_page(self, pdf_path, page_number, language=None):
        """Process a specific page from a PDF.

        Args:
            pdf_path: Path to PDF file
            page_number: Page number (0-based)
            language: Language code (e.g., 'eng', 'heb', 'auto')

        Returns:
            Extracted text
        """
        # Convert PDF page to image
        images = convert_from_path(
            pdf_path,
            first_page=page_number + 1,
            last_page=page_number + 1
        )

        if not images:
            logger.warning(f"Failed to convert PDF page {page_number} to image")
            return ""

        # Process the image
        return self.process_image(images[0], language)

    def _process_with_tesseract(self, image, language):
        """Process image with Tesseract OCR.

        Args:
            image: PIL Image
            language: Language code

        Returns:
            Extracted text
        """
        # Handle 'auto' language - try multiple languages
        if language == 'auto':
            lang_param = f"{self.default_language}+{'+'.join(self.additional_languages)}"
        else:
            lang_param = language

        try:
            # Apply image preprocessing if needed
            preprocessed_image = self._preprocess_image(image)

            # Run OCR
            text = pytesseract.image_to_string(
                preprocessed_image,
                lang=lang_param,
                config='--psm 6'  # Assume a single uniform block of text
            )

            return text
        except Exception as e:
            logger.error(f"Tesseract OCR error: {str(e)}")
            return ""

    def _process_with_aws_textract(self, image):
        """Process image with AWS Textract.

        Args:
            image: PIL Image

        Returns:
            Extracted text
        """
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Initialize AWS Textract client
            textract = boto3.client(
                'textract',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )

            # Detect text
            response = textract.detect_document_text(
                Document={'Bytes': img_byte_arr.read()}
            )

            # Extract text blocks
            text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text += item['Text'] + "\n"

            return text
        except Exception as e:
            logger.error(f"AWS Textract error: {str(e)}")
            return ""

    def _process_with_google_vision(self, image):
        """Process image with Google Cloud Vision.

        Args:
            image: PIL Image

        Returns:
            Extracted text
        """
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Prepare request
            api_url = "https://vision.googleapis.com/v1/images:annotate"
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": img_byte_arr.read().decode('latin-1')
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION"
                            }
                        ]
                    }
                ]
            }

            # Make API request
            response = requests.post(
                f"{api_url}?key={self.google_vision_key}",
                json=payload
            )

            # Parse response
            if response.status_code == 200:
                result = response.json()
                if 'responses' in result and result['responses']:
                    text = result['responses'][0].get('fullTextAnnotation', {}).get('text', '')
                    return text

            logger.warning(f"Google Vision API error: {response.status_code} - {response.text}")
            return ""
        except Exception as e:
            logger.error(f"Google Vision error: {str(e)}")
            return ""

    def _preprocess_image(self, image):
        """Preprocess image for better OCR results."""
        # This is a placeholder - add actual preprocessing steps as needed
        return image  # Return original image for now