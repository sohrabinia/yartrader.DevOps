# TradeYar.DevOps Windows Service Guide

This document describes how to deploy and manage `TradeYar.DevOps.Api` as a background Windows Service.

## Windows Service Architecture

The API uses `Microsoft.Extensions.Hosting.WindowsServices` to natively bind to the Windows Service Control Manager (SCM).

- **Service Name**: `TradeYar-DevOps`
- **Display Name**: `TradeYar DevOps Platform`
- **Startup Type**: `Automatic`
- **Graceful Shutdown**: Handled via `UseWindowsService()`, allowing active collectors to finish executing before the process terminates.

---

## Service Installation

To install `TradeYar-DevOps` as a Windows Service, run PowerShell as Administrator and follow these steps:

### 1. Compile the Binary
Publish the API project targeting `win-x64`:
```powershell
dotnet publish src\TradeYar.DevOps.Api\TradeYar.DevOps.Api.csproj -c Release -r win-x64 --self-contained true -o C:\TradeYar\DevOps
```

### 2. Create the Service
```powershell
New-Service -Name "TradeYar-DevOps" -BinaryPathName "C:\TradeYar\DevOps\TradeYar.DevOps.Api.exe" -DisplayName "TradeYar DevOps Platform" -StartupType Automatic
```

### 3. Configure Failure Recovery
Ensure that the Windows SCM automatically restarts the service on any crash:
```powershell
sc.exe failure "TradeYar-DevOps" reset= 86400 actions= restart/60000/restart/60000/restart/60000
```

### 4. Start the Service
```powershell
Start-Service -Name "TradeYar-DevOps"
```

---

## Log Management

When running as a Windows Service, output is piped to:
- **Windows Event Log**: Stored under Applications with the source `TradeYar-DevOps`.
- **Configuration Overrides**: Environment variables can be configured globally to change log levels dynamically.
