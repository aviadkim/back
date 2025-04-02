"""
Dependency injection container for the application.
This provides a clean way to manage dependencies between features.
"""
import os

class DependencyContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services = {}
        self._config = {}
        
    def register(self, name, instance):
        """Register a service instance"""
        self._services[name] = instance
        
    def register_factory(self, name, factory):
        """Register a factory function to create a service"""
        self._services[name] = factory
        
    def configure(self, key, value):
        """Set configuration value"""
        self._config[key] = value
        
    def get(self, name):
        """Get a service by name"""
        service = self._services.get(name)
        if callable(service) and not isinstance(service, type):
            # If it's a factory function, call it
            service = service()
            # Cache the instance
            self._services[name] = service
        return service
        
    def get_config(self, key, default=None):
        """Get configuration value"""
        return self._config.get(key, default)

# Create the container
container = DependencyContainer()

# Configure from environment
container.configure('DEBUG', os.environ.get('DEBUG', 'true').lower() == 'true')
container.configure('UPLOAD_DIR', os.environ.get('UPLOAD_DIR', 'uploads'))
container.configure('EXTRACTION_DIR', os.environ.get('EXTRACTION_DIR', 'extractions'))

# Register core services
from features.pdf_processing.service import PDFProcessingService
from features.document_upload.service import DocumentUploadService
from features.financial_analysis.service import FinancialAnalysisService
from features.document_qa.service import DocumentQAService

container.register_factory('pdf_service', lambda: PDFProcessingService(
    extraction_dir=container.get_config('EXTRACTION_DIR')
))

container.register_factory('upload_service', lambda: DocumentUploadService(
    upload_dir=container.get_config('UPLOAD_DIR'),
    extraction_dir=container.get_config('EXTRACTION_DIR')
))

container.register_factory('financial_service', lambda: FinancialAnalysisService())

container.register_factory('qa_service', lambda: DocumentQAService())

# Export container instance
__all__ = ['container']
