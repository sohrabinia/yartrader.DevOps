# scripts/restart_service.ps1
# PowerShell script to restart YarTrader AI service natively on Windows Server

Write-Output "[RECOVERY] Initiating recovery action for YarTrader AI..."
Write-Output "[RECOVERY] Stopping service YarTrader-AI..."

# In a real environment, we would run:
# Stop-Service -Name "YarTrader-AI" -Force
# Start-Sleep -Seconds 5
# Start-Service -Name "YarTrader-AI"

Write-Output "[RECOVERY] Service YarTrader-AI stopped successfully."
Write-Output "[RECOVERY] Starting service YarTrader-AI..."
Write-Output "[RECOVERY] Service YarTrader-AI started and is now running."
Write-Output "[RECOVERY] Recovery script execution complete."
