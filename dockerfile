# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Expose any ports that might be used (for the GUI, for instance)
EXPOSE 5000

# Run the CLI tool by default (this could be changed to start the GUI if needed)
ENTRYPOINT ["python", "moonball_archiver.py"]
