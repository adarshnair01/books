#!/bin/bash
echo "🚀 Syncing chapters..."
./venv/bin/python sync_to_web.py --all

echo "📦 Installing reader dependencies..."
cd frontend
npm install

IP_ADDR=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "✨ Starting Kindle Reader..."
echo "👉 Local:   http://localhost:5173/minimalist_genai_book/"
echo "🌐 Network: http://$IP_ADDR:5173/minimalist_genai_book/"
npm run dev -- --host
