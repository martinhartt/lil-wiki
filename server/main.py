from flask import Flask, request, send_file
from tts import generate
from phrasesplit import split
from wikisentences import generate_sentences
from ngrams import LModel
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

model = LModel().ngrams('rapdata/hip_hop.txt', 3) # or substitute in 4 for 4-grams, etc.
print("Done ngrams")

@app.route('/generate_rap', methods=['GET'])
def generate_rap():
    sentences = generate_sentences(request.args.get("tags").split(','))


    print(model.rspin("house"))
    # for sentence in sentences[0]:
    #     last_word = sentence.strip('.').split(' ')[-1]
    #     print(sentence.strip('.'), model.rspin(last_word))

    phrases = split(['ok'])

    path_to_file = generate(["Testing testing"])

    return send_file(
        path_to_file,
        mimetype="audio/mp3",
        as_attachment=False,
        attachment_filename="audio.mp3"
    )

if __name__ == '__main__':
  app.run()
