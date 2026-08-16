# YarTrader.DevOps Deployment Guide

This guide details steps for deploying the `YarTrader.DevOps` platform as a background system service or interactive container.

## Windows Service Deployment (Production)

The platform compiles directly into a native executable ready to run as a Windows Service named `YarTrader-DevOps`.

### Requirements
- Directory: `C:\YarTrader\DevOps`
- Executable: `YarTrader.DevOps.Api.exe`
- Auto-start configured
- Automated crash recovery enabled

### Deployment Commands

To compile the self-contained production payload:
```bash
dotnet publish src/YarTrader.DevOps.Api/YarTrader.DevOps.Api.csproj -c Release -r win-x64 --self-contained true -o C:\YarTrader\DevOps
```

To register and start the Windows Service via PowerShell (Administrator):
```powershell
# Create the service
New-Service -Name "YarTrader-DevOps" -BinaryPathName "C:\YarTrader\DevOps\YarTrader.DevOps.Api.exe" -DisplayName "YarTrader DevOps Platform" -StartupType Automatic

# Set recovery actions on crash
sc.exe failure "YarTrader-DevOps" reset= 86400 actions= restart/60000/restart/60000/restart/60000

# Start the service
Start-Service -Name "YarTrader-DevOps"
```

---

## Linux / Docker Deployment (Containerized)

The platform is designed to run perfectly as a Docker container in a container orchestration engine.

### Sample Dockerfile
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /source

COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .

EXPOSE 5000
ENTRYPOINT ["dotnet", "YarTrader.DevOps.Api.dll"]
```

To run:
```bash
docker build -t YarTrader-devops .
docker run -d -p 5000:80 --name YarTrader-devops YarTrader-devops
```
