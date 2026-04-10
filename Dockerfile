# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Set environment variable
ENV PORT=5000

# Expose port
EXPOSE 5000

ENV PYTHONPATH="/app"

# Run the app
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --chdir app app:app"]


