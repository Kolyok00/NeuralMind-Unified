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
