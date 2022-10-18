#!/usr/bin/python3
from flask import Flask, request 
import json

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def post_request():
        if request.method == 'POST': 
            inputString = request.values['inputString']
             
            return respond(None,word_replacer(inputString))
            
        if request.method == 'GET' :
            return respond(None, 'Welcome to Word Replacer API')
 
def word_replacer(input_string):
    replce_words_list = ['Oracle', 'Google', 'Microsoft','Amazon' , 'Deloitte' ]
    
    output = ''
    for word in input_string.split():
        if word in replce_words_list:
            word = word + r'©'
        output = output + word + ' '
    return output

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }       
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)

