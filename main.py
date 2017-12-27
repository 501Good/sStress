# -*- coding: utf-8 -*-

import os
import re
import lstm.text_accentAPI as acc
import rules.rules_main as rules
from flask import Flask, render_template, request, redirect, \
    url_for, send_from_directory
from werkzeug.utils import secure_filename
from time import time
from lstm.tokenizer import tokenize

UPLOAD_FOLDER = os.getcwd() + '/uploads'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.secret_key = 'lolkekcheburek'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
accent = acc.AccentLSTM()
accent.initialize()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print(request.files)
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        print(file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filetext = open('uploads/' + filename, encoding='utf-8').read()
            accented_text = accent.put_stress(filetext, "'")
            newfilename = 'accented_' + str(time()).replace('.', '') + '.txt'
            with open('uploads/' + newfilename,
                      'w', encoding='utf-8') as accented_file:
                accented_file.write(accented_text)
            return redirect(url_for('uploaded_file',
                                    filename=newfilename))
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    text = request.get_data().decode('utf-8')
    text = text.replace("́", "")
    text = text.replace("'", "")
    accented_text = accent.put_stress(text, "́")
    new_accented_text = ""
    temp_accented_text = accented_text.replace("\n", "<br/>") + " "
    for i, char in enumerate(temp_accented_text):
        if i + 1 < len(temp_accented_text):
            if temp_accented_text[i + 1] in ["'", "́"]:
                new_accented_text += '<b><span style="background-color: ' + \
                    '#82E0AA">{}</span></b>'.format(char)
            elif char not in ["'", "́"]:
                new_accented_text += char
    return new_accented_text


@app.route('/predict_rules/', methods=['GET', 'POST'])
def predict_rules():
    text = request.get_data().decode('utf-8')
    text = text.replace("́", "")
    text = text.replace("'", "")
    accented_text, accented_tokens, biggest_suffixes, stress_types, poses = rules.initialize(text)
    for i in range(len(accented_tokens)):
        if "'" in accented_tokens[i]:
            new_word = ''
            for index, char in enumerate(accented_tokens[i]):
                if index + 1 < len(accented_tokens[i]):
                    if accented_tokens[i][index + 1] in ["'", "́"]:
                        new_word += '<b><span style="background-color: ' + \
                            '#82E0AA">{}</span></b>'.format(char)
                    elif char not in ["'", "́"]:
                        new_word += char
                else:
                    if char not in ["'", "́"]:
                        new_word += char

            if poses[i] == 'NOUN': formated_pos = 'существительное'
            if poses[i] == 'ADJF': formated_pos = 'прилагательное'
            if poses[i] == 'VERB': formated_pos = 'глагол'

            if stress_types[i] == 'suffix': formated_type = 'суффикс'
            if stress_types[i] == 'suffix 1': formated_type = 'первый слог суффикса'
            if stress_types[i] == 'suffix 2': formated_type = 'второй слог суффикса'
            if stress_types[i] == 'suffix 3': formated_type = 'третий слог суффикса'
            if stress_types[i] == 'presuffix': formated_type = 'предсуффиксальный слог'
            if stress_types[i] == 'first vowel': formated_type = 'первый слог'
            if stress_types[i] == 'prefix': formated_type = 'приставку'
            if stress_types[i] == 'root': formated_type = 'корень'
            if stress_types[i] == 'type B': formated_type = 'флексию'
            
            new_text = '<span title="Слово было распознано как {},'.format(formated_pos) + \
                                 'в котором лемма оканчивается на {}.\n'.format(biggest_suffixes[i]) + \
                                 'В таких случаях ударение всегда падает на {}.">'.format(formated_type) + \
                                 '{}</span>'.format(new_word)

            accented_text = re.sub(accented_tokens[i], new_text, accented_text, 1)
            
    return accented_text
    


@app.route('/testme/', methods=['GET', 'POST'])
def testme():
    text = request.get_data().decode('utf-8')
    orig_text = text
    text = text.replace("́", "")
    text = text.replace("'", "")
    accented_text = accent.put_stress(text, "'")
    orig_tokens = tokenize(orig_text)
    accented_tokens = tokenize(accented_text)
    assert len(orig_tokens) == len(accented_tokens)
    result = ""
    for i in range(len(orig_tokens)):
        if orig_tokens[i].find("'") == accented_tokens[i].find("'"):
            result += '<b><span style="background-color: ' + \
                '#82E0AA">{}</span></b>'.format(orig_tokens[i])
        else:
            result += '<b><span style="background-color: ' + \
                '#E74C3C"><a href="#" class="deco-none" ' + \
                'data-toogle="tooltip" title="Ваш вариант: {}">' + \
                '{}</a></span></b>'.format(orig_tokens[i], accented_tokens[i])
    return result


if __name__ == '__main__':
    app.run(port=5000, debug=True)
