import os
import sys
import logging
import argparse
import uvicorn
import socket
from api.routes import app  # Import the FastAPI app from routes

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int = 8000, max_port: int = 9000) -> int:
    """Find an available port starting from start_port."""
    port = start_port
    while port < max_port:
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"No available ports found in range {start_port}-{max_port}")

def main():
    """Run the financial document analyzer application."""
    parser = argparse.ArgumentParser(description="Financial Document Analyzer")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error", "critical"],
                       help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    try:
        logging.info("Initializing application...")
        
        # Find an available port
        port = find_available_port(args.port, 9000)
        logging.info(f"Found available port: {port}")
        
        # Run the API server
        uvicorn.run(
            app,
            host=args.host,
            port=port,
            reload=args.reload,
            log_level=args.log_level
        )
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
