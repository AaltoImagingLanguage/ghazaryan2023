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

pic_target_dict = dict ()

for w in np.unique(labels.word):
    test_idx = np.array(labels.query('word==@w').index)
    train_idx = np.ones(len(labels),dtype="bool")
    train_idx[test_idx] = False

    pic_target_dict[w]=(train_idx,test_idx)
    

for layer in ["V1","V2","V4","IT","decoder"]:
    print(layer)
    vectors = []
    words = []
    cornet = np.load(f"CORnet-S_{layer}_output_feats.npy")
    train_mat = []
    test_mat = []
    count = 0
    # average cornet output per concept
    for w in unique_labels_list:
        
        words.append(w)
        count += 1
        print(count)
        # first assign all train idx as 1
        train_idx,test_idx = pic_target_dict[w]
        
        y_train = cornet[train_idx]
        y_test = cornet[test_idx]
        
           
        # scale train data
        sc = StandardScaler()
        y_train = sc.fit_transform(y_train)
        
        # transform test data 
        y_test = sc.transform(y_test)
        
        pca = PCA()
        # pca train
        y_train = pca.fit_transform(y_train)
        
        # pca transform test
        y_test = pca.transform(y_test)
        
        
        average_test = np.mean(y_test,axis=0)
        test_mat.append(average_test)
        
        
        train_words_repeated = np.array(labels.word.to_list())[train_idx]
        train_words_unique = np.array(unique_labels_list)[np.where(np.array(unique_labels_list) != w)]
        
        current_train_mat = [] 

        for train_w in train_words_unique: 
            current_train_idx = np.where(train_words_repeated==train_w)    
            average_train = np.mean(y_train[current_train_idx],axis=0)
            current_train_mat.append(average_train)

        current_train_mat = np.array(current_train_mat)
        
        train_mat.append(current_train_mat)
        
    basic_words = [unidecode.unidecode(i) for i in words]
    y_train = np.array(train_mat)
    y_test= np.array(test_mat)
    
    savemat(f"CORnet_vectors/pca_cv/CORnet_{layer}_train.mat",{'vectors' : y_train,"basic_words":basic_words})
    savemat(f"CORnet_vectors/pca_cv/CORnet_{layer}_test.mat",{'vectors' : y_test,"basic_words":basic_words})

        
