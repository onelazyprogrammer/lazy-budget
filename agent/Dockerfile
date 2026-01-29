# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# We copy the entire 'agent' directory content to /app/agent
# But usually, it's better to copy the parent dir or be specific.
# Given the project structure, we reside in /agent, so we copy . to /app/agent
COPY . /app/agent/

# Add the root directory to PYTHONPATH so that 'agent.api' etc. can be imported
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "-m", "agent.main"]
