import json
from apiai import *

CLIENT_ACCESS_TOKEN = "8793229baaf24ce2ba1e98214563969f"

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

request = ai.text_request()

#request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"

request.query = "I write to get your help in the transfer of US $ 10,500,000.00 dollars, I'm in Ghana."

response = request.getresponse()

resp = json.loads(response.read())

def get_responses(response ):
    ret = list()
    if type(response) == dict:
        for key,value in response.items():
            if type(value) == dict or type(value) == list:
                ret += get_responses(value)
            elif key == "speech" and len(value) != 0:
                ret.append(value)
    elif type(response) == list:
        for value in response:
            ret += get_responses(value)
    return ret
    

print((get_responses(resp)))
