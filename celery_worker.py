#!/usr/bin/env python3
"""
Celery Worker Entry Point
"""

from src.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start() 