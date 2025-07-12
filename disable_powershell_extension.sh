#!/bin/bash

# PowerShell Extension Disabler for Ubuntu Dev Container
# This script completely disables PowerShell extension in Cursor/VSCode for Linux development

set -e

echo "🐧 Disabling PowerShell extension for Ubuntu dev container..."

# Backup original settings
echo "💾 Creating backup of original settings..."
if [ -f "/workspace/.vscode/settings.json" ]; then
    cp "/workspace/.vscode/settings.json" "/workspace/.vscode/settings.json.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
fi

# Create Cursor user settings directory
CURSOR_USER_DIR="$HOME/.cursor-server/data/User"
mkdir -p "$CURSOR_USER_DIR"

# Disable PowerShell extension globally
echo "🔧 Disabling PowerShell extension globally..."
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
    }
}
EOF

# Create extension blacklist
echo "📦 Creating extension blacklist..."
cat > "/workspace/.cursor/disabled_extensions.json" << 'EOF'
{
    "disabled_extensions": [
        "ms-vscode.powershell"
    ],
    "reason": "PowerShell not needed in Ubuntu dev container - using Bash instead",
    "alternative_shells": [
        "bash",
        "zsh",
        "fish"
    ],
    "recommended_for_linux": {
        "shell": "bash",
        "scripting": "bash",
        "automation": "python3",
        "package_manager": "apt"
    }
}
EOF

# Remove PowerShell from terminal profiles
echo "🖥️ Configuring terminal profiles for Linux..."
cat > "/workspace/.cursor/terminal_config.json" << 'EOF'
{
    "terminal": {
        "defaultProfile": "bash",
        "profiles": {
            "bash": {
                "path": "/bin/bash",
                "icon": "terminal-bash",
                "description": "Default Bash shell for Ubuntu",
                "args": ["--login"]
            },
            "zsh": {
                "path": "/bin/zsh",
                "icon": "terminal",
                "description": "Z shell (if installed)",
                "args": []
            },
            "fish": {
                "path": "/usr/bin/fish",
                "icon": "terminal",
                "description": "Fish shell (if installed)",
                "args": []
            }
        },
        "environment": {
            "SHELL": "/bin/bash",
            "TERM": "xterm-256color",
            "PYTHONPATH": "/workspace/d_drive/projects/NeuralMind-Unified",
            "NEURALMIND_ENV": "development"
        }
    }
}
EOF

# Create NeuralMind bash aliases
echo "⚡ Creating NeuralMind bash aliases..."
cat > "/workspace/.bashrc_neuralmind" << 'EOF'
#!/bin/bash
# NeuralMind Bash Aliases and Functions

# Set NeuralMind environment
export NEURALMIND_PATH="/workspace/d_drive/projects/NeuralMind-Unified"
export PYTHONPATH="$NEURALMIND_PATH"
export NEURALMIND_ENV="development"

# NeuralMind aliases
alias neuralmind='cd "$NEURALMIND_PATH" && python3 main.py'
alias mcp='cd "$NEURALMIND_PATH" && python3 -m neuralmind.mcp_server'
alias neural-cd='cd "$NEURALMIND_PATH"'
alias neural-status='cd "$NEURALMIND_PATH" && python3 main.py --help'
alias neural-test='cd "$NEURALMIND_PATH" && python3 -c "import neuralmind; print(\"NeuralMind module loaded successfully\")"'

# Useful Linux aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# Python aliases
alias py='python3'
alias pip='pip3'
alias venv='python3 -m venv'

# Docker aliases (if needed)
alias dps='docker ps'
alias dimg='docker images'
alias dlog='docker logs'

# NeuralMind functions
neuralmind-help() {
    echo "🧠 NeuralMind Commands:"
    echo "  neuralmind      - Start NeuralMind application"
    echo "  mcp             - Start MCP server"
    echo "  neural-cd       - Go to NeuralMind directory"
    echo "  neural-status   - Check NeuralMind status"
    echo "  neural-test     - Test NeuralMind module import"
    echo ""
    echo "📁 Current NeuralMind path: $NEURALMIND_PATH"
    echo "🐍 Python path: $PYTHONPATH"
    echo "🔧 Environment: $NEURALMIND_ENV"
}

# Custom prompt with NeuralMind info
neuralmind-prompt() {
    local git_branch=""
    if [ -d .git ]; then
        git_branch=" ($(git branch --show-current 2>/dev/null))"
    fi
    
    PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[33m\]$git_branch\[\033[00m\]$ "
}

# Welcome message
echo "🧠 NeuralMind Development Environment Ready!"
echo "📍 Use 'neuralmind-help' for available commands"
echo "🐧 Running on Ubuntu with Bash (no PowerShell needed!)"
EOF

# Add NeuralMind aliases to bashrc
echo "📝 Adding NeuralMind aliases to .bashrc..."
if ! grep -q "source /workspace/.bashrc_neuralmind" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# NeuralMind aliases and functions" >> ~/.bashrc
    echo "if [ -f /workspace/.bashrc_neuralmind ]; then" >> ~/.bashrc
    echo "    source /workspace/.bashrc_neuralmind" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
fi

# Create environment file
echo "🔧 Setting up environment variables..."
cat >> "/workspace/.env" << 'EOF'

# Linux/Bash environment (no PowerShell)
SHELL=/bin/bash
TERM=xterm-256color
NEURALMIND_SHELL=bash
DISABLE_POWERSHELL=true
EOF

# Kill any PowerShell processes
echo "⚡ Cleaning up PowerShell processes..."
pkill -f "PowerShell" 2>/dev/null || true
pkill -f "pwsh" 2>/dev/null || true
pkill -f "Microsoft.PowerShell" 2>/dev/null || true

# Remove PowerShell installation attempts
echo "🗑️ Removing PowerShell installation files..."
rm -f /workspace/install_powershell.sh 2>/dev/null || true
rm -f /workspace/cleanup_powershell_processes.sh 2>/dev/null || true

# Test bash environment
echo "🧪 Testing bash environment..."
bash -c "source /workspace/.bashrc_neuralmind && neuralmind-help"

echo ""
echo "🎉 PowerShell extension disabled! Using Bash for Ubuntu development."
echo ""
echo "📋 What was configured:"
echo "  ✅ PowerShell extension disabled globally"
echo "  ✅ Terminal profiles set to Bash/Zsh only"
echo "  ✅ NeuralMind bash aliases created"
echo "  ✅ Environment variables configured for Linux"
echo "  ✅ PowerShell processes cleaned up"
echo "  ✅ PowerShell installation files removed"
echo ""
echo "🐧 Linux/Bash commands:"
echo "  • neuralmind        - Start NeuralMind"
echo "  • mcp               - Start MCP server"
echo "  • neural-cd         - Go to project directory"
echo "  • neuralmind-help   - Show all commands"
echo ""
echo "🔄 To apply changes:"
echo "  1. Restart Cursor/VSCode terminal"
echo "  2. Or run: source ~/.bashrc"
echo ""