# YarTrader.DevOps Windows Service Guide

This document describes how to deploy and manage `YarTrader.DevOps.Api` as a background Windows Service.

## Windows Service Architecture

The API uses `Microsoft.Extensions.Hosting.WindowsServices` to natively bind to the Windows Service Control Manager (SCM).

- **Service Name**: `YarTrader-DevOps`
- **Display Name**: `YarTrader DevOps Platform`
- **Startup Type**: `Automatic`
- **Graceful Shutdown**: Handled via `UseWindowsService()`, allowing active collectors to finish executing before the process terminates.

---

## Service Installation

To install `YarTrader-DevOps` as a Windows Service, run PowerShell as Administrator and follow these steps:

### 1. Compile the Binary
Publish the API project targeting `win-x64`:
```powershell
dotnet publish src\YarTrader.DevOps.Api\YarTrader.DevOps.Api.csproj -c Release -r win-x64 --self-contained true -o C:\YarTrader\DevOps
```

### 2. Create the Service
```powershell
New-Service -Name "YarTrader-DevOps" -BinaryPathName "C:\YarTrader\DevOps\YarTrader.DevOps.Api.exe" -DisplayName "YarTrader DevOps Platform" -StartupType Automatic
```

### 3. Configure Failure Recovery
Ensure that the Windows SCM automatically restarts the service on any crash:
```powershell
sc.exe failure "YarTrader-DevOps" reset= 86400 actions= restart/60000/restart/60000/restart/60000
```

### 4. Start the Service
```powershell
Start-Service -Name "YarTrader-DevOps"
```

---

## Log Management

When running as a Windows Service, output is piped to:
- **Windows Event Log**: Stored under Applications with the source `YarTrader-DevOps`.
- **Configuration Overrides**: Environment variables can be configured globally to change log levels dynamically.
