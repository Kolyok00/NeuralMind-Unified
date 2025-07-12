#!/bin/bash
# Kill PowerShell extension processes that might show notifications
pkill -f "PowerShell Editor Services" 2>/dev/null || true
pkill -f "pwsh.*LanguageServer" 2>/dev/null || true
pkill -f "Microsoft.PowerShell.EditorServices" 2>/dev/null || true
echo "PowerShell extension processes cleaned up"
