from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from werkzeug.middleware.proxy_fix import ProxyFix
import yaml
import myai
import logging


class chatGPTChat:

    api_key = ""
    tokenKeys = ""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
        self.socketio = SocketIO(self.app)

        keys = self.get_yaml()
        self.api_key = str(keys['apiKey'])
        self.tokenKeys = str(keys['key'])
        flaskKey = keys['flaskKey']

        self.app.config['SECRET_KEY'] = flaskKey
        self.app.logger.setLevel(logging.WARNING)

    def get_yaml(self):
        with open('key.yaml', 'r') as file:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                logging.debug(e)
        return data

    def run(self):
        @self.socketio.on('connect')
        def handle_connect():
            join_room(request.sid)
            # logging.debug("===================")
            # logging.debug(request.sid)
            logging.debug("===================")
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")
            emit('connect', request.sid)

        @self.app.route('/')
        def index():
            token = request.args.get('token')
            
            logging.debug("===================")
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")

            if token in self.tokenKeys.split(", "):
                return render_template('index.html')
            else:
                return 'Unauthorized access!'

        @self.socketio.on('message')
        def handle_message(data):
            logging.debug('received args: ' + data['message'])
            logging.debug('received args: ' + data['room'])
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")

            try:
                
                logging.debug( "api_key :%s"%self.api_key)

                for re in myai.openaiPromt(self.api_key, data['message']):
                    aimsg = str(re.message['content'])
                    logging.debug(re.message['content'])
                    emit('response', aimsg, room=data['room'])

            except Exception as e:
                logging.debug('An error occurred:', e)

        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    app = chatGPTChat()
    app.run()