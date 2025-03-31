# Getting Your App Running in a New Codespace Session

When you open your codespace in the future, here's a simple guide for starting your app without having to reinstall dependencies each time:

## Quick Start Commands

```bash
# 1. Start MongoDB (required for the app to work)
# Make sure no other MongoDB container is running with the same name or port
docker run -d -p 27017:27017 --name mongodb mongo:4.4

# 2. Start the application (assuming app.py is the main entry point)
python app.py 
```

This should be enough to get your app running, typically at `http://localhost:5000` (check the application's startup logs for the exact address).

## If You Need to Rebuild the Frontend

If you've made changes to the frontend code (`frontend/` directory) and need to rebuild it:

```bash
cd frontend
npm install # Run this if you added new dependencies
npm run build
cd ..
# Then restart the application
python app.py
```

## About Dependencies

The good news is that you don't need to reinstall dependencies each time you open a codespace. GitHub Codespaces persists your workspace between sessions, including:

*   Installed Python packages (from `pip install -r requirements.txt`)
*   Installed npm packages (in `frontend/node_modules`)
*   Docker images you've pulled (like the `mongo:4.4` image)