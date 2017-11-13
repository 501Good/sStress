from keras.models import model_from_json
import tensorflow as tf
import numpy as np
import re
from tokenizer import tokenize

VOWELS = 'аеиоуэюяыё'
REG = '[{}].*[{}]'.format(VOWELS, VOWELS)
MAXLEN = 40
CHARS = ["'", '-', '_', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к',
        'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', 'ё']
CHAR_INDICES = dict((c, i) for i, c in enumerate(CHARS))
MODEL_FILE = "text_model.json"
WEIGHTS_FILE = "on-texts-weights-improvement-09-0.96.hdf5"


class AccentLSTM(object):


    def __init__(self):
        self.model_file = MODEL_FILE
        self.weights_file = WEIGHTS_FILE


    def initialize(self):
        with open(self.model_file, 'r') as content_file:
            json_string = content_file.read()
        self.model = model_from_json(json_string)
        self.model.load_weights(self.weights_file)
        self.graph = tf.get_default_graph()
        
        
    def __parse_the_phrase(self, text):
        text = text.replace("c", "с")  # latinic to cyrillic
        regex1 = "[…:,.?!\n]"
        text = re.sub(regex1, " _ ", text).lower()  # mark beginning of clause
        regex2 = "[^а-яё'_ -]"  # get rid of "#%&""()*-[0-9][a-z];=>@[\\]^_{|}\xa0'
        text = re.sub(regex2, "", text)
        words = text.split(' ')
        return words


    def __add_endings(self, wordlist):
        pluswords = []
        for i,word in enumerate(wordlist):
            if not bool(re.search(REG, word)):
                pluswords.append(word) # won't predict, just return (less then two syllables )
            elif i == 0 or wordlist[i-1] == '_':
                pluswords.append('_' + word)
            else:
                context = wordlist[i-1].replace("'", "")
                if len(context)<3:
                    ending = context
                else:
                    ending = context[-3:]
                plusword = ending + '_' + word
                pluswords.append(plusword)
        return pluswords


    def __predict(self, word):
        x = np.zeros((1, MAXLEN, len(CHAR_INDICES)), dtype=np.bool)
        #print(word)
        for index, letter in enumerate(word):
            pos = MAXLEN - len(word.replace("'", "")) + index
            x[0, pos, CHAR_INDICES[letter]] = 1
        #print(x)
        preds = self.model.predict(x, verbose=0)[0]
        preds = preds.tolist()
        max_value = max(preds)
        index = preds.index(max_value)
        #cut left context "ные_мечты" -> "мечты"
        word = word[word.index('_')+1:]
        index = len(word) - MAXLEN + index
        #print(preds)
        #print('max_value in preds is %s with index %s' % (max_value, index))
        if index > len(word)-1:
            print('no %s-th letter in %s' % (index+1,word))
        else:
            acc_word = word[:index+1]+'\''+ word[index+1:]
            return(acc_word)


    def put_stress(self, text, stress_symbol="'"):
        """This function gets any string as an input and returns the same string
        but only with the predicted stress marks.
        
        All the formating is preserved using this function. 
        """
        with self.graph.as_default():
            words = self.__parse_the_phrase(text)
            tokens = tokenize(text)
            accented_phrase = []
            pluswords = self.__add_endings(words)

            for w in pluswords:
                if not bool(re.search(REG, w)):
                    pass
                else:
                    accented_phrase.append(self.__predict(w))
            final = []
            
            for token in tokens:
                try:
                    temp = accented_phrase[0].replace("'", '')
                except IndexError:
                    temp = ''
                if temp == token.lower():
                    stress_position = accented_phrase[0].find("'")
                    final.append(token[:stress_position] + stress_symbol + token[stress_position:])
                    accented_phrase = accented_phrase[1:]
                else:
                    final.append(token)
            final = ''.join(final)
            return final