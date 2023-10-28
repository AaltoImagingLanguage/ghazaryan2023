"""
Prepare word2vec vectors for RSA.
"""
from scipy.io import loadmat, savemat
from sklearn.model_selection import LeavePOut
from sklearn.preprocessing import StandardScaler
import numpy as np

norm_file = 'target_vectors.mat'

data = loadmat(norm_file)
vectors = data['vectors']
words = data['basic_words']


sc = StandardScaler()
y = sc.fit_transform(vectors)


savemat("CORnet_vectors/word2vec.mat",\
                {'vectors' : y,"basic_words":words})







