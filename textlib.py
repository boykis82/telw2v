import konlpy
import eunjeon
from konlpy.tag import Okt
from konlpy.tag import Kkma
from konlpy.tag import Komoran
from eunjeon import Mecab
import regex
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# 문서를 문장으로 분리
def sentence_segment(text):
    return [w.strip() for w in regex.split("([.?!])?[\n]+|[.?!] ", text) if w is not None and len(w.strip()) > 1]

# 문장 클렌징
def clean_text(text):
    text = strip_tags(text) # remove html tags
    text = regex.sub("(?s)<ref>.+?</ref>", "", text) # remove reference links
    text = regex.sub("(?s)<[^>]+>", "", text) # remove html tags
    text = regex.sub("&[a-z]+;", "", text) # remove html entities
    text = regex.sub("(?s){{.+?}}", "", text) # remove markup tags
    text = regex.sub("(?s){.+?}", "", text) # remove markup tags
    text = regex.sub("(?s)\[\[([^]]+\|)", "", text) # remove link target strings
    text = regex.sub("(?s)\[\[([^]]+\:.+?]])", "", text) # remove media links
    
    text = regex.sub("[']{5}", "", text) # remove italic+bold symbols
    text = regex.sub("[']{3}", "", text) # remove bold symbols
    text = regex.sub("[']{2}", "", text) # remove italic symbols
    
    text = regex.sub(u"[^ \r\n\p{Latin}\p{Hangul}_.?/!]", " ", text) # Replace unacceptable characters with a space.

    text = regex.sub("[ ]{2,}", " ", text) # Squeeze spaces.
    
    return text



# 문장을 tokenize 하여 corpus를 파일에 쓴다.
def write_corpora(sentences, output_file_handle, tagger=None):
    target_tags = None

    if tagger is None:
        tagger = Mecab()

    if isinstance(tagger, konlpy.tag._okt.Okt):
        target_tags = ['Alpha', 'Noun', 'Adjective']
    elif isinstance(tagger, konlpy.tag._kkma.Kkma):
        target_tags = ['NN', 'NNG', 'NNB', 'NNM',' NNP', 'NP', 'NR', 'OH', 'OL', 'ON', 'VA', 'VXA']
    elif isinstance(tagger, konlpy.tag._komoran.Komoran):
        target_tags = ['NNG', 'NNB', 'NNP', 'NP', 'NR', 'SH', 'SL', 'SN', 'VA']
    elif isinstance(tagger, eunjeon._mecab.Mecab):
        target_tags = ['VA', 'NNG', 'NNB', 'NNBC', 'NNP', 'NP', 'NR', 'SH', 'SL', 'SN', 'VA']
    else:
        raise ValueError(f'invalid tagger {tagger.__class__}')
    
    for i, s in enumerate(sentences):
        try:
            pos_tagged = tagger.pos(s)               
        except ValueError:
            print(f'could not {i}th parsed! sentence = {s}')
            continue

        tokenized = [t[0].strip() for t in pos_tagged if t[1] in target_tags]
        output_file_handle.write(' '.join(tokenized) + '\n')    
        