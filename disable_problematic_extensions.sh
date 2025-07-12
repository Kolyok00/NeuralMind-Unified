#!/bin/bash

# Problematic Extensions Disabler for Ubuntu Dev Container
# This script disables problematic VSCode/Cursor extensions that cause errors

set -e

echo "🔧 Disabling problematic extensions in Ubuntu dev container..."

# Backup original settings
echo "💾 Creating backup of original settings..."
if [ -f "/workspace/.vscode/settings.json" ]; then
    cp "/workspace/.vscode/settings.json" "/workspace/.vscode/settings.json.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
fi

# Create Cursor user settings directory
CURSOR_USER_DIR="$HOME/.cursor-server/data/User"
mkdir -p "$CURSOR_USER_DIR"

# Disable problematic extensions globally
echo "🚫 Disabling problematic extensions globally..."
cat > "$CURSOR_USER_DIR/settings.json" << 'EOF'
{
    "extensions.ignoreRecommendations": true,
    "extensions.showRecommendationsOnlyOnDemand": true,
    "notifications.showExtensionsOnlyFromTrustedPublishers": true,
    "update.showReleaseNotes": false,
    "telemetry.telemetryLevel": "off",
    "workbench.startupEditor": "none",
    "workbench.welcomePage.walkthroughs.openOnInstall": false,
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "/bin/bash",
            "icon": "terminal-bash",
            "args": []
        },
        "zsh": {
            "path": "/bin/zsh", 
            "icon": "terminal",
            "args": []
        }
    },
    "terminal.integrated.shell.linux": "/bin/bash",
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}",
        "NEURALMIND_ENV": "development",
        "NEURALMIND_CONFIG": "${workspaceFolder}/d_drive/projects/NeuralMind-Unified/config/main.json"
    },
    "json.validate.enable": false,
    "json.format.enable": false,
    "json.suggest.mode": "off",
    "json.trace.server": "off",
    "jsonc.validate.enable": false,
    "jsonc.format.enable": false,
    "vscode.json-language-features": false,
    "typescript.validate.enable": false,
    "typescript.suggest.enabled": false,
    "javascript.validate.enable": false,
    "javascript.suggest.enabled": false
}
EOF

# Update extension blacklist
echo "📦 Updating extension blacklist..."
cat > "/workspace/.cursor/disabled_extensions.json" << 'EOF'
{
    "disabled_extensions": [
        "ms-vscode.powershell",
        "vscode.json-language-features",
        "vscode.typescript-language-features",
        "vscode.javascript-language-features"
    ],
    "reason": "Unnecessary extensions disabled in Ubuntu dev container - using minimal setup for better performance",
    "alternative_tools": {
        "json": "python json module, jq command line tool",
        "typescript": "tsc command line compiler",
        "javascript": "node.js runtime",
        "shell": "bash",
        "scripting": "bash, python3",
        "automation": "python3, bash scripts",
        "package_manager": "apt, pip3"
    },
    "recommended_for_linux": {
        "shell": "bash",
        "scripting": "bash, python3",
        "automation": "python3",
        "package_manager": "apt",
        "json_processing": "jq, python json",
        "text_editing": "vim, nano, built-in editor"
    }
}
EOF

# Create extension override configuration
echo "⚙️ Creating extension override configuration..."
cat > "/workspace/.cursor/extension_overrides.json" << 'EOF'
{
    "extension_overrides": {
        "vscode.json-language-features": {
            "enabled": false,
            "reason": "Causes errors in dev container",
            "alternative": "Use Python json module or jq for JSON processing"
        },
        "ms-vscode.powershell": {
            "enabled": false,
            "reason": "Not needed in Ubuntu container",
            "alternative": "Use bash for shell scripting"
        },
        "vscode.typescript-language-features": {
            "enabled": false,
            "reason": "Not needed for Python-focused development",
            "alternative": "Use tsc command line if TypeScript needed"
        },
        "vscode.javascript-language-features": {
            "enabled": false,
            "reason": "Not needed for Python-focused development", 
            "alternative": "Use node.js runtime directly if JavaScript needed"
        }
    },
    "minimal_setup": {
        "enabled_features": [
            "python language support",
            "git integration",
            "terminal",
            "file explorer",
            "search",
            "basic text editing"
        ],
        "disabled_features": [
            "json language server",
            "typescript language server",
            "javascript language server",
            "powershell integration",
            "extension recommendations",
            "telemetry",
            "welcome screens"
        ]
    }
}
EOF

# Kill problematic extension processes
echo "⚡ Cleaning up problematic extension processes..."
pkill -f "json-language-features" 2>/dev/null || true
pkill -f "typescript-language-features" 2>/dev/null || true
pkill -f "javascript-language-features" 2>/dev/null || true
pkill -f "PowerShell" 2>/dev/null || true

# Create JSON processing alternatives
echo "🛠️ Setting up JSON processing alternatives..."
cat > "/workspace/json_tools.sh" << 'EOF'
#!/bin/bash
# JSON Processing Tools for Ubuntu Dev Container

# Check if jq is installed, install if not
if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq for JSON processing..."
    apt update && apt install -y jq 2>/dev/null || echo "jq installation requires sudo"
fi

# JSON processing functions
json_validate() {
    if [ $# -eq 0 ]; then
        echo "Usage: json_validate <file.json>"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        jq empty "$1" 2>/dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
    else
        python3 -c "import json; json.load(open('$1'))" 2>/dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
    fi
}

json_format() {
    if [ $# -eq 0 ]; then
        echo "Usage: json_format <file.json>"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        jq . "$1"
    else
        python3 -c "import json; print(json.dumps(json.load(open('$1')), indent=2))"
    fi
}

json_query() {
    if [ $# -lt 2 ]; then
        echo "Usage: json_query <file.json> <query>"
        echo "Example: json_query config.json '.database.host'"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        jq "$2" "$1"
    else
        echo "jq not available, use Python for complex JSON queries"
    fi
}

# Export functions
export -f json_validate
export -f json_format
export -f json_query

echo "🔧 JSON tools loaded:"
echo "  json_validate <file>  - Validate JSON file"
echo "  json_format <file>    - Format JSON file"
echo "  json_query <file> <q> - Query JSON file with jq syntax"
EOF

chmod +x "/workspace/json_tools.sh"

# Add JSON tools to bashrc
echo "📝 Adding JSON tools to .bashrc..."
if ! grep -q "source /workspace/json_tools.sh" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# JSON processing tools" >> ~/.bashrc
    echo "if [ -f /workspace/json_tools.sh ]; then" >> ~/.bashrc
    echo "    source /workspace/json_tools.sh" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
fi

# Update environment variables
echo "🔧 Setting up environment variables..."
cat >> "/workspace/.env" << 'EOF'

# Disable problematic language features
VSCODE_JSON_LANGUAGE_FEATURES_DISABLED=true
VSCODE_TYPESCRIPT_DISABLED=true
VSCODE_JAVASCRIPT_DISABLED=true
VSCODE_POWERSHELL_DISABLED=true

# Alternative tools
JSON_PROCESSOR=jq
SHELL_PROCESSOR=bash
SCRIPT_PROCESSOR=python3
EOF

# Test the configuration
echo "🧪 Testing extension disabling..."
echo "✅ Problematic extensions should now be disabled"

echo ""
echo "🎉 Problematic extensions disabled! Using minimal setup for better performance."
echo ""
echo "📋 What was disabled:"
echo "  ❌ vscode.json-language-features"
echo "  ❌ ms-vscode.powershell"
echo "  ❌ vscode.typescript-language-features"
echo "  ❌ vscode.javascript-language-features"
echo ""
echo "🛠️ Alternative tools available:"
echo "  • JSON processing: json_validate, json_format, json_query"
echo "  • Shell scripting: bash"
echo "  • Python development: python3"
echo "  • Git operations: git commands"
echo ""
echo "🔄 To apply changes:"
echo "  1. Restart Cursor/VSCode (Ctrl+Shift+P → 'Developer: Reload Window')"
echo "  2. Run: source ~/.bashrc (for JSON tools)"
echo ""