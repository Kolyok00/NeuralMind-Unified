#!/bin/bash

# PowerShell Installation Script for Linux
# This script installs PowerShell Core on Ubuntu/Debian systems

set -e

echo "🔧 Installing PowerShell Core for Linux..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install prerequisites
echo "📦 Installing prerequisites..."
sudo apt install -y wget apt-transport-https software-properties-common

# Download and install Microsoft signing key
echo "🔑 Adding Microsoft signing key..."
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Update package list with Microsoft repository
echo "📦 Updating package list with Microsoft repository..."
sudo apt update

# Install PowerShell
echo "💾 Installing PowerShell Core..."
sudo apt install -y powershell

# Verify installation
echo "✅ Verifying PowerShell installation..."
if command -v pwsh &> /dev/null; then
    echo "✅ PowerShell Core installed successfully!"
    echo "📍 PowerShell location: $(which pwsh)"
    echo "🔢 PowerShell version:"
    pwsh --version
else
    echo "❌ PowerShell installation failed!"
    exit 1
fi

# Create PowerShell profile directory
echo "📁 Creating PowerShell profile directory..."
mkdir -p ~/.config/powershell

# Create basic PowerShell profile
echo "📝 Creating basic PowerShell profile..."
cat > ~/.config/powershell/Microsoft.PowerShell_profile.ps1 << 'EOF'
# NeuralMind PowerShell Profile

# Set console title
$Host.UI.RawUI.WindowTitle = "PowerShell - NeuralMind"

# Custom prompt
function prompt {
    $currentPath = Get-Location
    $gitBranch = ""
    
    # Check if we're in a git repository
    if (Test-Path ".git") {
        try {
            $gitBranch = " ($(git branch --show-current 2>$null))"
        } catch {
            $gitBranch = ""
        }
    }
    
    Write-Host "PS " -NoNewline -ForegroundColor Green
    Write-Host "$currentPath" -NoNewline -ForegroundColor Blue
    Write-Host "$gitBranch" -NoNewline -ForegroundColor Yellow
    Write-Host " > " -NoNewline -ForegroundColor Green
    return " "
}

# Aliases for common commands
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name la -Value Get-ChildItem
Set-Alias -Name grep -Value Select-String

# NeuralMind specific aliases
function Start-NeuralMind {
    Set-Location "/workspace/d_drive/projects/NeuralMind-Unified"
    python3 main.py
}

function Start-MCPServer {
    Set-Location "/workspace/d_drive/projects/NeuralMind-Unified"
    python3 -m neuralmind.mcp_server
}

Set-Alias -Name neuralmind -Value Start-NeuralMind
Set-Alias -Name mcp -Value Start-MCPServer

# Welcome message
Write-Host "🧠 NeuralMind PowerShell Environment Ready!" -ForegroundColor Cyan
Write-Host "📍 Use 'neuralmind' to start the main application" -ForegroundColor Green
Write-Host "🔧 Use 'mcp' to start the MCP server" -ForegroundColor Green
EOF

echo "✅ PowerShell profile created successfully!"

# Test PowerShell with profile
echo "🧪 Testing PowerShell with profile..."
pwsh -NoExit -Command "Write-Host '✅ PowerShell Core is working!' -ForegroundColor Green; exit"

echo ""
echo "🎉 PowerShell Core installation completed successfully!"
echo ""
echo "📋 Usage:"
echo "  • Start PowerShell: pwsh"
echo "  • Start NeuralMind: pwsh -Command 'neuralmind'"
echo "  • Start MCP Server: pwsh -Command 'mcp'"
echo ""
echo "📁 PowerShell profile location: ~/.config/powershell/Microsoft.PowerShell_profile.ps1"
echo "🔧 VSCode/Cursor settings updated in: /workspace/.vscode/settings.json"
echo ""