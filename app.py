from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
from gtts import gTTS
import os, io, sys
import numpy as np
import cv2
import base64
import time

from yolo_detection import run_model
from language_conversion import convert_lang

app = Flask(__name__)


############################################## THE REAL DEAL STARTS HERE ###############################################
@app.route('/detectObject', methods=['POST'])
def mask_image():
    # print(request.files , file=sys.stderr)
    #################################################
    file = request.files['image'].read() ## byte file
    # npimg = np.fromstring(file, np.uint8)
    npimg = np.frombuffer(file,np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)[:, :, ::-1]
    # OpenCV image (BGR to RGB)
    
    ################################################
    # cv2.imshow('After reading from request', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    ################################################
    ################################################
    ######### Do preprocessing here ################
    # img[img > 150] = 0
    ## any random stuff do here
    ################################################


    img,text = run_model(img)
    print("{} This is from app.py".format(text))
    if(len(text) == 0):
        text = "Reload the page and try with another better image"
    tts_english = gTTS(text, lang="en", tld="com")
    # ask user the lang
    # call to google Translate api to convert text in english to text in given lang
    # save the file in recording using gTTS with lang parameter as given lang
    tts_english.save('static/' + "detected_image_english.mp3")
    text = convert_lang(text)
    tts_hindi = gTTS(text,lang="hi",tld="com")
    tts_hindi.save('static/' + "detected_image_hindi.mp3")

    """
    rawBytes = io.BytesIO()
    img = Image.fromarray(img.astype("uint8"))
    img.save(rawBytes,"JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return jsonify({'status':str(img_base64)})
    """
    bufferedBytes = io.BytesIO()
    img_base64 = Image.fromarray(img)
    img_base64.save(bufferedBytes, format="JPEG")
    img_base64 = base64.b64encode(bufferedBytes.getvalue())
    return jsonify({'status':str(img_base64)})

################################## THE MAIN PART IS DONE ABOVE #########################################################


@app.route('/test', methods=['GET', 'POST'])
def test():
	print("log: got at test", file=sys.stderr)
	return jsonify({'status': 'succces'}) 


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/audioFile')
def getAudio():
    newAudioFileEnglish = "detected_image_english.mp3"
    newAudioFileHindi = "detected_image_hindi.mp3"
    return render_template('play.html',audioFileEnglish = newAudioFileEnglish, audioFileHindi=newAudioFileHindi)

@app.after_request
def after_request(response):
    print("log: setting cors", file=sys.stderr)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
	app.run(debug=True)
