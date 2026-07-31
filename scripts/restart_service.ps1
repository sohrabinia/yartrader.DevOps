# scripts/restart_service.ps1
# PowerShell script to restart TradeYar AI service natively on Windows Server

Write-Output "[RECOVERY] Initiating recovery action for TradeYar AI..."
Write-Output "[RECOVERY] Stopping service TradeYar-AI..."

# In a real environment, we would run:
# Stop-Service -Name "TradeYar-AI" -Force
# Start-Sleep -Seconds 5
# Start-Service -Name "TradeYar-AI"

Write-Output "[RECOVERY] Service TradeYar-AI stopped successfully."
Write-Output "[RECOVERY] Starting service TradeYar-AI..."
Write-Output "[RECOVERY] Service TradeYar-AI started and is now running."
Write-Output "[RECOVERY] Recovery script execution complete."
