from scipy.spatial import distance
from scipy.stats import zscore
from sklearn.model_selection import LeavePOut
from sklearn.linear_model import RidgeCV as RidgeGCV
import numpy as np
from scipy.spatial.distance import cdist
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def _patterns_from_weights(X, W, y_hat):
    """Compute activity patterns from regression weights.

    Regression weights originating from multivariage regression cannot be
    directly interpreted. Instead, they must be multiplied with the covariance
    matrix of the data in order to yield 'patterns' instead of 'filters' [1].
    The resulting patterns can be interpreted.

    Parameters
    ----------
    X : 2D array (n_samples, n_features)
        The data the learning was performed on.
    W : 1D array (n_features)
        The regression weights (may include the 1's added for learning the bias).
    y_hat : 2D array (n_samples, n_targets)
        The targets that where predicted from the data (not the ground thruth!).
    alpha : 1D array (n_targets)
        The optimal shrinkage parameters chosen by the regression algorithm.

    Returns
    -------
    P : 2D array (n_samples, n_features)
        The activity patterns.

    References
    ----------
    [1] Haufe, S., Meinecke, F., Görgen, K., Dähne, S., Haynes, J.-D.,
    Blankertz, B., & Bießmann, F. (2014). On the interpretation of weight
    vectors of linear models in multivariate neuroimaging. NeuroImage, 87,
    96–110.  http://doi.org/10.1016/j.neuroimage.2013.10.067
    """	
    # Check input dimensions
    n_samples, n_features = X.shape
    if W.shape[1] != n_features:
        raise ValueError("The number of weights doesn't match the number of features.")
    assert y_hat.shape[0] == n_samples

    # Compute inverse covariance of the predicted targets
    SS = (y_hat - y_hat.mean(axis=0)) / np.sqrt(n_samples - 1)
    S_cov_i = np.linalg.pinv(SS.T.dot(SS))

    # Compute patterns
    XX = (X - X.mean(axis=0)) / np.sqrt(n_samples - 1)

    # Rewrite equation (6) from Haufe2014 to be more computationally friendly:
    # P = cov_X * W * cov_S^(-1)
    # P = (X.T * X) * W * cov_S^(-1)
    # P = X.T * (X * W) * cov_S^(-1)

    P = XX.T.dot(XX.dot(W.T))
    P = P.dot(S_cov_i).T

    return P



def brain_semspace_map_loo(X_train, X_test, y, perm=False, 
                           normalize_brain=True,
                           pca=None, model=None):
    """
    Learn mapping from brain data to semantic space.
    
    This function trains and returns predictions for a given model
    (which defaults to linear ridge regression), using a leave-one-out
    cross-validation scheme.

    Parameters
    ----------
    X_train : 2D array (n_targets, n_brain_features)
        The brain data to train on.
    X_test : 2D array (n_targets, n_brain_features)
        The brain data to test on.
    y : 2D array (n_targets, n_semantic_features)
        The targets to learn from the data.
    perm: bool
        Whether to shuffle training data for permutation test calculation.
    normalize_brain : bool
        Whether to normalize X (normalize along each column).
        Defaults to True (you normally always want to do this).
    pca: 2D array
        PCA vectors of targets.
    model : scikit-learn regression model | None
        The model to use. If None, the RidgeGCV modelm
        will be used. You can also pass a scikit-learn pipeline
        here, which is useful if you want to add some preprocessing steps that
        should be done at each iteration of the leave-two-out loop.

    Returns    
    -------
    prediction_distances:
    """
    assert len(X_train) == len(y)
    n_samples, n_features = X_train.shape
    _, n_targets = y.shape
 
    # model to use
    if model is None:
        alphas = [.0000001, .000001, .00001, .0001, .001, .01, .1, .5, 1, 5,
                  10, 50, 100, 500, 1000, 10000, 20000, 50000, 100000, 500000,
                  1000000, 5000000, 10000000]
        model = RidgeGCV(alphas=alphas, alpha_per_target=True,
                         fit_intercept=True,
                         store_cv_values=True)
    
    if perm:
    	#perform permutation for p-value
    	order = np.arange(0,n_samples)
    	np.random.shuffle(order)
    	X_train = X_train[order]
    	X_test = X_test[order]
    	
    # create an empty array 
    if pca is not None:
    	predictions = np.zeros((n_samples, pca[0].shape[1]))
    else:
        predictions = np.zeros((n_samples,n_targets))
    
    y = zscore(y, axis=0, ddof=1)  
    
    # Do leave-1-out crossvalidation
    cv = LeavePOut(1)
    for train_index, test_index in cv.split(X_train, y):
        current_train_x = X_train[train_index]
        current_train_y = y[train_index]
        current_test_x = X_test[test_index]   
        
        if normalize_brain:
            sc_brain = StandardScaler()
            current_train_x = sc_brain.fit_transform(current_train_x)
            current_test_x  = sc_brain.transform(current_test_x)
            
        if pca is not None:
            current_train_y = pca[test_index].squeeze()

            
        # train the model
        model.fit(current_train_x, current_train_y)


        # test the model
        prediction = model.predict(current_test_x)
        predictions[test_index] = prediction 

    return predictions
