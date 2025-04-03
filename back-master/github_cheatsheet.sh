#!/bin/bash
# GitHub and Workspace Cheat Sheet for Financial Document Processor

cat << 'EOL'
=================================================
   GitHub and Workspace Management Cheat Sheet
=================================================

WHEN STARTING A NEW CODESPACE:
------------------------------
1. Set up the workspace:
   $ ./restore_workspace.sh

2. Start the application:
   $ ./start_production.sh

3. Monitor document processing:
   $ python document_dashboard.py

4. Run API tests:
   $ python test_api.py


ENVIRONMENT MANAGEMENT:
----------------------
1. Set up API keys:
   $ ./setup_ai_integration.sh

2. Test OpenRouter API:
   $ python test_openrouter.py


GIT AND GITHUB COMMANDS:
-----------------------
1. Check branch status:
   $ git status
   $ git branch -a

2. Safely push to GitHub:
   $ ./prepare_for_github.sh   # Clean API keys
   $ git add .
   $ git commit -m "Your commit message"
   $ git push origin master    # or main

3. Fix branch divergence:
   $ ./fix_branch_divergence.sh

4. Resolve uncommitted changes:
   $ ./resolve_uncommitted_changes.sh


COMMON ISSUES AND FIXES:
-----------------------
1. API keys exposed:
   $ ./remove_api_keys.sh

2. Push failing:
   $ ./fix_git_upstream.sh
   # If needed: 
   $ ./force_push_to_github.sh

3. Directory issues:
   $ ./fix_directory_permissions.sh


APPLICATION MANAGEMENT:
---------------------
1. Start application:
   $ ./start_production.sh

2. Stop application:
   $ ./stop_server.sh

3. Test application:
   $ ./test_full_implementation.sh

4. Verify implementation:
   $ ./run_all_verification_tests.sh


QUICK DEMOS:
-----------
1. Process a sample PDF:
   $ ./quick_qa_test.py

2. Demo API usage:
   $ ./demo_api_usage.py


DEVELOPMENT WORKFLOW:
-------------------
1. Make changes to code
2. Run tests: ./test_api.py 
3. Clean API keys: ./prepare_for_github.sh
4. Commit changes: git add . && git commit -m "message"
5. Push to GitHub: git push
EOL

# Make relevant scripts executable
echo -e "\nMaking important scripts executable..."
chmod +x restore_workspace.sh 2>/dev/null || echo "restore_workspace.sh not found"
chmod +x start_production.sh 2>/dev/null || echo "start_production.sh not found"
chmod +x prepare_for_github.sh 2>/dev/null || echo "prepare_for_github.sh not found"
chmod +x test_full_implementation.sh 2>/dev/null || echo "test_full_implementation.sh not found"

echo -e "\nCheat sheet created! Use this for quick reference when working with your project."
echo "To view this cheat sheet anytime, run: ./github_cheatsheet.sh"
