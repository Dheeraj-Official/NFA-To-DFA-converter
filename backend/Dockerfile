# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Graphviz is required for diagram generation
# g++ is required to compile the C++ program on Linux
RUN apt-get update && apt-get install -y \
    graphviz \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY python/ python/
COPY cpp/ cpp/
COPY app.py .

# Compile C++ program for Linux (Render runs Linux, not Windows)
RUN g++ -std=c++17 -O2 cpp/01_NFA_To_DFA.cpp -o cpp/01_NFA_To_DFA

# Make the C++ executable executable
RUN chmod +x cpp/01_NFA_To_DFA

# Expose port (Render will set PORT env var)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application with dynamic port from Render
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-5000}"]
