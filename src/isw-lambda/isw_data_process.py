from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import numpy as np
import string
from num2words import num2words
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import os
import pickle 

def remove_preface(text: str):
    # first two lines of text are list of authors and date 
    # they are of no use for prediction
    return '\n'.join(text.split('\n')[2:])

def remove_one_letter_words(text):
    words = word_tokenize(text)
    words = filter(lambda w: len(w) > 1, words)
    return ' '.join(words)

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    stop_words = stop_words - {'no', 'not'}
    
    words = word_tokenize(text)
    words = filter(lambda w: w not in stop_words, words)
    return ' '.join(words)

def remove_links(text):
    reg =  re.compile(r'^http[s]?://.*[\r\n]*')

    words = word_tokenize(text)
    words = filter(lambda w: not reg.fullmatch(w), words)
    return ' '.join(words)

def nums_to_words(text):
    def num_to_word(word):
        return '' if int(word) < 1000000000000 else num2words(word) 
    
    words = word_tokenize(text)
    words = map(lambda w: num_to_word(w) if w.isdigit() else w, words)

    return ' '.join(words)

def to_lower(text):
    return ''.join(np.char.lower(text).tolist())

def remove_apostrophe(text):
    return ''.join(filter(lambda ch: ch != '\'', text))

def remove_punctuation(text):
    return ''.join(filter(lambda ch: ch not in string.punctuation, text))

def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    words = map(lemmatizer.lemmatize, words)

    return ' '.join(words)

def preprocess(text):
    text = remove_preface(text)
    text = remove_punctuation(text)
    text = remove_apostrophe(text)
    text = remove_one_letter_words(text)
    text = remove_links(text)
    text = to_lower(text)
    text = remove_stopwords(text)
    text = nums_to_words(text)

    text = lemmatize(text)

    text = remove_punctuation(text)
    text = remove_stopwords(text)
    return text

if __name__ == "__main__":
    raw_txt_dir = 'isw_data_raw_text'
    preprocessed_dir = 'isw_data_preprocessed'

    for filename in os.listdir(raw_txt_dir):
        f = os.path.join(raw_txt_dir, filename)
        fres = os.path.join(preprocessed_dir, filename)
        with open(f, encoding = 'UTF-8') as fr:
            preprocessed = preprocess(fr.read())
        with open(fres, 'w', encoding = 'UTF-8', ) as fw:
            fw.write(preprocessed)

    preprocessed_texts = []
    for filename in os.listdir(preprocessed_dir):
        f = os.path.join(preprocessed_dir, filename)
        with open(f, encoding = 'UTF-8') as fr:
            preprocessed_texts.append(fr.read())

    cv = CountVectorizer()
    word_count_v = cv.fit_transform(preprocessed_texts)
    with open('CountVectorizer.pkl', 'wb') as handle:
        pickle.dump(cv, handle)
    tf_idf_transformer = TfidfTransformer()
    tf_idf_transformer.fit(word_count_v)
    with open('TfidfTransformer.pkl', 'wb') as handle:
        pickle.dump(tf_idf_transformer, handle)
    