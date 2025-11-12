# test_setup.py
import sys
print(f"✅ Python version: {sys.version}")
print(f"✅ Python location: {sys.executable}")

try:
    import flask
    print(f"✅ Flask installed: {flask.__version__}")
except ImportError:
    print("❌ Flask not installed")

try:
    import flask_cors
    print("✅ Flask-CORS installed")
except ImportError:
    print("❌ Flask-CORS not installed")

try:
    import mysql.connector
    print("✅ MySQL Connector installed")
except ImportError:
    print("❌ MySQL Connector not installed")

try:
    import werkzeug
    print(f"✅ Werkzeug installed: {werkzeug.__version__}")
except ImportError:
    print("❌ Werkzeug not installed")