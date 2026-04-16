#!/bin/bash

echo "🚀 RAG Chat Frontend Launcher"
echo "================================"
echo ""

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node version: $(node -v)"
echo "✓ NPM version: $(npm -v)"
echo ""

# Ask user what to do
echo "Choose an option:"
echo "  1) Start development server (npm run dev)"
echo "  2) Build for production (npm run build)"
echo "  3) Install dependencies (npm install)"
echo "  4) Preview production build (npm run preview)"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Starting development server..."
        echo "📍 Open http://localhost:5173 in your browser"
        echo ""
        npm run dev
        ;;
    2)
        echo ""
        echo "📦 Building for production..."
        npm run build
        echo ""
        echo "✓ Build complete! Output: app/static/dist/"
        ;;
    3)
        echo ""
        echo "📥 Installing dependencies..."
        npm install
        echo ""
        echo "✓ Dependencies installed!"
        ;;
    4)
        echo ""
        echo "👀 Previewing production build..."
        npm run preview
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
