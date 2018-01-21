import pronouncing
import re

MIN_LENGTH = 4

def stress(sentence):

    """
    Returns stress pattern for a sentence
    :param sentence: list(str)
    :return: list(list(str))
    """

    stresses = []

    for word in sentence:

        phones = pronouncing.phones_for_word(word)
        homonyms = [pronouncing.stresses(p) for p in phones]
        homonyms_int = [int(p) for p in homonyms]

        if len(homonyms_int) == 0:
            homonyms = ['0']
            homonyms_int = [0]

        word_stress = homonyms[homonyms_int.index(min(homonyms_int))]

        stresses.append(word_stress)

    if stresses[0][0] == str(0):
        return None

    words = sentence[:]
    phrases = []
    current_phrase = []

    for word in sentence:

        # if re.search("[a-zA-Z0-9]", word) is None:
        #     continue

        current_phrase.append(word)

        if len("".join(stresses[:len(current_phrase)])) >= MIN_LENGTH:

            next_stresses = "".join(stresses[len(current_phrase):])

            if len(next_stresses) > 1 and next_stresses[0] == str(1) and \
                    re.search("[a-zA-Z]", words[len(current_phrase)]):

                phrases.append(current_phrase)
                words = words[len(current_phrase):]
                stresses = stresses[len(current_phrase):]
                current_phrase = []

    if len(current_phrase) > 0:
        phrases.append(current_phrase)

    return([" ".join(p) for p in phrases])

if __name__ == "__main__":
    sentence = ['tennis', 'in', 'tennis', ',', 'grass', 'is', 'grown', 'on', 'very', 'hard-packed', 'soil', ',', 'and', 'the', 'bounce', 'of', 'a', 'tennis', 'ball', 'may', 'vary', 'depending', 'on', 'the', 'grass', "'s", 'health', ',', 'how', 'recently', 'it', 'has', 'been', 'mowed', ',', 'and', 'the', 'wear', 'and', 'tear', 'of', 'recent', 'play', '.']
    print(stress(sentence))