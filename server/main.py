from flask import Flask, request, send_file
from tts import generate
from phrasesplit import split
from wikisentences import generate_sentences
import pronouncing
import pydub
from ngrams import LModel
import random

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

templates = []
with open('caption-templates.txt', 'r') as f:
    for line in f:
        templates.append(line.strip())

model = LModel().ngrams('rapdata/hip_hop.txt', 3) # or substitute in 4 for 4-grams, etc.
print("Done ngrams")

def last(words):
    if len(words) == 1:
        return words[0]

    if words[-1].upper() == words[-1].lower():
        return last(words[:-1])

    return ''.join(filter(lambda x: x.isalpha(), words[-1]))

@app.route('/generate_rap', methods=['GET'])
def generate_rap():
    caption = request.args.get('caption')
    sentences = generate_sentences(request.args.get("tags").split(',')) #only one sentence

    A = [ (random.choice(templates).replace('_', caption) + '. ').split(' ') ]
    for i,sent  in enumerate(sentences[:14]):
        print('iu4ry', last(sent))
        rhymes = pronouncing.rhymes(last(sent))
        rhyming = random.choice(rhymes) if len(rhymes) > 0 else 'END' #last word
        C  = model.rspin(rhyming)

        A.append(sent)
        A.append(C)

    print("A", A)

    result = []
    for sent in A:
        phrases = split(sent)
        if phrases is None:
            continue
        result.extend(phrases)

    print("result", result)



    # for sentence in sentences[0]:
    #     last_word = sentence.strip('.').split(' ')[-1]
    #     print(sentence.strip('.'), model.rspin(last_word))


    path_to_file = generate(['Yo this is Lil Wiki']+result)

    return send_file(
        path_to_file,
        mimetype="audio/mp3",
        as_attachment=False,
        attachment_filename="audio.mp3"
    )

if __name__ == '__main__':
    # pass
  app.run()
