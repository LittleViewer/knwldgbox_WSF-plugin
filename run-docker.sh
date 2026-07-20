#!/bin/bash
echo "🚀 Building and starting KNWLDGBox via Docker Compose..."
docker compose up -d --build

echo ""
echo "✅ KNWLDGBox is running in the background!"
echo "🌐 Open your browser to: http://127.0.0.1:8000"
echo ""
echo "To view logs:     docker compose logs -f"
echo "To stop:          docker compose down"
echo "To authenticate ghunt:  docker compose exec knwldgbox ghunt login"
