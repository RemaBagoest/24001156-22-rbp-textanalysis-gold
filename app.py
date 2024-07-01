import re
import pandas as pd
from flask import Flask, jsonify, request, send_file
import io
#Defining app
app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder = LazyJSONEncoder

#Defining Swagger Template 
swagger_template = {
    "info": {
        "title": "API for Cleaning Tweet Data in Indonesia",
        "version": "1.0.0",
        "description": "Cleaning text data its contain abusive text by Rema Bagos Pudyastowo",
        "description": "by Rema Bagos Pudyastowo | e-mail :Remabagospudyastowo@gmail.com",
    },
    "host": "127.0.0.1:5000"
}

#Defining Swagger Configuration
swagger_config = {
	"headers" : [],
	"specs" : [
		{
			"endpoint" : 'docs',
			"route" : '/docs.json'
		}
	],
	"static_url_path" : '/flasgger_static',
	"swagger_ui" : True,
	"specs_route" : "/docs/"
}

swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


# defining additional data for cleaning dictionary purpose
kamusalay = pd.read_csv('data/new_kamusalay.csv', encoding='latin-1', header=None)
abusive_dict = pd.read_csv('data/abusive.csv', encoding='latin-1', header=None)
kamusalay = kamusalay.rename(columns={0: 'original', 1: 'replacement'})

#redefine column on abusive_dict
abusive_dict = abusive_dict.rename(columns={0: 'abusive'})

# define function for text cleaning
def lowercase(text):
    return text.lower()

#removing unnecessary char 
def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Remove every '\n'
    text = re.sub('rt',' ',text) # Remove every retweet symbol
    text = re.sub('user',' ',text) # Remove every username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Remove every URL
    pattern = re.compile(r'\\x[0-9A-Fa-f]{2}')
    # Use the compiled pattern to replace matches in the text
    text = pattern.sub(' ', text)
    #text = re.sub((r'\\x[0-9A-Fa-f]{2}'),' ', text) #remove emoji 
    text = re.sub('  +', ' ', text) # Remove extra spaces 
    return text
      
#remove nonalphanumeric
def remove_nonaplhanumeric(text):
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

kamusalay_map = dict(zip(kamusalay['original'], kamusalay['replacement']))
def normalize_alay(text):
    return ' '.join([kamusalay_map[word] if word in kamusalay_map else word for word in text.split(' ')])

# remove abusive text
def remove_abusive(text):
    text = ' '.join(['' if word in abusive_dict.abusive.values else word for word in text.split(' ')])
    text = re.sub('  +', ' ', text) # Remove extra spaces
    text = text.strip()
    return text
    
#library python for data processing
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# stemming function
def stemming(text):
    return stemmer.stem(text)

# Defining preprocess function
def preprocess(text):
    text = lowercase(text) # 1
    text = remove_nonaplhanumeric(text) # 2
    text = remove_unnecessary_char(text) # 2
    text = normalize_alay(text) # 3
    text = stemming(text) # 4
    text = remove_abusive(text) # 5
    return text
# code 
@swag_from("D:/Rema Workspace/portofolio_data/binar_challenge/docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "WELCOME TO API FOR CLEANING TEXT DATA!!",
        'data': "To continue please access the '/text-processing' endpoint for data cleaning via form, '/text-processing-file' for data cleaning via file upload or '/docs' to see all available menus.",
    }

    response_data = jsonify(json_response)
    return response_data


@swag_from("D:/Rema Workspace/portofolio_data/binar_challenge/docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    text = request.form.get('text')
    cleaned_text_form = preprocess(text)

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text_form,
    }

    response_data = jsonify(json_response)
    return response_data

@app.route('/text-processing-file', methods=['POST'])
@swag_from("D:/Rema Workspace/portofolio_data/binar_challenge/docs/text_processing_file.yml", methods=['POST'])
def text_processing_file():
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file, encoding = 'latin-1')

    # Ambil teks yang akan diproses dalam format list
    texts = df['Tweet'].to_list()

    cleaned_text = [preprocess(text) for text in texts]
    # Create a new DataFrame with cleaned text
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text,
    }
    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run()