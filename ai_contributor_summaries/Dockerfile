FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs mock_data

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/health || exit 1

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting AI Contributor Summaries..."\n\
\n\
# Wait for Weaviate to be ready\n\
echo "Waiting for Weaviate to be ready..."\n\
while ! curl -s $WEAVIATE_URL/v1/meta > /dev/null; do\n\
  echo "Weaviate is not ready yet. Waiting..."\n\
  sleep 2\n\
done\n\
echo "Weaviate is ready!"\n\
\n\
# Initialize schema\n\
echo "Initializing Weaviate schema..."\n\
python -m summarization.run_pipeline init-schema || echo "Schema already exists"\n\
\n\
# Start the application\n\
echo "Starting Streamlit application..."\n\
exec streamlit run ui/streamlit_app.py --server.port=$STREAMLIT_SERVER_PORT --server.address=$STREAMLIT_SERVER_ADDRESS\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default command
CMD ["/app/entrypoint.sh"]