#!/bin/bash

echo "🐳 Starting Weaviate with Docker..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo "   1. Open Applications folder"
    echo "   2. Double-click Docker.app"
    echo "   3. Wait for the Docker whale icon to appear in menu bar"
    echo "   4. Run this script again"
    exit 1
fi

# Stop existing Weaviate container if running
if docker ps -q -f name=weaviate >/dev/null 2>&1; then
    echo "🛑 Stopping existing Weaviate container..."
    docker stop weaviate
    docker rm weaviate
fi

# Start Weaviate container
echo "🚀 Starting Weaviate container..."
docker run -d \
    --name weaviate \
    -p 8080:8080 \
    -e QUERY_DEFAULTS_LIMIT=25 \
    -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
    -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
    -e DEFAULT_VECTORIZER_MODULE='none' \
    -e ENABLE_MODULES='text2vec-openai,generative-openai' \
    -e CLUSTER_HOSTNAME='node1' \
    semitechnologies/weaviate:1.25.0

# Wait for Weaviate to be ready
echo "⏳ Waiting for Weaviate to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/v1/meta >/dev/null 2>&1; then
        echo "✅ Weaviate is ready!"
        echo "🌐 Weaviate is running at: http://localhost:8080"
        exit 0
    fi
    echo "   Attempt $i/30..."
    sleep 2
done

echo "❌ Weaviate failed to start within 60 seconds"
echo "   Check Docker logs with: docker logs weaviate"
exit 1