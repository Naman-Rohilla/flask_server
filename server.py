from flask import Flask, make_response, request, jsonify, send_file
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# import pprint
import openai
import os
import fitz
import io
import google.generativeai as palm
from flask_cors import CORS
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



# Replace the placeholder with your Atlas connection string
uri = "mongodb+srv://flask_app_user:owIucyK1X0hFTNtL@clusterflask.thetpql.mongodb.net/?retryWrites=true&w=majority"
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update the path accordingly
# openai.api_key  = os.getenv("openAI")
# 

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))



db = client.myDatabase

app = Flask(__name__, static_folder='static')

CORS(app,  resources={r"/api/*": {"origins": "https://chatbot-theta-three.vercel.app"}})

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


palm.configure(api_key=os.getenv("palmAI"))

@app.route('/check', methods = ['POST', 'GET', 'OPTIONS'])
def hello_dev():
    print("hello world")

    return "hello world"



@app.route('/', methods = ['POST', 'GET', 'OPTIONS'])
def hello_world():
    # db.temp.insert_one({
    #     "a" : 1,
    # })
    try: 
        print("a")    
        data = request.args.get('param1')
        print(data)
        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        model = models[0].name
        print(model)
        prompt = """
          You are an expert at solving word problems.

          Solve the following problem:

          I have three houses, each with three cats.
          each cat owns 4 mittens, and a hat. Each mitten was
          knit from 7m of yarn, each hat from 4m.
          How much yarn was needed to make all the items?

          Think about it step by step, and show your work.
        """

        completion = palm.generate_text(
          model=model,
          prompt=data,
          temperature=0,
          # The maximum length of the response
          max_output_tokens=1000,
        )

        print(completion)
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://chatbot-theta-three.vercel.app")
        response.data = completion.result if completion.result != None else "please try again"

        return response
    except Exception as e:
        error_message = "Naman An error occurred: " + str(e)
        response = make_response(error_message, 500)  # Respond with a 500 Internal Server Error
        return response

@app.route('/g')
def hello_world_2():
    x = input("What you want?")
    print(x)
    return 'Hello gg!'


@app.route('/process_pdf_chatbot', methods=['POST', 'GET', 'OPTIONS'])
def process_pdf_chatbot():
    pdf_file = request.files['pdf_file']

    print(pdf_file);
    if pdf_file:
        ocr_text = extract_ocr_text_from_pdf_chatbot(pdf_file)
        temp_text = ocr_text if len(ocr_text) < 7799 else ocr_text[0:7799]

        data = "use this data as refernce: " + temp_text + "write 5 important points of the data"

        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        model = models[0].name
        print(model)
        completion = palm.generate_text(
           model=model,
           prompt=data,
           temperature=0,
           # The maximum length of the response
           max_output_tokens=1000,
        )

        print(completion)

        content = "use this data as refernce: " + temp_text + "$*breakforresult" + completion.result

        print("completed")
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://chatbot-theta-three.vercel.app")
        response.data = content if completion.result != None else "please try again"
        response.ocr = data
        return response
    else:
        return jsonify({"error": "No PDF file provided"})

def extract_ocr_text_from_pdf_chatbot(pdf_file):
    ocr_text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            # print(image_data)
            img = Image.open(io.BytesIO(image_data))
            ocr_text += f"OCR Result for Image {img_index + 1}:\n"
            ocr_text += pytesseract.image_to_string(img)
            ocr_text += "\n"

    return ocr_text


@app.route('/process_pdf', methods=['POST', 'GET', 'OPTIONS'])
def process_pdf():
    print("entered1")
    pdf_file = request.files['pdf_file']

    print(pdf_file);
    if pdf_file:
        print("entered2")
        ocr_text = extract_ocr_text_from_pdf(pdf_file)
        
        print("completed")
        # print(new_pdf_path)
        # send_file(new_pdf_path, as_attachment=True)
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://chatbot-theta-three.vercel.app")
        response.data = ocr_text if len(ocr_text) > 0 else "please try again"
        return response
    else:
        return jsonify({"error": "No PDF file provided"})

def extract_ocr_text_from_pdf(pdf_file):
    print("entered3")
    ocr_text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    print("entered4")
    for page in doc:
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            # print(image_data)
            img = Image.open(io.BytesIO(image_data))
            ocr_text += f"OCR Result for Image {img_index + 1}:\n"
            ocr_text += pytesseract.image_to_string(img)
            ocr_text += "\n"

    return ocr_text



if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)