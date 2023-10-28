"""
Average visual model vectors over instances of the same concept

"""
import numpy as np
import pandas as pd
import unidecode
from scipy.io import savemat



labels = pd.read_csv("stimuli.csv")

for layer in ["V1","V2","V4","IT","decoder"]:
    vectors = []
    words = []
    cornet = np.load(f"CORnet-S_{layer}_output_feats.npy")
    for w in np.unique(labels.word):
        current_idx = np.array(labels.query('word==@w').index)
        average_vector = np.mean(cornet[current_idx],axis=0)
        vectors.append(average_vector)
        words.append(w)
   
    basic_words = [unidecode.unidecode(i) for i in words]

    savemat(f"CORnet_vectors/CORnet_{layer}.mat",\
                    {'vectors' : vectors, 'words':words,"basic_words":basic_words})
    
