#!/bin/bash
<<<<<<< HEAD

echo "Making test scripts executable..."
chmod +x /workspaces/back/test_document_qa_with_pdf.py
chmod +x /workspaces/back/benchmark_models.sh
chmod +x /workspaces/back/test_real_world_qa.py
chmod +x /workspaces/back/run_with_real_pdf.sh
chmod +x /workspaces/back/prepare_for_github.sh
chmod +x /workspaces/back/setup_env.sh
chmod +x /workspaces/back/push_to_github.sh
chmod +x /workspaces/back/debug_api_keys.py
chmod +x /workspaces/back/test_qa_feature.py
chmod +x /workspaces/back/test_qa_with_openrouter.sh
chmod +x /workspaces/back/comprehensive_qa_test.py
chmod +x /workspaces/back/analyze_qa_results.py

echo "Done! You can run the following scripts:"
echo "  ./prepare_for_github.sh        # Prepare project for GitHub (handle API keys)"
echo "  ./push_to_github.sh           # Prepare and push to GitHub in one step"
echo "  ./setup_env.sh                 # Set up environment after cloning"
echo "  ./run_with_real_pdf.sh         # Test Q&A with any PDF file"
echo "  ./test_document_qa_with_pdf.py # Test Q&A with a PDF file"
echo "  ./benchmark_models.sh          # Benchmark different AI models"
echo "  ./test_real_world_qa.py        # Run comprehensive tests"
=======
echo "Making all scripts executable..."
chmod +x /workspaces/back/start_production.sh
chmod +x /workspaces/back/stop_server.sh
chmod +x /workspaces/back/document_dashboard.py
chmod +x /workspaces/back/launch_production.sh
chmod +x /workspaces/back/make_scripts_executable.sh

echo "All scripts are now executable."
echo "You can now run ./launch_production.sh to set up everything."
>>>>>>> main
