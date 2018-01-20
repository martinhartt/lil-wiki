import requests
import re
import nltk
from urllib import parse

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
    all_sentences = nltk.sent_tokenize(clean_text)

    filtered_sentences = []

    for s in all_sentences:
        words = [wnl.lemmatize(w.lower()) for w in nltk.word_tokenize(s)]
        if len(words) > 2 and len(words) < 20 and wnl.lemmatize(word.lower()) in words:
            filtered_sentences.append(s)

    return filtered_sentences

if __name__ == "__main__":
    wnl = nltk.stem.WordNetLemmatizer()
    sample_input = ["asdfasdfasdf", "table", "chair", "grass"]
    for w in sample_input:
        html = extract_wiki(w)
        if html is not None:
            print(filter_sentences(html, w, wnl))
