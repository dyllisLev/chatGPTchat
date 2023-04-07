import openai, os, json
import logging
# 로그 파일 설정
logging.basicConfig(filename='my_log_file.log', level=logging.DEBUG)

class chatGPT:

    apiKey = ""
    history = {}

    def __init__(self, apiKey):
        logging.debug( "self.apiKey : %s"%self.apiKey )
        self.apiKey = apiKey
        logging.debug( "self.apiKey : %s"%self.apiKey )

    def setHistoryById(self, id):
        if id not in self.history:
            self.history[id] = {"historyContent": []}

    def saveHistory(self, id, type, msg):
        self.history[id]['historyContent'].append({"role": type, "content": msg})
        

    def getHistory(self, id):
        if id in self.history:
            return self.history[id]['historyContent']
        else:
            self.setHistoryById(id)
            return None
            
    def openaiPromt(self, sid, promt):
        
        self.setHistoryById(sid)
        
        openai.api_key = self.apiKey

        # logging.debug( "sid : %s"%sid )
        # logging.debug( "promt : %s"%promt )

        # logging.debug( self.history )
        self.saveHistory(sid, "user", promt)
        # logging.debug( self.history )

        # Define the messages for the GPT-3.5-turbo model
        # messages = [
        #     # {"role": "system", "content": ""},
        #     {"role": "user", "content": promt},
        # ]


        messages = self.getHistory(sid)
        # logging.debug( hi )
        # logging.debug( messages )


        # Call the OpenAI API with the GPT-3.5-turbo model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.8,
        )
        self.saveHistory(sid, "assistant", response.choices[0].message['content'])
        # logging.debug( messages )
        return response.choices
