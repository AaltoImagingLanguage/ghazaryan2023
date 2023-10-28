"""
Run ridge regression to learn mapping between brain response and feature vectors.
"""
import sys
sys.path.append('..')
import argparse
import subprocess
from scipy.io import loadmat
from brain_semspace_map import brain_semspace_map_loo
from pathlib import Path
from scipy.io import savemat
import numpy as np

print('Code version:'+ subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8'))
norm_file = 'target_vectors.mat'


# Handle command line arguments
parser = argparse.ArgumentParser(description='Learn brain semantic space mapping.')

parser.add_argument('input_file', type=str,
                    help='The file that contains the subject data; should be a .mat file.')
parser.add_argument('-i', '--subject-id', metavar='N', type=int, default=1,
                    help='The subject-id (as a number). This number is recorded in the output .mat file. Defaults to 1.')
parser.add_argument('-input2','--input_file2', metavar='filename',type=str,
                    help='The file that contains the test subject data (if different from training subject); should be a .mat file.')
parser.add_argument('-i2', '--subject-id2', metavar='N', type=int, default=1,
                    help='The subject-id of the test subject (as a number). This number is recorded in the output .mat file. Defaults to 1.')
parser.add_argument('-o', '--output', metavar='filename', type=str, default='./results.mat',
                    help='The file to write the results to; should end in .mat. Defaults to ./results.mat.')
parser.add_argument('-n', '--norms', metavar='filename', type=str, default=norm_file,
                    help='The file that contains the norm data. Defaults to %s.' % norm_file)
parser.add_argument('-c', '--control', metavar='filename', type=str, default=None,
                    help=('The file that contains the control variables; should end in .mat. Defaults to None, which disables '
                          'adding control variables.'))
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Whether to show a progress bar')
parser.add_argument('-b', '--break-after', metavar='N', type=int, default=-1,
                    help='Break after N iterations (useful for testing)')
parser.add_argument('-tr', '--time-resolved', metavar='N', type=int, default=-1,
                    help='When set, decoding is performed in a time-resolved manner using a sliding window of size N.')
parser.add_argument('-pca','--pca', metavar='filename', type=str,nargs='?', default=None)
parser.add_argument('-cum','--cumulative', type=int, default = -1,
                    help="When set, decoding is performed with a cumulative window of step size N.")
parser.add_argument('-tc','--temporal-cross', type=int, default = -1,
                    help="When set, cross-temporal decoding is performed.")
parser.add_argument('-p','--permutation', type=int, default = -1,
                    help-"When set will generate permutations.")

args = parser.parse_args()
verbose = args.verbose
if args.break_after > 0:
    break_after = args.break_after
else:
    break_after = None

print('Subject:', args.subject_id)
print('Input:', args.input_file)
print('Norms:', args.norms)

if args.input_file2 is None:
    print('Performing within subject decoding')
elif args.input_file != args.input_file2:
    print('Performing cross subject decoding')
    print('Train subject:', args.subject_id)
    print('Test Subject:', args.subject_id2)
if args.temporal_cross != -1:
    print('Performing temporal cross decoding')
if args.time_resolved != -1:
    print('Performing time-resolved analysis')
if args.cumulative != -1:
    print('Performing cumulative analysis')

print('Output:', args.output)

# Load MEG data
m = loadmat(args.input_file)

X_train = m['megdata']

if args.input_file2 is None:
    # then its normal within subject decoding
    X_test = X_train
else:
    m = loadmat(args.input_file2)
    X_test = m['megdata']



target_word_labels = [w.strip() for w in m['items']]
n_stimuli = len(target_word_labels)
cat_index = m['cat_index']


if args.pca:
    print("PCA vectors used")
    print(args.pca)
    pca = loadmat(args.pca)
    order_pca = [np.char.strip(pca['basic_words']).tolist().index(w) for w in target_word_labels]
    pca = pca['vectors'][order_pca]
else:
    pca = None

_, n_vertices, n_times = X_train.shape    

m = loadmat(args.norms)
y = m['vectors']
n_targets = y.shape[1]

norm_words = m['basic_words']
norm_words = [i.strip() for i in norm_words]
order = [norm_words.index(w) for w in target_word_labels]
y_norm = y[order]


if args.permutation != -1:
    np.random.seed(args.permutation)
    
# cumulative
if args.cumulative != -1:
    predictions = []
    weights = []
    patterns = []
    alphas = []
    target_scores = []
    perm = (args.permutation != -1)
    X_train = X_train.reshape(-1, n_vertices, n_times)
    X_test = X_test.reshape(-1, n_vertices, n_times)
    # first timepoint = t0, last timepoint = n_times + 1 - window size (args.cumulative)
    for t in range(0, n_times + 1 - args.cumulative):
        X_train_slice = X_train[:, :, :t + args.cumulative]
        _, _, n_times_slice = X_train_slice.shape    

        X_train_slice = X_train_slice.reshape(-1, n_vertices * n_times_slice)
        X_test_slice = X_test[:, :, :t + args.cumulative].reshape(-1, n_vertices * n_times_slice)
        if verbose:
            print('Decoding up to (including) t %d' % (t))
        current_predictions = brain_semspace_map_loo(X_train=X_train_slice, X_test=X_test_slice,
                                         y=y_norm, pca = pca, perm=perm)   
        predictions.append(current_predictions)
        

# time-resolved (sliding window)
elif args.time_resolved != -1:
    predictions = []
    weights = []
    patterns = []
    alphas = []
    target_scores = []
    perm = (args.permutation != -1)
    X_train = X_train.reshape(-1, n_vertices, n_times)
    X_test = X_test.reshape(-1, n_vertices, n_times)
    for t in range(0, n_times + 1 - args.time_resolved):
        X_train_slice = X_train[:, :, t:t + args.time_resolved].reshape(-1, n_vertices * args.time_resolved)
        X_test_slice = X_test[:, :, t:t + args.time_resolved].reshape(-1, n_vertices * args.time_resolved)
        if verbose:
            print('Decoding from t %d' % (t), 'to (not including) %d' %(t + args.time_resolved))      
        current_predictions = brain_semspace_map_loo(X_train=X_train_slice, X_test=X_test_slice,
                                         y=y_norm, normalize_brain=True, pca=pca, perm=perm)   
        predictions.append(current_predictions)
        
         
         
# cross-temporal
elif args.temporal_cross != -1:
    predictions = []
    weights = []
    patterns = []
    alphas = []
    target_scores = []
    perm = (args.permutation != -1)
    
    for t_train in range(n_times + 1 - args.temporal_cross):
        X_train_slice = X_train[:, :, t_train:t_train + args.temporal_cross].reshape(-1, n_vertices * args.temporal_cross)
        for t_test in range(n_times - args.temporal_cross + 1):
            X_test_slice = X_test[:, :, t_test:t_test + args.temporal_cross].reshape(-1, n_vertices * args.temporal_cross)
            if verbose:
                print(f'Training on t {t_train} to (not including) {t_train + args.temporal_cross}')
                print(f'Testing on t {t_test} to (not including) {t_test + args.temporal_cross}') 
            current_predictions = brain_semspace_map_loo(
                X_train=X_train_slice,
                X_test=X_test_slice,
                y=y_norm,perm=perm,
                normalize_brain=True,
                pca=pca)  
            
            predictions.append(current_predictions)
            
# full time course
else: 
    X_train = X_train.reshape(-1, n_vertices * n_times)
    X_test = X_test.reshape(-1, n_vertices * n_times)
    # permutation test
    perm = (args.permutation != -1)
    predictions = brain_semspace_map_loo(
        X_train=X_train,
        X_test=X_test,
        y=y_norm,
        perm=perm,
        normalize_brain=True,
        pca=pca)
    predictions = [predictions]


results = {
    'predictions': predictions,
    'subject': args.subject_id,
    'inputfile': args.input_file,
    'normfile': args.norms,
    'targets': target_word_labels,
    'sliding': args.time_resolved,
    'cumulative': args.time_resolved,
    'temporal_cross': args.temporal_cross,

}
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
savemat(args.output, results)
