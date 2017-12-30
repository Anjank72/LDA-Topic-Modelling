# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:01:31 2017

@author: Admin
"""
from gensim.corpora.textcorpus import TextDirectoryCorpus
from gensim.corpora import Dictionary, MmCorpus
from gensim.models import LdaModel, TfidfModel
from gensim.matutils import cossim
import os
import glob

# replace LdaModel with LdaMulticore for faster train times
from gensim.models.ldamulticore import LdaMulticore
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def process():
    # read all the text files in the directory and build a corpus
    corpus = TextDirectoryCorpus("C://Users//Kumar Abhijeet//Project/Preprocess_data//JD//")
    # save word-id dictionary
    #corpus.dictionary.save_as_text('wordids_JD2.txt')
    # save matrix market format vectors
    MmCorpus.serialize('JD_bow.mm', corpus)

    # load word-id dictionary
    id2word = Dictionary.load('foobar.txtdic')
    # load matrix market format vectors
    mm = MmCorpus('JD_bow.mm')

    # train tfidf
    tfidf = TfidfModel(mm, id2word=id2word, normalize=True)
    # save tfidf model
    tfidf.save('tfidf_JD.model')
    # save tfidf vectors in matrix market format
    MmCorpus.serialize('tfidf_JD.mm', tfidf[mm])


def lda():
    """ LDA model
    https://radimrehurek.com/gensim/models/ldamodel.html

    num_topics is the number of requested latent topics to be extracted from the
    training corpus.

    id2word is a mapping from word ids (integers) to words (strings). It is used
    to determine the vocabulary size, as well as for debugging and topic
    printing.

    alpha and eta are hyperparameters that affect sparsity of the document-topic
    (theta) and topic-word (lambda) distributions. Both default to a symmetric
    1.0/num_topics prior.

    alpha can be set to an explicit array = prior of your choice. It also
    support special values of ‘asymmetric’ and ‘auto’: the former uses a fixed
    normalized asymmetric 1.0/topicno prior, the latter learns an asymmetric
    prior directly from your data.

    eta can be a scalar for a symmetric prior over topic/word distributions, or
    a vector of shape num_words, which can be used to impose (user defined)
    asymmetric priors over the word distribution. It also supports the special
    value ‘auto’, which learns an asymmetric prior over words directly from your
    data. eta can also be a matrix of shape num_topics x num_words, which can be
    used to impose asymmetric priors over the word distribution on a per-topic
    basis (can not be learned from data).

    Calculate and log perplexity estimate from the latest mini-batch every
    eval_every model updates (setting this to 1 slows down training ~2x; default
    is 10 for better performance). Set to None to disable perplexity estimation.

    decay and offset parameters are the same as Kappa and Tau_0 in Hoffman et
    al, respectively.

    minimum_probability controls filtering the topics returned for a document
    (bow).

    random_state can be a np.random.RandomState object or the seed for one

    callbacks a list of metric callbacks to log/visualize evaluation metrics of
    topic model during training

    The model can be updated (trained) with new documents via
    >>> lda.update(other_corpus)

    You can then infer topic distributions on new, unseen documents, with
    >>> doc_lda = lda[doc_bow]

    """

    # load word-id dictionary
    id2word = Dictionary.load('foobar.txtdic')
    # load matrix market format bow vectors
    # mm = MmCorpus('bow.mm')
    # load Tfidf Model in matrix market format
    mm = MmCorpus('tfidf_JD.mm')
    # train LDA model
    lda = LdaModel(
        corpus=mm, id2word=id2word, num_topics=21, distributed=False,
        chunksize=2000, passes=3, update_every=1, alpha='symmetric',
        decay=0.5, offset=1.0, eval_every=10, iterations=50,
        gamma_threshold=0.001, minimum_probability=0.01, random_state=None,
        ns_conf=None, minimum_phi_value=0.01, per_word_topics=False,
        callbacks=None)

    # save LDA model
    lda.save('lda.model')


def similarity1():
    # load word-id dictionary
    dirpath = os.getcwd()
    id2word = Dictionary.load('model_1/foobar.txtdic')
    # load LDA model
    lda = LdaModel.load('model_1/lda.model')

    # read file contents and split into words
    os.chdir(dirpath+ "//docs//")
    docs = glob.glob("*.txt")
    for file_x in docs:
        for file_y in docs:
            if file_x != file_y:
                with open(file_x) as fp:
                    doc_1 = fp.read().lower().split()
                with open(file_y) as fp:
                    doc_2 = fp.read().lower().split()

                # create document bow
                doc_1_bow = id2word.doc2bow(doc_1)
                doc_2_bow = id2word.doc2bow(doc_2)

                # infer topic distributions
                doc_1_lda = lda[doc_1_bow]
                doc_2_lda = lda[doc_2_bow]

                # find similarity using cosine distance
                similarity = cossim(doc_1_lda, doc_2_lda)
                print("The similarity score of "+ file_x[:-4] + " and "+ file_y[:-4] + " is = " + str(similarity*100))
                print()


#process()
#lda()
similarity1()