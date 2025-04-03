"""
Feature registry for vertical slice architecture.
This makes it easier to discover and manage available features.
"""

import os

class FeatureRegistry:
    """Registry of all available features"""
    
    def __init__(self):
        self.features = {}
        self.apis = {}
    
    def register(self, name, module, api=None, enabled=True):
        """Register a feature"""
        self.features[name] = {
            'module': module,
            'api': api,
            'enabled': enabled
        }
        if api:
            self.apis[name] = api
    
    def get_feature(self, name):
        """Get a feature by name"""
        return self.features.get(name)
    
    def list_features(self):
        """List all registered features"""
        return list(self.features.keys())
    
    def list_enabled_features(self):
        """List all enabled features"""
        return [name for name, data in self.features.items() if data['enabled']]
    
    def add_frontend_routes(self, app):
        """Add routes to serve the frontend application"""
        # Check if the route is already registered to avoid duplicates
        if 'serve_frontend_root' not in [rule.endpoint for rule in app.url_map.iter_rules()]:
            @app.route('/')
            def serve_frontend_root():
                return app.send_static_file('index.html')
        
        # Check if the route is already registered to avoid duplicates
        if 'serve_frontend_files' not in [rule.endpoint for rule in app.url_map.iter_rules()]:
            @app.route('/<path:path>')
            def serve_frontend_files(path):
                if os.path.exists(os.path.join(app.static_folder, path)):
                    return app.send_static_file(path)
                return app.send_static_file('index.html')
    
    def register_all_with_app(self, app):
        """Register all API routes with the Flask app"""
        for name, data in self.features.items():
            if data['enabled'] and data['api']:
                try:
                    data['api'].register_routes(app)
                except Exception as e:
                    import logging
                    logging.error(f"Error registering routes for {name}: {e}")
        
        # Make sure frontend routes are registered
        self.add_frontend_routes(app)

# Create the registry
registry = FeatureRegistry()

# Import and register features
try:
    from .pdf_processing import api as pdf_api
    registry.register('pdf_processing', 'features.pdf_processing', pdf_api)
except ImportError:
    pass

try:
    from .document_upload import api as upload_api
    registry.register('document_upload', 'features.document_upload', upload_api)
except ImportError:
    pass

try:
    from .financial_analysis import api as financial_api
    registry.register('financial_analysis', 'features.financial_analysis', financial_api)
except ImportError:
    pass

try:
    from .document_qa import api as qa_api
    registry.register('document_qa', 'features.document_qa', qa_api)
except ImportError:
    pass

try:
    from .document_export import api as export_api
    registry.register('document_export', 'features.document_export', export_api)
except ImportError:
    pass

__all__ = ['registry']
