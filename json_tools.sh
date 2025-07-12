#!/bin/bash

# JSON processing tools using jq
# ✅ jq successfully installed!

json_validate() {
    if [ -z "$1" ]; then
        echo "Usage: json_validate <file>"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "❌ File not found: $1"
        return 1
    fi
    
    if jq empty "$1" 2>/dev/null; then
        echo "✅ Valid JSON: $1"
        return 0
    else
        echo "❌ Invalid JSON: $1"
        jq empty "$1"
        return 1
    fi
}

json_format() {
    if [ -z "$1" ]; then
        echo "Usage: json_format <file>"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "❌ File not found: $1"
        return 1
    fi
    
    jq '.' "$1"
}

json_query() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: json_query <file> <jq_expression>"
        echo "Example: json_query package.json '.dependencies'"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "❌ File not found: $1"
        return 1
    fi
    
    jq "$2" "$1"
}

# Export functions
export -f json_validate json_format json_query

echo "🔧 JSON tools loaded:"
echo "  json_validate <file>  - Validate JSON file"
echo "  json_format <file>    - Format JSON file"
echo "  json_query <file> <q> - Query JSON file with jq syntax"
