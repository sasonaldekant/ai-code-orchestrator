# Multi-language sandbox for AI Code Orchestrator
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for React/TS/JS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install .NET SDK (for C#)
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-sdk-7.0

# Install Python dependencies (commonly used for analysis)
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    requests \
    pytest \
    scikit-learn

# Set up work directory
WORKDIR /sandbox

# Create a non-root user for security
RUN useradd -m -u 1000 sanduser
USER sanduser

# Entry point
CMD ["/bin/bash"]
