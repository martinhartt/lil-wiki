from flask import Flask, request, send_file
from tts import generate
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/generate_rap', methods=['GET'])
def generate_rap():
     path_to_file = generate("Testing testing")

     return send_file(
         path_to_file,
         mimetype="audio/mp3",
         as_attachment=False,
         attachment_filename="audio.mp3"
     )

if __name__ == '__main__':
  app.run()
