import os
from werkzeug.urls import url_quote
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    # قراءة المنفذ من Koyeb أو استخدام 8000 كافتراضي
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)