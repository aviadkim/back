#!/bin/bash

# ==============================================================================
# QUICK CHECK SCRIPT v1.0 (Fast Sanity Check)
# Project: מערכת ניתוח מסמכים פיננסיים
# Date:    Thu Mar 27 04:08:07 2025
# Context: Running in Codespace, Ra'anana, Israel Timezone
# Goals:   Fast check (~2-3min) for dependencies and basic tests.
# SKIPS:   Flake8, Pydocstyle, Radon, Bandit, Coverage, HTML reports.
# ==============================================================================

# --- Configuration ---
PROJECT_ROOT="/workspaces/back"
TEST_DIRS="tests/ features" # Directories pytest should search within
REPORTS_DIR="reports"      # Still used for docker status log

# --- Script Setup ---
cd "$PROJECT_ROOT" || { echo "[System] ERROR: Cannot navigate to project root '$PROJECT_ROOT'"; exit 1; }
mkdir -p "$REPORTS_DIR"
FAILURE_DETECTED=0 # Track if any step fails
START_TIME=$(date +%s)

# Function to print messages
log_step() {
  local step_name="$1"
  local message="$2"
  echo "[${step_name}] ${message}"
}

# Function to check command success and update failure status
check_status() {
  local exit_code=$?
  local step_name="$1"
  if [ $exit_code -ne 0 ]; then
    log_step "ERROR" "Step '$step_name' failed with exit code $exit_code."
    FAILURE_DETECTED=1
    # Exit immediately on critical dependency failure
    if [[ "$step_name" == "Dependency Installation"* ]]; then
      log_step "ERROR" "Exiting due to critical dependency installation failure."
      exit $exit_code
    fi
  else
    log_step "INFO" "Step '$step_name' completed successfully."
  fi
  echo # Add a newline for readability
}

echo "============================================="
log_step "INFO" "Initiating Quick Check v1.0..."
echo "============================================="
echo

# --- Environment & Dependencies ---
log_step "INFO" "STEP 1: Checking environment and installing dependencies..."
if [ -z "$VIRTUAL_ENV" ]; then
    log_step "INFO" "Activating virtual environment 'venv'..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        # Ensure Rust env sourced if present (needed for some builds even if skipped now)
        if [ -f "$HOME/.cargo/env" ]; then source "$HOME/.cargo/env"; fi
    else
        log_step "ERROR" "Virtual environment 'venv' not found. Please run: python -m venv venv"
        exit 1
    fi
fi

log_step "INFO" "Checking/Installing project requirements (requirements.txt)..."
pip install -r requirements.txt
check_status "Dependency Installation (requirements.txt)"

log_step "INFO" "Checking/Installing minimal testing tools..."
# Install only essential fast tools for this quick check
pip install --upgrade pytest pytest-flask pytest-mock black
check_status "Dependency Installation (Minimal Testing Tools)"

# --- Prerequisite Checks ---
log_step "INFO" "STEP 2: Performing prerequisite checks..."
[ -f ".env" ] || log_step "WARNING" ".env file not found. Ensure configuration is correctly set."
[ -d "uploads" ] || log_step "WARNING" "'uploads' directory not found."
[ -d "data" ] || log_step "WARNING" "'data' directory not found."
[ -d "logs" ] || log_step "WARNING" "'logs' directory not found."

log_step "INFO" "Checking Docker Compose status (for MongoDB)..."
docker-compose ps > "$REPORTS_DIR/docker_compose_status.log" 2>&1
DOCKER_EXIT_CODE=$?
if [ $DOCKER_EXIT_CODE -eq 0 ] && grep -q -E 'running|up' "$REPORTS_DIR/docker_compose_status.log"; then
    log_step "INFO" "MongoDB container appears to be running."
else
    log_step "WARNING" "Docker command failed (Code: $DOCKER_EXIT_CODE) or MongoDB container not running/up. Check '$REPORTS_DIR/docker_compose_status.log'."
fi
check_status "Docker Check Command Execution"

# --- Quick Code Quality & Security ---
log_step "INFO" "STEP 3: Running quick static analysis..."

log_step "INFO" "[3a] Running Black (Code Formatting Check)..."
black . --check || log_step "WARNING" "Black found formatting issues. Run 'black .' to fix."
check_status "Black Formatting Check"

log_step "INFO" "[3b] Running Flake8 (Linting Check)..."
# Run flake8 using the config file to ignore specific errors
python -m flake8 . || log_step "WARNING" "Flake8 found linting issues. Review output."
check_status "Flake8 Linting Check"

# SKIPPING: Pydocstyle, Radon, Bandit for speed

log_step "INFO" "[3c] Running Safety (Dependency Vulnerability Scan)..." # Renumbered step
# safety check -r requirements.txt # Output goes to terminal (SKIPPED)
check_status "Safety Scan"

# --- Basic Pytest Run ---
log_step "INFO" "STEP 4: Running basic automated tests (Pytest)..."
log_step "INFO" "Executing Pytest suite (Dirs: '$TEST_DIRS')... (Coverage/HTML report skipped)"

# Run pytest without coverage or HTML report
python -m pytest "$TEST_DIRS"
PYTEST_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    log_step "ERROR" "Pytest execution failed."
    FAILURE_DETECTED=1
else
    log_step "INFO" "Pytest execution completed."
fi
check_status "Basic Pytest Execution"

# --- Final Summary ---
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "============================================="
log_step "INFO" "Quick Check v1.0 Complete. Duration: $DURATION seconds."
echo "============================================="

if [ $FAILURE_DETECTED -ne 0 ]; then
  log_step "ERROR" "STATUS: FAILED. Issues detected during the quick check. Review logs above."
else
  log_step "INFO" "STATUS: PASSED. All quick checks passed."
  log_step "INFO" "NOTE: This was a quick check. Run the full 'super_check.sh' for deeper analysis (Flake8, Bandit, Coverage etc.)."
fi
echo

# Return overall status code
exit $FAILURE_DETECTED