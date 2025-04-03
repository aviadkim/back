# PowerShell test runner script
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"
python -m pytest tests/test_auth.py -v