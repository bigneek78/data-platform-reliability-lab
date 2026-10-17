$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python app.py
exit $LASTEXITCODE
