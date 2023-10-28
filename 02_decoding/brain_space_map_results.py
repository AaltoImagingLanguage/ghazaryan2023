"""
Generate results from  predictions.
"""

from scipy.io import loadmat
from scipy.spatial import distance
import numpy as np
import pandas as pd
import argparse
from pathlib import Path
import math
from scipy.stats import pearsonr
from scipy.stats import zscore


parser = argparse.ArgumentParser(description='Analyse results.')


norm_file = 'target_vectors.mat'

parser.add_argument('input_file', type=str,
                    help='The file that contains the subject data; should be a .mat file.')
parser.add_argument('-pca','--pca', metavar='filename', type=str,nargs='?',default=None)

parser.add_argument('-m', '--megfile', type=str,
                    help='The file that contains the meg data; should be a .mat file.')
parser.add_argument('-d', '--distance-metric', type=str, default='cosine',
                    help='The distance metric to use')
parser.add_argument('-n', '--norms', metavar='filename', type=str, default=norm_file,
                    help='The file that contains the norm data. Defaults to %s.' % norm_file)
parser.add_argument('-o', '--output', metavar='filename', type=str, default='./results.csv',
                    help='The file to write the results to; should end in .csv. Defaults to ./results.csv.')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Whether to show a progress bar')


args = parser.parse_args()

predictions = loadmat(args.input_file)['predictions']

# Load MEG data
meg = loadmat(args.megfile)

target_word_labels = [w.strip() for w in meg['items']]


m = loadmat(args.norms)
y_targets = m['vectors']

norm_words = m['basic_words']
norm_words = [i.strip() for i in norm_words]
order = [norm_words.index(w) for w in target_word_labels]

y_targets = y_targets[order]
y_targets = zscore(y_targets, axis=0, ddof=1)

if args.pca:
    print("pca")
    pca = loadmat(args.pca)
    order_pca = [np.char.strip(pca['basic_words']).tolist().index(w) for w in target_word_labels]
    pca = pca['vectors'][order_pca].squeeze()
    y_targets = pca

# calculate distances
n_timepoints,n_targets,_ = predictions.shape

def pearsonr_n(v1,v2):
    return pearsonr(v1,v2)[0]
 
if args.distance_metric == "pearson":
    distances_target = distance.cdist(predictions.reshape(n_timepoints*n_targets,-1), y_targets, pearsonr_n)
else:   
    # calculate the distances between the predictions and their target vector    
    distances_target = distance.cdist(predictions.reshape(n_timepoints*n_targets,-1), y_targets, args.distance_metric)

distances_target = distances_target.reshape(n_timepoints,n_targets,-1)
voi = np.diagonal(distances_target,axis1=1,axis2=2)

# adapt to different analysis options 
    # perfect square or not
if math.isqrt((voi.shape[0])) ** 2 == voi.shape[0]:
    print('Calucalating tempral-cross distances')
    var_names = ['time1', 'time2', 'target']
    n_timepoints = math.floor(math.sqrt(n_timepoints))
    idx = [range(n_timepoints),range(n_timepoints),range(n_targets)]
else:
    var_names = ['time', 'target', ]
    idx = [range(s) for s in voi.shape]


index = pd.MultiIndex.from_product(idx, names = var_names)

df = pd.DataFrame({
   'distance': voi.flatten()
}, index = index)['distance']

if args.verbose:
    print(df)

Path(args.output).parent.mkdir(parents=True, exist_ok=True)
df.to_csv(args.output)

