#!/usr/bin/bash
echo "Running Veronica..."
gunicorn "/chat_app/create_app:create_app()"