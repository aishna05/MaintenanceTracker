#!/bin/bash

# GearGuard - Quick Start Script
# This script will set up and run your Django server

echo "🚀 Starting GearGuard Maintenance Tracker..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Run migrations
echo "🗄️  Setting up database..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Django development server..."
echo "📱 Open your browser at: http://127.0.0.1:8000/"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the server
python manage.py runserver

