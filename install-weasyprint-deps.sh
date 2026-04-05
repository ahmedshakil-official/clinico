#!/usr/bin/env bash
set -e

# Update apt and install WeasyPrint system dependencies
export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get install -y \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libxml2 \
    libjpeg62-turbo \
    libpng16-16 \
    fonts-dejavu-core \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*
