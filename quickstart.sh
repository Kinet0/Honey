#!/bin/bash

# Quick start script for Honeypot Dashboard

set -e

echo "🔍 Honeypot Dashboard - Quick Start"
echo "===================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Create .env files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "✅ Created frontend/.env.local"
fi

echo ""
echo "🚀 Starting Honeypot Dashboard..."
echo ""

# Start services
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🗄️  Database: localhost:5432"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.dev.yml down"
echo ""
