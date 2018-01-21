import requests
import re
import nltk
from urllib import parse
import string

printable = set(string.printable)

def extract_wiki(word):

    """
    Extracts a Wikipedia article corresponding to a word
    :param word: str
    :return: str
    """

    url = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles=" + \
          parse.quote(word)

    r = requests.get(url)
    pages = r.json()["query"]["pages"]

    for id in pages:
        content = pages[id]
        if "extract" in content:
            if re.search("may refer to:</p>", content["extract"]) is None and len(content["extract"]) > 0:
                return content["extract"]
            else:

                # 2nd request for words with redirects/disambiguation
                url2 = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=" + \
                       parse.quote(word)
                r2 = requests.get(url2)
                pages2 = r2.json()["query"]["pages"]

                for id in pages2:

                    content = pages2[id]

                    if "revisions" in content:

                        search_title = content["revisions"][0]["*"]

                        m_disamb = re.search("may refer to",  search_title)
                        if m_disamb is not None:
                            search_title = content["revisions"][0]["*"][m_disamb.end():]

                        m_open = re.search("\[\[",  search_title)
                        m_close = re.search("\]\]", search_title)

                        title = search_title[m_open.end():m_close.start()]

                        # 3rd request for words with redirects / disambiguation
                        url3 = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles=" + \
                               parse.quote(title)

                        r3 = requests.get(url3)
                        pages3 = r3.json()["query"]["pages"]

                        for id in pages3:
                            content = pages3[id]
                            if "extract" in content:
                                return content["extract"]



def filter_sentences(article, word, wnl):

    """
    Cleans and filters appropriate sentences
    :param article: str
    :param word: str
    :param wnl: nltk.stem stemmer
    :return:
    """

    clean_text = re.sub("<[^>]+>", "", article)
    clean_text = ''.join( b for b in clean_text if b in printable ) \
        .replace('\n', ' ')
    all_sentences = nltk.sent_tokenize(clean_text)

    filtered_sentences = []

    for s in all_sentences:
        words = [w.lower() for w in nltk.word_tokenize(s)]
        lemmas = [wnl.lemmatize(w) for w in words]
        if len(lemmas) > 2 and len(lemmas) and wnl.lemmatize(word.lower()) in lemmas:
            filtered_sentences.append(words)

    return filtered_sentences

wnl = nltk.stem.WordNetLemmatizer()
def generate_sentences(tags):

    for w in tags:
        if w not in generate_sentences.used:
            try:
                html = extract_wiki(w)
            except:
                continue
            if html is not None:
                generate_sentences.used.append(w)
                return filter_sentences(html, w, wnl)
    for w in tags:
        try:
            html = extract_wiki(w)
        except:
            continue
        if html is not None:
            generate_sentences.used.append(w)
            return filter_sentences(html, w, wnl)

    return generate_sentences(["nothing"])

generate_sentences.used = []
