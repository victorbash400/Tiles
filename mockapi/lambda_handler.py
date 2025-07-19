import json
import os
from mangum import Mangum

from main import app
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse


# Remove the startup event handler since Lambda doesn't support it
# Database initialization will be handled on first request
app.router.routes = [route for route in app.router.routes if not hasattr(route, 'endpoint') or route.endpoint.__name__ != 'startup_event']

# Add global exception handler to log errors with traceback
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}")
    traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logging.error(traceback_str)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Initialize database on first import
def initialize_database():
    try:
        from dynamodb_database import create_tables, clear_all_tables
        create_tables()
        print("✅ DynamoDB tables created for Lambda")
        
        # Only clear database if explicitly requested via environment variable
        if os.getenv('CLEAR_DATABASE_ON_START', 'false').lower() == 'true':
            clear_all_tables()
            print("✅ DynamoDB tables cleared for fresh demo")
        else:
            print("ℹ️ Database clearing skipped (set CLEAR_DATABASE_ON_START=true to enable)")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        traceback.print_exc()
        # Continue without database for hackathon demo

# Initialize database when module is imported
initialize_database()

# Create Lambda handler using Mangum
handler = Mangum(app, lifespan="off")