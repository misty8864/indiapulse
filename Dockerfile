FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY src/ src/
COPY .env .
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN pip install uv
RUN uv pip install --system -r pyproject.toml

# Set environment
ENV PYTHONPATH=src

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "indiapulse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
