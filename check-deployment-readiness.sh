#!/bin/bash

echo "🔍 Checking for hardcoded URLs in codebase..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0

# Check for localhost in source files
echo "1️⃣ Checking for 'localhost' in source files..."
if grep -r "localhost" --include="*.js" --include="*.jsx" --include="*.py" frontend/src/ backend/*.py 2>/dev/null | grep -v ".log" | grep -v "node_modules"; then
    echo -e "${RED}❌ Found hardcoded 'localhost' references${NC}"
    errors=$((errors + 1))
else
    echo -e "${GREEN}✅ No hardcoded 'localhost' found${NC}"
fi
echo ""

# Check for hardcoded http:// or https:// URLs
echo "2️⃣ Checking for hardcoded HTTP URLs..."
if grep -r "http://localhost\|https://localhost" --include="*.js" --include="*.jsx" --include="*.py" frontend/src/ backend/*.py 2>/dev/null | grep -v ".log" | grep -v "node_modules"; then
    echo -e "${RED}❌ Found hardcoded HTTP URLs${NC}"
    errors=$((errors + 1))
else
    echo -e "${GREEN}✅ No hardcoded HTTP URLs found${NC}"
fi
echo ""

# Check for environment variable usage
echo "3️⃣ Checking environment variable usage..."
if grep -r "process.env.REACT_APP_BACKEND_URL\|os.environ" --include="*.js" --include="*.jsx" --include="*.py" frontend/src/ backend/*.py | grep -v ".log" | grep -v "node_modules" > /dev/null; then
    echo -e "${GREEN}✅ Using environment variables correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify environment variable usage${NC}"
fi
echo ""

# Check if .env files exist
echo "4️⃣ Checking for .env files..."
if [ -f "frontend/.env" ] || [ -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Found .env files (should not be committed)${NC}"
    ls -la frontend/.env backend/.env 2>/dev/null
else
    echo -e "${GREEN}✅ No .env files in repo (good!)${NC}"
fi
echo ""

# Check if .env.example exists
echo "5️⃣ Checking for .env.example files..."
if [ -f ".env.example" ] && [ -f "frontend/.env.production" ] && [ -f "backend/.env.production" ]; then
    echo -e "${GREEN}✅ Found example environment files${NC}"
else
    echo -e "${RED}❌ Missing example environment files${NC}"
    errors=$((errors + 1))
fi
echo ""

# Check if vercel.json exists
echo "6️⃣ Checking for Vercel configuration..."
if [ -f "vercel.json" ] && [ -f "frontend/vercel.json" ]; then
    echo -e "${GREEN}✅ Found Vercel configuration files${NC}"
else
    echo -e "${RED}❌ Missing Vercel configuration files${NC}"
    errors=$((errors + 1))
fi
echo ""

# Summary
echo "================================"
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for deployment${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $errors issue(s). Please fix before deploying${NC}"
    exit 1
fi
