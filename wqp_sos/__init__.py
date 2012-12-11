from flask import Flask

# Create application object
app = Flask(__name__)

app.config.from_object('wqp_sos.defaults')
app.config.from_envvar('APPLICATION_SETTINGS', silent=True)

# Create logging
if app.config.get('LOG_FILE') == True:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('logs/wqp_sos.txt')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

# Import everything
import wqp_sos.views