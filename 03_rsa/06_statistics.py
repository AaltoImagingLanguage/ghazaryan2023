"""
RSA statistics.
"""
import os
import mne
import numpy as np
from mne import spatial_src_adjacency
from mne.stats import (spatio_temporal_cluster_1samp_test)
import scipy.io 
import argparse
import sys
from config import fname
from pathlib import Path


# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-sl', '--sliding', metavar='N', type=int, default=-1)
parser.add_argument('-cum','--cumulative', type=int, default=-1)
parser.add_argument('-t','--time', type=int, default=20)

parser.add_argument('-l', '--level', metavar='filename', type=str, default="word2vec")
args = parser.parse_args()

src_f = os.path.join(fname.freesurfer_dir, 'fsaverage-5.1.0', 'bem', 'fsaverage-5.1.0-ico-4-src.fif')
src = mne.read_source_spaces(src_f)
connectivity =  spatial_src_adjacency(src)
t = args.time
level=args.level
print(level)
a = []
for hemi in ['lh','rh']:
    fname_label = f'freesurfer/fsaverage-5.1.0/label/{hemi}.Medial_wall.label' 
    label = mne.read_label(fname_label)
    label.values.fill(1)
    # morph label to ico4
    label = label.morph(
        subject_from='fsaverage-5.1.0',
        subject_to='fsaverage-5.1.0',
        smooth=5,
        grade=[np.arange(2562), np.arange(2562)],
        subjects_dir=fname.freesurfer_dir,
        n_jobs=1,
        verbose=None
    )
    if len(a) == 0:
        a = label.get_vertices_used()
    else:
        b = label.get_vertices_used()         
exclude = np.concatenate([a, b+2562]) #add lh offset to rh indices


# concatenate data from different subjects
def gather_data(t, analysis_type, window_size, n_s=20, bad_s=[10],level=level):
    # t corresponds to the timepoint of interest 
    X = []
    for subject in range(1,n_s+1):
        if subject not in bad_s:
            stc = mne.read_source_estimate(
                fname.rsa_visual(subject=subject, analysis_type=analysis_type,
                          t=t,window_size=window_size,level=level)
            )
            n_vertices_sample, n_times = stc.data.shape
            X.append(np.transpose(stc.data, [1, 0]))
    return np.array(X)

n_permutations = 5000

all_X = []
all_clusters = []
all_T = []
all_p = []

tmax = 50


if (args.cumulative == -1) and (args.sliding == -1):
    # Statistics for RSA on the whole data with both temporal and spatial radius
    analysis_type="full"
    all_X = gather_data(analysis_type=analysis_type, t=tmax, window_size=tmax)
    all_T, all_clusters, p_values, H0 = spatio_temporal_cluster_1samp_test(
        all_X, adjacency=connectivity, tail=0, n_permutations=n_permutations,
        spatial_exclude=exclude)
else: 
    if args.cumulative != -1:
        # Statistics for cumulative window RSA with only spatial radius
        window_size = args.cumulative
        analysis_type = 'cumulative'
        
    elif args.sliding != -1:
        # Statistics for sliding window RSA with only spatial radius
        window_size = args.sliding
        analysis_type = 'sliding'
    
    # as sliding analysis is with no overlapping windows
    # cumulative and sliding increments are the same
    # for each time window gather the data from all participants
    X = gather_data(analysis_type=analysis_type, 
                    t=t, window_size=window_size,level=level)
    
    # run spatio_temporal_cluster_1samp_test
    T_obs, clusters, p_values, H0 = spatio_temporal_cluster_1samp_test(
        X, adjacency=connectivity, tail=0, n_permutations=n_permutations,
        spatial_exclude=exclude, out_type='mask')
    
    

Path(fname.rsa_stats_visual_t(analysis_type=analysis_type, 
                              window_size=window_size,level=level,
                              time=t)).parent.mkdir(parents=True, exist_ok=True)

scipy.io.savemat(
    fname.rsa_stats_visual_t(analysis_type=analysis_type, 
                             window_size=window_size,level=level,
                             time=t),
    {'X': X, 
     'clusters': clusters,
     'T_obs': T_obs,
     'p_val': p_values}
)
