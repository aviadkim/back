#!/bin/bash
# Display a horizontal tree view of project structure

# Set colors for better readability
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${BLUE}===== Project Directory Structure =====${RESET}\n"

# Create a horizontal tree using find with pretty formatting
find /workspaces/back -not -path "*/\.*" -not -path "*/venv/*" | sort | while read -r file; do
    # Get depth by counting slashes after /workspaces/back/
    path=${file#/workspaces/back/}
    depth=$(($(echo "$path" | tr -cd '/' | wc -c)))
    
    # Generate indentation
    indent=""
    for ((i=0; i<depth; i++)); do
        indent="$indent│   "
    done
    
    # Replace last '│   ' with '├── ' for files/dirs that have siblings
    # or with '└── ' for the last item at its level
    if [ -n "$indent" ]; then
        indent="${indent%│   }"
        
        # Check if this is the last item at its level
        current_dir=$(dirname "$file")
        if [ "$(find "$current_dir" -maxdepth 1 | sort | tail -n 1)" = "$file" ]; then
            indent="${indent}└── "
        else
            indent="${indent}├── "
        fi
    fi
    
    # Get just the filename
    filename=$(basename "$file")
    
    # Display with different colors for directories vs files
    if [ -d "$file" ]; then
        echo -e "${indent}${CYAN}${filename}/${RESET}"
    else
        # For Python files, show with .py extension in a different color
        if [[ "$filename" == *.py ]]; then
            name_part=${filename%.py}
            echo -e "${indent}${name_part}${GREEN}.py${RESET}"
        else
            echo -e "${indent}${filename}"
        fi
    fi
done

echo -e "\n${BLUE}===== File Counts by Type =====${RESET}"
echo
echo "Python files: $(find /workspaces/back -name "*.py" | wc -l)"
echo "HTML files: $(find /workspaces/back -name "*.html" | wc -l)"
echo "JavaScript files: $(find /workspaces/back -name "*.js" | wc -l)"
echo "Shell scripts: $(find /workspaces/back -name "*.sh" | wc -l)"
echo "JSON files: $(find /workspaces/back -name "*.json" | wc -l)"
echo "Total files: $(find /workspaces/back -type f | wc -l)"
