from scipy.io import loadmat, savemat
from sklearn.model_selection import LeavePOut
from sklearn.preprocessing import StandardScaler
import numpy as np

norm_file = 'target_vectors.mat'

data = loadmat(norm_file)
vectors = data['vectors']
words = data['basic_words']

cv = LeavePOut(1)

train_mat=[]
test_mat=[]
for train_index, test_index in cv.split(vectors):
    train_data = vectors[train_index]
    test_data = vectors[test_index]
    
    # scale train data
    sc = StandardScaler()
    y_train = sc.fit_transform(train_data)
    
    # transform test data 
    y_test = sc.transform(test_data)[0]
    train_mat.append(y_train)
    test_mat.append(y_test)
    
savemat("CORnet_vectors/pca_cv/word2vec_train.mat",{'vectors' : np.array(train_mat),"basic_words":words})
savemat("CORnet_vectors/pca_cv/word2vec_test.mat",{'vectors' : np.array(test_mat),"basic_words":words})







