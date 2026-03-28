#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies with only binary packages (no source compilation)
pip install --only-binary=:all: -r requirements.txt || pip install -r requirements.txt
