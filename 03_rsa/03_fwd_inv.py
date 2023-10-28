"""
Forward model and inverse.
"""
import sys
sys.path.append('..')
import mne
from config import fname
import argparse
from mne.minimum_norm import make_inverse_operator

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)
 
epochs = mne.read_epochs(fname.epochs_all(subject=subject))
epochs= epochs["picture"].pick_types("grad")
 
fwd = mne.make_forward_solution(info = epochs.info,
                                trans = fname.trans_coreg(subject=subject), 
                                src=fname.src(subject=subject), 
                                bem=fname.bem(subject=subject),
                                meg=True, eeg=False, n_jobs=1,
                                verbose=True, mindist=5.0)

mne.write_forward_solution(fname.fwd(subject=subject),fwd,overwrite=True)

noise_cov = mne.compute_covariance(epochs, tmax=0.)
noise_cov = mne.cov.regularize(noise_cov, epochs.info)
noise_cov.save(fname.noise_cov(subject=subject))

inverse_operator = make_inverse_operator(epochs.info, fwd, noise_cov,loose=0.3,depth=0.8)
mne.minimum_norm.write_inverse_operator(fname.inv(subject=subject), inverse_operator)
