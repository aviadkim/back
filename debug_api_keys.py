#!/usr/bin/env python3
"""
Debug API keys and test connections to various services.
This will help pinpoint why the system is falling back to rule-based responses.
"""
import os
import sys
import json
import logging
import requests
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_debug.log')
    ]
)
logger = logging.getLogger("APIDebug")

def green(text):
    """Format text in green color"""
    return f"\033[92m{text}\033[0m"

def red(text):
    """Format text in red color"""
    return f"\033[91m{text}\033[0m"

def yellow(text):
    """Format text in yellow color"""
    return f"\033[93m{text}\033[0m"

def test_openrouter_key():
    """Test the OpenRouter API key"""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error(red("OpenRouter API key not found in .env file"))
        return False
        
    # Display the key format for validation (without showing the full key)
    key_start = api_key[:10] if len(api_key) > 10 else api_key
    key_end = api_key[-4:] if len(api_key) > 4 else ""
    logger.info(f"OpenRouter API key format: {key_start}...{key_end}")
    
    if not api_key.startswith("sk-or-"):
        logger.error(red("Invalid OpenRouter API key format. Should start with 'sk-or-'"))
        return False
    
    # Test the API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-document-processor.dev",
        "X-Title": "Financial Document Processor Debug"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",  # Use a free model for testing
        "messages": [
            {
                "role": "user",
                "content": "Say hello world"
            }
        ]
    }
    
    try:
        logger.info("Testing OpenRouter API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info(green(f"✓ OpenRouter API working! Response: {content}"))
            return True
        else:
            logger.error(red(f"OpenRouter API error: {response.status_code}"))
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(red(f"Error connecting to OpenRouter: {e}"))
        return False

def test_ai_service():
    """Test the AI service directly"""
    try:
        sys.path.insert(0, os.path.abspath('.'))
        from project_organized.shared.ai.service import AIService
        
        ai_service = AIService()
        
        # Check environment variables
        logger.info("Environment variables:")
        logger.info(f"DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL')}")
        logger.info(f"OPENROUTER_MODEL: {os.getenv('OPENROUTER_MODEL')}")
        
        # Display AI service config
        logger.info("\nAI service configuration:")
        logger.info(f"Default model: {ai_service.default_model}")
        logger.info(f"OpenRouter key valid: {ai_service.has_valid_openrouter_key}")
        logger.info(f"HuggingFace key valid: {ai_service.has_valid_YOUR_HUGGINGFACE_API_KEY}")
        logger.info(f"Gemini key valid: {ai_service.has_valid_gemini_key}")
        
        # Test with a simple prompt
        test_prompt = "Say hello world"
        logger.info("\nTesting AI service with a simple prompt...")
        response = ai_service.generate_response(test_prompt)
        
        logger.info(f"Response using default model ({ai_service.default_model}): {response}")
        
        # Force OpenRouter if available
        if ai_service.has_valid_openrouter_key:
            logger.info("\nTesting with explicit OpenRouter model...")
            response = ai_service.generate_response(test_prompt, model="openrouter")
            logger.info(f"OpenRouter response: {response}")
            
        # Check if we're falling back
        if "fallback" in response.lower() or "couldn't find" in response.lower():
            logger.warning(yellow("The response suggests we're falling back to rule-based answers"))
            return False
            
        return True
    except ImportError as e:
        logger.error(red(f"Import error: {e}"))
        return False
    except Exception as e:
        logger.error(red(f"Error in AI service test: {e}"))
        return False

def verify_file_structure():
    """Verify the file structure for AI module"""
    logger.info("Checking file structure...")
    
    # Check important files
    files_to_check = [
        "/workspaces/back/project_organized/shared/__init__.py",
        "/workspaces/back/project_organized/shared/ai/__init__.py",
        "/workspaces/back/project_organized/shared/ai/service.py",
    ]
    
    all_ok = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(green(f"✓ {file_path} exists"))
        else:
            logger.error(red(f"✗ {file_path} missing"))
            all_ok = False
    
    return all_ok

def fix_issues():
    """Fix common issues with API keys"""
    logger.info("Applying fixes...")
    
    # 1. Fix OpenRouter API key
    load_dotenv()
    current_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not current_key.startswith("sk-or-"):
        logger.info("Fixing OpenRouter API key format...")
        
        # Backup current .env file
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                env_content = f.read()
                
            with open(".env.backup", "w") as f:
                f.write(env_content)
                
            logger.info("Created backup of current .env file at .env.backup")
        
        # Get a valid key from user or use the provided one
        new_key = "YOUR_OPENROUTER_API_KEY"
        
        # Update the .env file
        try:
            with open(".env", "r") as f:
                lines = f.readlines()
                
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY
                        f.write(f"OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY
                    else:
                        f.write(line)
                        
            logger.info(green("Updated OpenRouter API key in .env file"))
        except Exception as e:
            logger.error(red(f"Failed to update .env file: {e}"))
    
    # 2. Make sure DEFAULT_MODEL is set to openrouter
    current_default = os.getenv("DEFAULT_MODEL", "")
    if current_default != "openrouter":
        logger.info("Setting DEFAULT_MODEL to openrouter...")
        try:
            with open(".env", "r") as f:
                lines = f.readlines()
                
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("DEFAULT_MODEL="):
                        f.write("DEFAULT_MODEL=openrouter\n")
                    else:
                        f.write(line)
                        
            logger.info(green("Updated DEFAULT_MODEL in .env file"))
        except Exception as e:
            logger.error(red(f"Failed to update .env file: {e}"))

    # 3. Fix AI service file if needed
    logger.info("Ensuring AI service is configured correctly...")
    ai_service_path = "/workspaces/back/project_organized/shared/ai/service.py"
    try:
        if os.path.exists(ai_service_path):
            with open(ai_service_path, "r") as f:
                content = f.read()
                
            # Make sure the file recognizes OpenRouter API keys
            if "has_valid_openrouter_key" not in content:
                logger.warning("AI service needs to be updated to support OpenRouter")
                # This would normally add the required code, but for now we'll just warn
    except Exception as e:
        logger.error(red(f"Failed to check AI service file: {e}"))

def quick_check():
    """Run a quick check, returning only exit code"""
    file_ok = verify_file_structure()
    if not file_ok:
        return False
        
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not api_key.startswith("sk-or-"):
        return False
        
    # Quick check of AI service
    try:
        from project_organized.shared.ai.service import AIService
        ai_service = AIService()
        if not ai_service.has_valid_openrouter_key:
            return False
    except:
        return False
        
    return True

def main():
    """Main function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Debug API keys and AI services")
    parser.add_argument("--quick", action="store_true", help="Run a quick check, returning only exit code")
    args = parser.parse_args()
    
    # Run quick check if requested
    if args.quick:
        success = quick_check()
        return 0 if success else 1
    
    # Otherwise run full check
    logger.info("===== API Keys Debug Tool =====")
    
    # Check file structure first
    if not verify_file_structure():
        logger.error(red("File structure issues found. Fix these first."))
        return 1
        
    # Test OpenRouter key
    openrouter_ok = test_openrouter_key()
    
    # Test AI service
    ai_service_ok = test_ai_service()
    
    # Print summary
    logger.info("\n===== Debug Results =====")
    logger.info(f"File structure: {'OK' if verify_file_structure() else 'Issues found'}")
    logger.info(f"OpenRouter API: {'OK' if openrouter_ok else 'Not working'}")
    logger.info(f"AI service: {'OK' if ai_service_ok else 'Not working'}")
    
    # Apply fixes if needed
    if not openrouter_ok or not ai_service_ok:
        answer = input("\nWould you like to apply fixes automatically? (y/n): ")
        if answer.lower() in ["y", "yes"]:
            fix_issues()
            logger.info("\nFixes applied. Please run the script again to verify.")
        else:
            logger.info("\nNo fixes applied.")
    else:
        logger.info(green("\nAll systems are working correctly!"))
    
    return 0 if openrouter_ok and ai_service_ok else 1

if __name__ == "__main__":
    sys.exit(main())
