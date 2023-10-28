"""
Prepare visual feature vectors for RSA.
"""
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat
import unidecode


meg = loadmat('bids/derivatives/meg-derivatives/grand_ave/matrices/modality-picture.mat')

target_word_labels = [w.strip() for w in meg['items']]     
labels = pd.read_csv("stimuli.csv")

_,idx = np.unique(labels.word,return_index =True)
unique_labels_list = labels.word[np.sort(idx)].to_list()

    

for layer in ["V1","V2","V4","IT","decoder"]:
    print(layer)
    vectors = []
    words = []
    cornet = np.load(f"CORnet-S_{layer}_output_feats.npy")
   
    # scale train data
    sc = StandardScaler()
    y = sc.fit_transform(cornet)
    
    pca = PCA(n_components=300)
    # pca train
    y = pca.fit_transform(y)
    
    y_avg = []
    
    for w in unique_labels_list: 
        current_idx = np.where(labels.word==w)  
        average_target = np.mean(y[current_idx],axis=0)
        y_avg.append(average_target)

                
    basic_words = [unidecode.unidecode(i) for i in unique_labels_list]
    y_avg = np.array(y_avg)
    

    savemat(f"CORnet_vectors/CORnet_{layer}.mat",\
                    {'vectors' : y_avg,"basic_words":basic_words})

        
