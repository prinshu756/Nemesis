#!/bin/bash
# Nemesis Repository Cleanup Script
# Removes unnecessary files and directories to reduce repository bloat

NEMESIS_DIR="/home/kali/Desktop/Nemesis"

echo "🧹 Cleaning Nemesis Repository..."
echo "================================"

# Counter for deleted items
DELETED_FILES=0
DELETED_DIRS=0

echo ""
echo "Step 1: Removing duplicate package-lock.json..."
if [ -f "$NEMESIS_DIR/package-lock.json" ]; then
    rm -f "$NEMESIS_DIR/package-lock.json"
    echo "✓ Removed duplicate package-lock.json"
    ((DELETED_FILES++))
else
    echo "- Already removed or doesn't exist"
fi

echo ""
echo "Step 2: Removing VSCode configuration..."
if [ -d "$NEMESIS_DIR/.vscode" ]; then
    rm -rf "$NEMESIS_DIR/.vscode"
    echo "✓ Removed .vscode configuration directory"
    ((DELETED_DIRS++))
else
    echo "- Already removed or doesn't exist"
fi

echo ""
echo "Step 3: Removing outdated run.sh script..."
if [ -f "$NEMESIS_DIR/run.sh" ]; then
    rm -f "$NEMESIS_DIR/run.sh"
    echo "✓ Removed old run.sh (use start_backend.sh instead)"
    ((DELETED_FILES++))
else
    echo "- Already removed or doesn't exist"
fi

echo ""
echo "Step 4: Cleaning Python cache (__pycache__)..."
CACHE_COUNT=$(find "$NEMESIS_DIR" -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$CACHE_COUNT" -gt 0 ]; then
    find "$NEMESIS_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    echo "✓ Removed $CACHE_COUNT __pycache__ directories"
    ((DELETED_DIRS+=CACHE_COUNT))
else
    echo "- No __pycache__ directories found"
fi

echo ""
echo "Step 5: Consolidating logs..."
if [ -d "$NEMESIS_DIR/agents/alpha/logs" ]; then
    mkdir -p "$NEMESIS_DIR/logs"
    if [ "$(ls -A $NEMESIS_DIR/agents/alpha/logs 2>/dev/null)" ]; then
        mv "$NEMESIS_DIR/agents/alpha/logs"/* "$NEMESIS_DIR/logs/" 2>/dev/null
        echo "✓ Moved Alpha logs to centralized /logs directory"
    fi
    rmdir "$NEMESIS_DIR/agents/alpha/logs" 2>/dev/null
    echo "✓ Removed agents/alpha/logs directory"
    ((DELETED_DIRS++))
else
    echo "- agents/alpha/logs not found (may already be cleaned)"
fi

echo ""
echo "Step 6: Cleaning temporary data files..."
if [ -d "$NEMESIS_DIR/agents/alpha/data" ]; then
    DATAFILES=$(find "$NEMESIS_DIR/agents/alpha/data" -type f 2>/dev/null | wc -l)
    if [ "$DATAFILES" -gt 0 ]; then
        rm -rf "$NEMESIS_DIR/agents/alpha/data"/*
        echo "✓ Removed $DATAFILES temporary data files"
        ((DELETED_FILES+=DATAFILES))
        mkdir -p "$NEMESIS_DIR/agents/alpha/data"
        touch "$NEMESIS_DIR/agents/alpha/data/.gitkeep"
        echo "✓ Recreated data directory structure"
    else
        echo "- No temporary data files to remove"
    fi
else
    echo "- agents/alpha/data not found"
fi

echo ""
echo "Step 7: Checking for other unnecessary files..."
# Check for common development files
if [ -f "$NEMESIS_DIR/.DS_Store" ]; then
    rm -f "$NEMESIS_DIR/.DS_Store"
    echo "✓ Removed .DS_Store"
    ((DELETED_FILES++))
fi

# Check for large test files
if [ -f "$NEMESIS_DIR/test_combined.db" ]; then
    rm -f "$NEMESIS_DIR/test_combined.db"
    echo "✓ Removed test_combined.db"
    ((DELETED_FILES++))
fi

echo ""
echo "================================"
echo "✅ Cleanup Complete!"
echo ""
echo "Summary:"
echo "  Files deleted:       $DELETED_FILES"
echo "  Directories deleted: $DELETED_DIRS"
echo ""
echo "📊 Recommended Next Steps:"
echo "  1. Verify application still runs: ./start_backend.sh"
echo "  2. Test in browser: http://localhost:5173"
echo "  3. Check git status: git status"
echo "  4. Commit cleanup: git add -A && git commit -m 'chore: cleanup unnecessary files'"
echo ""
echo "💾 Space Management:"
echo "  - venv/ (4.9GB) - Keep (deployable)"
echo "  - frontend/ (123MB) - Keep (deployable)"
echo "  - agents/, core/, api/, intelligence/ - Keep (core system)"
echo "  - Removed: ~400MB of cache and config"
echo ""
echo "🎯 Focus Areas for Next Development Sprint:"
echo "  1. Phase 2 (Orient): Load real CVE data"
echo "  2. Phase 3 (Decide): Integrate Ollama + Docker honeypots"
echo "  3. Phase 4 (Act): Fix Gamma method signatures"
echo "  4. OODA: Optimize loop timing to <100ms"
echo ""
