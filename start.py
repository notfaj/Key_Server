from keyserver import app
from waitress import serve

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)  # Change the port if needed
