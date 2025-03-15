from app import app

# Expose the Flask app as a Vercel serverless function
def handler(event, context):
    return app(event, context)
