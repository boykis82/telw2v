# python build_dictionary_from_memo.py
import os.path
from eunjeon import Mecab
import textlib as tl

MEMO_PATH_ROOT = 'D:\\memo'
CORPORA_FILE = 'skt_words_memo.dat'

mecab = Mecab()

def create_corpora_from_nateonmemo(corpora_file_name):
    with open(corpora_file_name, 'w', encoding='utf-8') as wf:   
        for (path, dir, files) in os.walk(MEMO_PATH_ROOT):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == '.html':
                    fullpath = os.path.join(path, filename)

                    with open(fullpath, 'r', encoding='utf-16') as f:                
                        doc = f.read()
                        cleansed = tl.clean_text(doc)
                        sentences = tl.sentence_segment(cleansed)
                        tl.write_corpora(sentences, wf, mecab)
                        print(f'{fullpath} completed!')

if __name__ == '__main__':
    create_corpora_from_nateonmemo(CORPORA_FILE)