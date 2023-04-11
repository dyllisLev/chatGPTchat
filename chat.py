from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
import yaml, datetime
import myai
import logging


class chatGPTChat:

    api_key = ""
    tokenKeys = ""
    history = {}
    chatGPT = None

    def __init__(self):
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.WARNING)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
        self.socketio = SocketIO(self.app)

        keys = self.get_yaml()
        self.api_key = str(keys['apiKey'])
        self.tokenKeys = str(keys['key'])
        
        self.app.config['SECRET_KEY'] = keys['flaskKey']
        
        try:
            self.chatGPT = myai.chatGPT(str(keys['apiKey']))

        except Exception as e:
            logging.debug('An error occurred:', e)
    
    def append_to_file(self, filename, text):
        with open(filename, 'a') as f:
            f.write(text+"\n")

    def get_yaml(self):
        try:
            with open('key.yaml', 'r') as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            data = {
                'key': 'key',
                'apiKey': 'apiKey',
                'flaskKey': 'flaskKey'
            }
            with open('key.yaml', 'w') as file:
                yaml.safe_dump(data, file)
        except yaml.YAMLError as e:
            logging.debug(e)
        return data

    def run(self):
        @self.socketio.on('connect')
        def handle_connect():
            join_room(request.sid)
            logging.debug("===================")
            logging.debug("connect : " + request.sid)
            logging.debug("===================")
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")
            self.history[request.sid] = ""
            emit('connect', request.sid)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            sid = request.sid
            logging.debug("===================")
            logging.debug("disconnect : " + request.sid)
            logging.debug("===================")
            if self.chatGPT.getHistory(request.sid) is not None:
                del self.chatGPT.history[request.sid]
            leave_room(sid)

        @self.app.route('/')
        def index():
            token = request.args.get('token')
            
            logging.debug("===================")
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")

            if token in self.get_yaml()['key'].split(", "):
                return render_template('index.html')
            else:
                return 'Unauthorized access!'

        @self.socketio.on('message')
        def handle_message(data):
            
            remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logging.debug('connect to IP : %s' % str(remote_addr))
            logging.debug("===================")

            try:
                
                logging.debug( "api_key :%s"%self.api_key)

                start_date = datetime.datetime.now()
                
                self.append_to_file("chat.log", "==========START %s========="%start_date.strftime("%Y/%m/%d %H:%M:%S"))
                self.append_to_file("chat.log", '질문자 : ' + remote_addr + " / " + data['room'])
                self.append_to_file("chat.log", '질문 : ' + data['message'])
                
                logging.debug("===================")
                logging.debug('질문자 : ' + data['room'])
                logging.debug('질문 : ' + data['message'])

                for re in self.chatGPT.openaiPromt(data['room'], data['message']):
                    aimsg = str(re.message['content'])
                    self.append_to_file("chat.log", '답변 : ' + aimsg)
                    logging.debug('답변 : ' + aimsg)
                    emit('response', aimsg, room=data['room'])
                
                end_date = datetime.datetime.now()
                time_diff = end_date - start_date
                time_diff_in_seconds = time_diff.total_seconds()
                self.append_to_file("chat.log", "==========소요시간 : %s========="%time_diff_in_seconds)
                self.append_to_file("chat.log", "==========END %s=============="%end_date.strftime("%Y/%m/%d %H:%M:%S"))
                logging.debug("===================")

            except Exception as e:
                logging.debug('An error occurred:', e)

        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    
    app = chatGPTChat()
    app.run()
