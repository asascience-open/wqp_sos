from wqp_sos import app
import os

if os.environ.get("APPLICATION_SETTINGS") == 'development.py':
    app.run(host="0.0.0.0", port=3000)
