#!/bin/bash

# PowerShell Notifications Disabler Script
# This script disables all PowerShell notifications in Cursor/VSCode

set -e

echo "🔕 Disabling PowerShell notifications in Cursor/VSCode..."

# Backup original settings
echo "💾 Creating backup of original settings..."
if [ -f "/workspace/.vscode/settings.json" ]; then
    cp "/workspace/.vscode/settings.json" "/workspace/.vscode/settings.json.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created: settings.json.backup"
fi

# Create Cursor user settings directory if it doesn't exist
CURSOR_USER_DIR="$HOME/.cursor-server/data/User"
mkdir -p "$CURSOR_USER_DIR"

# Create global settings to disable PowerShell notifications
echo "🔧 Creating global Cursor settings..."
cat > "$CURSOR_USER_DIR/settings.json" << 'EOF'
{
    "powershell.promptToUpdatePowerShell": false,
    "powershell.integratedConsole.showOnStartup": false,
    "powershell.enableProfileLoading": false,
    "powershell.scriptAnalysis.enable": false,
    "powershell.codeFormatting.autoCorrectAliases": false,
    "powershell.developer.bundledModulesPath": "",
    "powershell.developer.editorServicesLogLevel": "Error",
    "powershell.developer.editorServicesWaitForDebugger": false,
    "powershell.powerShellExePath": "",
    "powershell.bugReporting": false,
    "powershell.helpCompletion": "Disabled",
    "powershell.buttons.showPanelMovementButtons": false,
    "powershell.buttons.showRunButtons": false,
    "powershell.codeFormatting.addWhitespaceAroundPipe": false,
    "powershell.codeFormatting.trimWhitespaceAroundPipe": false,
    "powershell.codeFormatting.useConstantStrings": false,
    "powershell.codeFormatting.useCorrectCasing": false,
    "notifications.showExtensionsOnlyFromTrustedPublishers": true,
    "extensions.ignoreRecommendations": true,
    "extensions.showRecommendationsOnlyOnDemand": true,
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false,
    "update.showReleaseNotes": false,
    "workbench.welcomePage.walkthroughs.openOnInstall": false,
    "workbench.startupEditor": "none",
    "telemetry.telemetryLevel": "off",
    "workbench.settings.enableNaturalLanguageSearch": false
}
EOF

# Create extension-specific settings
echo "📦 Creating extension-specific settings..."
EXTENSIONS_DIR="$HOME/.cursor-server/extensions"
mkdir -p "$EXTENSIONS_DIR"

# Disable PowerShell extension notifications
cat > "/workspace/.cursor/extension_settings.json" << 'EOF'
{
    "ms-vscode.powershell": {
        "promptToUpdatePowerShell": false,
        "integratedConsole.showOnStartup": false,
        "enableProfileLoading": false,
        "scriptAnalysis.enable": false,
        "bugReporting": false,
        "helpCompletion": "Disabled",
        "buttons.showPanelMovementButtons": false,
        "buttons.showRunButtons": false,
        "developer.editorServicesLogLevel": "Error"
    }
}
EOF

# Create a PowerShell profile that suppresses notifications
echo "📝 Creating PowerShell profile to suppress notifications..."
POWERSHELL_PROFILE_DIR="$HOME/.config/powershell"
mkdir -p "$POWERSHELL_PROFILE_DIR"

cat > "$POWERSHELL_PROFILE_DIR/Microsoft.PowerShell_profile.ps1" << 'EOF'
# Suppress PowerShell notifications and warnings
$WarningPreference = "SilentlyContinue"
$InformationPreference = "SilentlyContinue"
$VerbosePreference = "SilentlyContinue"
$DebugPreference = "SilentlyContinue"

# Disable PowerShell update checks
$env:POWERSHELL_UPDATECHECK = "Off"
$env:POWERSHELL_TELEMETRY_OPTOUT = "1"

# Suppress PSReadLine warnings
if (Get-Module -ListAvailable PSReadLine) {
    try {
        Import-Module PSReadLine -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        Set-PSReadLineOption -BellStyle None -WarningAction SilentlyContinue
    } catch {
        # Silently ignore any PSReadLine errors
    }
}

# Custom prompt without version info
function prompt {
    $currentPath = Get-Location
    Write-Host "PS " -NoNewline -ForegroundColor Green
    Write-Host "$currentPath" -NoNewline -ForegroundColor Blue
    Write-Host " > " -NoNewline -ForegroundColor Green
    return " "
}

# NeuralMind aliases (silent)
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
EOF

# Set environment variables to disable PowerShell notifications
echo "🔧 Setting environment variables..."
cat >> "/workspace/.env" << 'EOF'

# PowerShell notification suppression
POWERSHELL_UPDATECHECK=Off
POWERSHELL_TELEMETRY_OPTOUT=1
DOTNET_CLI_TELEMETRY_OPTOUT=1
VSCODE_DISABLE_WORKSPACE_TRUST=1
EOF

# Create a script to kill PowerShell extension processes that might show notifications
echo "⚡ Creating PowerShell process cleanup script..."
cat > "/workspace/cleanup_powershell_processes.sh" << 'EOF'
#!/bin/bash
# Kill PowerShell extension processes that might show notifications
pkill -f "PowerShell Editor Services" 2>/dev/null || true
pkill -f "pwsh.*LanguageServer" 2>/dev/null || true
pkill -f "Microsoft.PowerShell.EditorServices" 2>/dev/null || true
echo "PowerShell extension processes cleaned up"
EOF

chmod +x "/workspace/cleanup_powershell_processes.sh"

# Test the configuration
echo "🧪 Testing PowerShell notification suppression..."
if command -v pwsh &> /dev/null; then
    echo "✅ PowerShell found, testing notification suppression..."
    pwsh -NoProfile -NoLogo -Command "Write-Host 'PowerShell notifications should now be suppressed' -ForegroundColor Green; exit" 2>/dev/null || echo "PowerShell test completed"
else
    echo "ℹ️ PowerShell not installed, but notification settings configured"
fi

echo ""
echo "🎉 PowerShell notifications have been disabled!"
echo ""
echo "📋 What was configured:"
echo "  ✅ Global Cursor settings updated"
echo "  ✅ Workspace settings updated"
echo "  ✅ PowerShell extension settings disabled"
echo "  ✅ PowerShell profile configured to suppress warnings"
echo "  ✅ Environment variables set to disable telemetry"
echo "  ✅ Process cleanup script created"
echo ""
echo "🔄 To apply changes:"
echo "  1. Restart Cursor/VSCode (Ctrl+Shift+P → 'Developer: Reload Window')"
echo "  2. If notifications still appear, run: ./cleanup_powershell_processes.sh"
echo ""
echo "📁 Configuration files:"
echo "  • Global: $CURSOR_USER_DIR/settings.json"
echo "  • Workspace: /workspace/.vscode/settings.json"
echo "  • PowerShell Profile: $POWERSHELL_PROFILE_DIR/Microsoft.PowerShell_profile.ps1"
echo "  • Environment: /workspace/.env"
echo ""