# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based CRM (Customer Relationship Management) system designed to convert an existing Django-based project to Flask. The system manages customers, products, stores, and store employees in an integrated web application.

## Development Environment Setup

The project uses a Python virtual environment with Flask:

```bash
# Activate virtual environment
venv/Scripts/activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py
```

The Flask application runs on port 5000 (debug mode) with the following endpoints:
- `/` - Hello World page
- `/health` - Health check endpoint

## Database Configuration

The system is designed to work with MySQL:
- Database: crm
- User: crmuser
- Password: 1234
- Host: localhost:3306
- Connection URL: mysql+pymysql://crmuser:1234@localhost:3306/crm

## Architecture

This is currently a minimal Flask application that will be expanded to include:

- **Authentication System**: User login/logout with session management
- **Customer Management**: CRUD operations with search and pagination
- **Product Management**: Category-based product management with inventory tracking
- **Store Management**: Store operations with business status tracking
- **Employee Management**: Staff management with role and department tracking

The application is intended to run on port 8000 in production but currently uses Flask's default port 5000 in development mode.

## Key Features to Implement

- User authentication and session management
- Customer registration, editing, deletion with search capabilities
- Product catalog with categories and inventory management
- Store operations with automatic business year calculations
- Employee management with automatic tenure calculations and salary tracking

## Development Notes

This is an early-stage Flask project being converted from a Django codebase. The current implementation contains only basic Flask setup with health check endpoints.