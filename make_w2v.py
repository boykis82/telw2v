# python make_w2v.py
import nltk
import os
import codecs
import argparse
import numpy as np
import multiprocessing

# arguments setting 
parser = argparse.ArgumentParser()
parser.add_argument('--vector_size', type=int, default=200, help='the size of a word vector')
parser.add_argument('--window_size', type=int, default=5, help='the maximum distance between the current and predicted word within a sentence.')
parser.add_argument('--vocab_size', type=int, default=30000, help='the maximum vocabulary size')
parser.add_argument('--num_negative', type=int, default=5, help='the int for negative specifies how many “noise words” should be drawn')
args = parser.parse_args()

vector_size = args.vector_size
window_size = args.window_size
vocab_size = args.vocab_size
num_negative = args.num_negative

def get_min_count(sents):
    '''
    Args:
      sents: A list of lists. E.g., [["I", "am", "a", "boy", "."], ["You", "are", "a", "girl", "."]]
     
    Returns:
      min_count: A uint. Should be set as the parameter value of word2vec `min_count`.   
    '''
    global vocab_size
    from itertools import chain
     
    fdist = nltk.FreqDist(chain.from_iterable(sents))
    min_count = fdist.most_common(vocab_size)[-1][1] # the count of the the top-kth word
    
    return min_count


def make_wordvectors():
    import gensim # In case you have difficulties installing gensim, you need to consider installing conda.
    import _pickle as pickle
     
    print('Making memo sentences as list...')
    sents = []
    with open('skt_words_memo.dat', 'r', encoding='utf-8') as fin:
        while 1:
            line = fin.readline()
            if not line: break
             
            words = line.split()
            sents.append(words)

    print('Making sop sentences as list...')
    with open('skt_words_sop.dat', 'r', encoding='utf-8') as fin:
        while 1:
            line = fin.readline()
            if not line: break
             
            words = line.split()
            sents.append(words)            

    print('Making word vectors...')
    min_count = get_min_count(sents)
    model = gensim.models.Word2Vec(sents, size=vector_size, min_count=min_count,
                                   negative=num_negative, 
                                   window=window_size,
                                   sg=1,
                                   iter=200,
                                   workers=multiprocessing.cpu_count())
    
    model.save('skt_w2v.dat')
    model.wv.save_word2vec_format('skt_w2v_type')
    
    # Save to file
    with codecs.open('i2w.tsv', 'w', 'utf-8') as fout:
        for i, word in enumerate(model.wv.index2word):
            fout.write(u"{}\t{}\t{}\n".format(str(i), word.encode('utf8').decode('utf8'),
                                              np.array_str(model[word])
                                              ))
if __name__ == "__main__":
    make_wordvectors()
    
    print('Completed')