# Dockerfile for TwinSecure AI Backend

# --- Base Stage ---
# Use an official Python runtime as a parent image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1

# Install system dependencies (if needed, e.g., for WeasyPrint or other libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpango-1.0-0 libcairo2 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 \
#     # Add other dependencies here (e.g., wkhtmltopdf for pdfkit)
#     && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set the working directory in the container
WORKDIR /app

# --- Builder Stage ---
# Used to install dependencies
FROM base as builder

# Copy only necessary files to leverage Docker cache
# COPY pyproject.toml poetry.lock* ./

# Install dependencies using poetry
# --no-root: Don't install the project itself, only dependencies
# --no-dev: Exclude development dependencies
# Use this if you switch to using pyproject.toml instead of requirements.txt
# RUN poetry install --no-root --no-dev --no-interaction --no-ansi

# --- OR ---

# If using requirements.txt (simpler for this example)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
# Final image with the application code
FROM base as runtime

WORKDIR /app

# Copy installed dependencies from the builder stage
# If using Poetry:
# COPY --from=builder /opt/pypoetry/ /opt/pypoetry/
# ENV PATH="/opt/pypoetry/bin:$PATH"
# If using requirements.txt:
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY ./app . 

COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /home/appuser/app 
# Change workdir to user's home
COPY --chown=appuser:appuser ./app /home/appuser/app/app
COPY --chown=appuser:appuser ./alembic /home/appuser/app/alembic
COPY --chown=appuser:appuser alembic.ini /home/appuser/app/alembic.ini


# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# The entrypoint script can handle migrations before starting
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Using reload for development (change for production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

