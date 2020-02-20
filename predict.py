from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for
from io import BytesIO
import numpy as np
from PIL import Image
from flask import make_response
from flask import Flask
from skimage import io
import sys, os, json, time

start = time.time()
from keras.models import model_from_json
print("import keras time = ", time.time()-start)

TEMPLATE = open('./index.html').read()

ALLOWED_EXTENSIONS = set(['jpg'])
app = Flask(__name__)

base_path = ''

model = None
# Getting model
model_path = os.environ.get("model_path")
with open(model_path + '/model.json', 'r') as f:
    model_content = f.read()
    model = model_from_json(model_content)
    # Getting weights
    model.load_weights(model_path + "/weights.h5")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        # check if the post request has the file part
        if 'file' not in request.files:
            return TEMPLATE.replace('{fc-result}', "no picture, please upload")
        file = request.files['file']
        if not file:
            return TEMPLATE.replace('{fc-result}', "no picture, please upload")
        content = file.stream.read()
        environ = request.environ
        tp = TEMPLATE
        if allowed_file(file.filename):
            return tp.replace('{fc-result}', predict(content, environ.get('fc.context')))
        else:
            return tp.replace('{fc-result}', "picture format must be jpg")
    
    return TEMPLATE.replace('{fc-result}', "?")

def predict(event, context):
    start = time.time()
    img_size = 64

    img_buffer = np.asarray(bytearray(event), dtype='uint8')
    img = io.imread(BytesIO(img_buffer))
    img = np.array(Image.fromarray(img).resize((img_size, img_size)))
    X = np.zeros((1, 64, 64, 3), dtype='float64')
    X[0] = img

    global model
    Y = model.predict(X)
    result = "dog: {:.2}, cat: {:.2}; ".format(Y[0][1], Y[0][0])
    Y = np.argmax(Y, axis=1)
    Y = 'cat' if Y[0] == 0 else 'dog'
    print("predict time = {}".format(time.time()-start))
    return result + '\nIt is a ' + Y + ' !'

def handler(environ, start_response):
    # 如果没有使用自定义域名
    if environ['fc.request_uri'].startswith("/2016-08-15/proxy"):
        from urllib.parse import urlparse
        parsed_tuple = urlparse(environ['fc.request_uri'])
        li = parsed_tuple.path.split('/')
        global base_path
        if not base_path:
            base_path = "/".join(li[0:5])

        context = environ['fc.context']
        environ['HTTP_HOST'] = '{}.{}.fc.aliyuncs.com'.format(
            context.account_id, context.region)
        environ['SCRIPT_NAME'] = base_path + '/'

    return app(environ, start_response)

def initializer(context):
    print("just imexitport keras")

if __name__ == '__main__':
    img_path = sys.argv[1]
    with open(img_path,  "rb") as f:
        print(predict(f.read(), ""))

# if __name__ == '__main__':
#     app.run()