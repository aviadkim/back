"""
Dependency injection container for the application.
This provides a clean way to manage dependencies between features.
"""
import os
import logging

logger = logging.getLogger(__name__)

class DependencyContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services = {}
        self._config = {}
    
    def register(self, name, service):
        """Register a service"""
        self._services[name] = service
        logger.debug(f"Registered service: {name}")
        return self
    
    def get(self, name):
        """Get a service"""
        if name in self._services:
            return self._services[name]
        logger.warning(f"Service not found: {name}")
        return None
    
    def configure(self, key, value):
        """Set a configuration value"""
        self._config[key] = value
        return self
    
    def get_config(self, key, default=None):
        """Get a configuration value"""
        return self._config.get(key, default)

# Create the container
container = DependencyContainer()

# Configure from environment
container.configure('DEBUG', os.environ.get('DEBUG', 'true').lower() == 'true')
container.configure('PORT', int(os.environ.get('PORT', 5001)))
container.configure('MAX_UPLOAD_SIZE', os.environ.get('MAX_UPLOAD_SIZE', '100MB'))
container.configure('DEFAULT_LANGUAGE', os.environ.get('DEFAULT_LANGUAGE', 'heb+eng'))
container.configure('OCR_DPI', int(os.environ.get('OCR_DPI', 300)))

# Register core services
try:
    from project_organized.shared.ai.service import AIService
    container.register('ai_service', AIService())
except ImportError:
    logger.warning("AIService not available")

try:
    from project_organized.features.document_upload.service import DocumentUploadService
    container.register('document_upload', DocumentUploadService())
except ImportError:
    logger.warning("DocumentUploadService not available")

try:
    from project_organized.features.pdf_processing.service import PDFProcessingService
    container.register('pdf_processing', PDFProcessingService())
except ImportError:
    logger.warning("PDFProcessingService not available")

try:
    from project_organized.features.financial_analysis.service import FinancialAnalysisService
    container.register('financial_analysis', FinancialAnalysisService())
except ImportError:
    logger.warning("FinancialAnalysisService not available")

try:
    from project_organized.features.document_qa.service import DocumentQAService
    container.register('document_qa', DocumentQAService())
except ImportError:
    logger.warning("DocumentQAService not available")

try:
    from project_organized.features.document_export.service import DocumentExportService
    container.register('document_export', DocumentExportService())
except ImportError:
    logger.warning("DocumentExportService not available")
