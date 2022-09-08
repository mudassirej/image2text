#!/usr/bin/python
from flask import Flask, render_template, request
import os
from flask import send_file
import pandas as pd
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
app = Flask(__name__)

stability_api = client.StabilityInference(
key='sk-x1yjGm2IjpbimGZDcgACLgbyPLjeAF991qFfc6jVXL9LA9MK', 
verbose=True,
)




@app.route("/")
def index():
	return render_template('index.html')
@app.route("/image-text", methods=['GET'])
def image_text():
    if request.method == "GET":
        text = request.args.get("text")
    print("text is: ",text)
    print(os.listdir(os.curdir))
    df = pd.read_csv("static/text.csv")
    df1 = pd.DataFrame(columns=['text'])
    df1.text = [text]
    df = df.append(df1,ignore_index=True)
    print(df1)
    print(df)
    df.to_csv("static/text.csv",index=False)

    return render_template('loading.html')

@app.route("/processing")
def processing():
    df = pd.read_csv("static/text.csv")
    text = df.text.tolist()[-1]

    print("text is: ",text)
    # the object returned is a python generator
    answers = stability_api.generate(
        prompt=text
    )

    # iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img = img.save(f"static/{text}.jpg")

    return render_template('download.html',message = text, s3_file = f'static/{text}.jpg')


@app.route('/download')
def downloadFile ():
    df = pd.read_csv("static/text.csv")
    text = df.text.tolist()[-1]
    path = f"static/{text}.jpg"
    return send_file(path, as_attachment=True)

