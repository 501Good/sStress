import re, os, nltk, pymorphy2, sys
from suffix_trees.STree import STree

BASE_DIR = os.path.dirname(__file__)


def make_rules(folder):
    rules_dictionary = {}
    try:
        path = os.path.join(os.getcwd(), 'rules', 'data', folder)
        path = os.path.join(BASE_DIR, path)
        files = os.listdir(path)
    except:
        path = os.path.join(os.getcwd(), 'data', folder)
        path = os.path.join(BASE_DIR, path)
        files = os.listdir(path)
    short_files_rule = re.compile('.txt')
    for file in files:
        if short_files_rule.search(file) != None:
            class_name = re.sub('_', ' ', re.sub('\.txt', '', file))
            current_file = open(os.path.join(path, file), 'r', encoding='utf-8').read()
            affixes = current_file.split(', ')
            rules_dictionary[class_name] = affixes
    return(rules_dictionary)


def find_affixes(rules_noun, lemma, word_possible_stress):
    for stress_type, affixes in rules_noun.items():
        for affix in affixes:
            affix_type = ''
            if re.search('^[а-яё]+\-$', affix) != None:
                regexp = '^'+affix[:-1]
                affix_type = 'preffix'
            elif re.search('^\-[а-яё]+$', affix) != None:
                regexp = affix[1:]+'$'
                affix_type = 'suffix'
            elif re.search('^[а-яё]+\-\.\.\.\-[а-яё]+$', affix) != None:
                regexp = '^'+re.sub('\-\.\.\.\-', '.+', affix)+'$'
                affix_type = 'combination'

            if re.search(regexp, lemma) != None:
                if stress_type in word_possible_stress:
                    word_possible_stress[stress_type].append((affix, affix_type))
                else:
                    word_possible_stress[stress_type] = [(affix, affix_type)]
    return(word_possible_stress)


def find_biggest_affixes(word_possible_stress):
    biggest_len_suffix, biggest_len_prefix = 0, 0
    biggest_suffix, biggest_prefix = '', ''
    if 'all suffixes' in word_possible_stress:
        for suffix in word_possible_stress['all suffixes']:
            if len(suffix[0]) > biggest_len_suffix:
                biggest_suffix = suffix[0]
                biggest_len_suffix = len(suffix[0])
        del word_possible_stress['all suffixes']
        
    if 'all prefixes' in word_possible_stress:
        for prefix in word_possible_stress['all prefixes']:
            if len(prefix[0]) > biggest_len_prefix:
                biggest_prefix = prefix[0]
                biggest_len_prefix = len(prefix[0])
        del word_possible_stress['all prefixes']
    return(biggest_prefix, biggest_suffix, word_possible_stress)


def find_possible_types(word_possible_stress, biggest_suffix, biggest_prefix):
    possible_types = []
    for stress_type, affixes in word_possible_stress.items():
        for affix in affixes:
            if affix[1] == 'suffix':
                if affix[0] == biggest_suffix:
                    possible_types.append(stress_type)
            elif affix[1] == 'prefix':
                if affix[0] == biggest_prefix:
                    possible_types.append(stress_type)
            elif affix[1] == 'combination':
                possible_types = []
                pair = affix[0].split('...')
                if pair[0] == biggest_prefix and pair[1] == biggest_suffix:
                    possible_types.append(stress_type)
    return(possible_types)


def make_stressed_word(possible_types, token, lemma, biggest_suffix, original_token):                        
    if possible_types[0] == 'prefix' or possible_types[0] == 'first vowel':
        stressed_word = re.sub('^([^уеыаоэяиюёУЕЫАОЭЯИЮЁ]*[уеыаоэяиюёУЕЫАОЭЯИЮЁ])', '\g<1>\'', token)
        #print(token, stressed_word, lemma, biggest_prefix, biggest_suffix)
    elif possible_types[0] == 'suffix' or possible_types[0] == 'suffix 1':
        stem = STree([token, lemma]).lcs()
        stem_cutted = re.sub(re.sub('-', '', biggest_suffix)+'$', '', stem)
        for num in range(1,5):
            if stem == stem_cutted:
                stem_cutted = re.sub(re.sub('-', '', biggest_suffix)[:-num]+'$', '', stem)
        stressed_word = re.sub('^('+stem_cutted+'[^уеыаоэяиюёУЕЫАОЭЯИЮЁ]*[уеыаоэяиюёУЕЫАОЭЯИЮЁ])', '\g<1>\'', token)
    elif possible_types[0] == 'suffix 2':
        stem = STree([token, lemma]).lcs()
        stem_cutted = re.sub(re.sub('-', '', biggest_suffix)+'$', '', stem)
        for num in range(1,5):
            if stem == stem_cutted:
                stem_cutted = re.sub(re.sub('-', '', biggest_suffix)[:-num]+'$', '', stem)
        stressed_word = re.sub('^('+stem_cutted+'([^уеыаоэяиюёУЕЫАОЭЯИЮЁ]*[уеыаоэяиюёУЕЫАОЭЯИЮЁ]){2})', '\g<1>\'', token)

    elif possible_types[0] == 'suffix 3':
        stem = STree([token, lemma]).lcs()
        stem_cutted = re.sub(re.sub('-', '', biggest_suffix)+'$', '', stem)
        for num in range(1,5):
            if stem == stem_cutted:
                stem_cutted = re.sub(re.sub('-', '', biggest_suffix)[:-num]+'$', '', stem)
        stressed_word = re.sub('^('+stem_cutted+'([^уеыаоэяиюёУЕЫАОЭЯИЮЁ]*[уеыаоэяиюёУЕЫАОЭЯИЮЁ]){3})', '\g<1>\'', token)
    
    elif possible_types[0] == 'presuffix':
        stem = STree([token, lemma]).lcs()
        stem_cutted = re.sub(re.sub('-', '', biggest_suffix)+'$', '', stem)
        for num in range(1,5):
            if stem == stem_cutted:
                stem_cutted = re.sub(re.sub('-', '', biggest_suffix)[:-num]+'$', '', stem)
        suffixes = re.sub(stem_cutted, '', stem)
        stressed_word = re.sub('([уеыаоэяиюёУЕЫАОЭЯИЮЁ])([^уеыаоэяиюёУЕЫАОЭЯИЮЁ]*'+suffixes+'.{,5})$', '\g<1>\'\g<2>', token)
    elif possible_types[0] == 'type B':
        stressed_word = re.sub('^(.+[уеыаоэяиюё])([^уеыаоэяиюё]*)$', '\g<1>\'\g<2>', token)
    try:
        parts = stressed_word.split('\'')
        stressed_word = original_token[:len(parts[0])]+'\''+original_token[len(parts[0]):]
    except:
        stressed_word = original_token
    return(stressed_word)


def process_stresses(part_of_speech, rules, pos, lemma, token, original_token, word_possible_stress, current_file):
    stressed_word, biggest_suffix, possible_types = '', '', ['']
    if part_of_speech in pos:
        word_possible_stress = find_affixes(rules, lemma, word_possible_stress)

        if word_possible_stress != {} and list(word_possible_stress.keys()) != ['all prefixes', 'all suffixes'] and \
           list(word_possible_stress.keys()) != ['all suffixes'] and list(word_possible_stress.keys()) != ['all prefixes']:

            biggest_prefix, biggest_suffix, word_possible_stress = find_biggest_affixes(word_possible_stress)
            possible_types = find_possible_types(word_possible_stress, biggest_suffix, biggest_prefix)
            if len(possible_types) == 1:
                stressed_word = make_stressed_word(possible_types, token, lemma, biggest_suffix, original_token)
                current_file = re.sub(original_token, stressed_word, current_file)
##                if pos == 'VERB':
##                    print(pos, lemma, token, stressed_word, biggest_suffix, possible_types[0])
    if possible_types == []: possible_types = ['']
    return(current_file, stressed_word, biggest_suffix, possible_types[0])


def initialize(current_file):
    morph = pymorphy2.MorphAnalyzer()
    rules_noun = make_rules('NOUN')
    rules_adj = make_rules('ADJ')
    rules_verb = make_rules('VERB')
    all_tokens = nltk.word_tokenize(current_file)
    stressed_words, biggest_suffixes, stress_types, poses = [], [], [], []
    for token in all_tokens:
        stressed_word, biggest_suffix, stress_type, pos = token, '', '', ''
        original_token = token
        token = token.lower()
        word_possible_stress = {}
        if re.search('^[А-ЯЁа-яё\-]+$', token) != None and token != '-':
            token = re.sub('^-', '', token)
            pos = morph.parse(token)[0].tag.POS
            # pos = nltk.pos_tag(token, lang='rus')
            lemma = morph.parse(token)[0].normal_form
            if pos != None:
                current_file, stressed_word, biggest_suffix, stress_type = process_stresses('NOUN', rules_noun, pos, lemma, token, original_token, word_possible_stress, current_file)
                if biggest_suffix == '':
                    current_file,stressed_word, biggest_suffix, stress_type = process_stresses('ADJF', rules_adj, pos, lemma, token, original_token, word_possible_stress, current_file)
                    if biggest_suffix == '':
                        current_file, stressed_word, biggest_suffix, stress_type = process_stresses('VERB', rules_verb, pos, lemma, token, original_token, word_possible_stress, current_file)
        if stressed_word == '':
            stressed_word = original_token
        stressed_words.append(stressed_word)
        biggest_suffixes.append(biggest_suffix)
        stress_types.append(stress_type)
        poses.append(pos)
    return(current_file, stressed_words, biggest_suffixes, stress_types, poses)
