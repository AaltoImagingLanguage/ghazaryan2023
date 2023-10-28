"""
Generate source estimate and BEM solution.
"""
import sys
sys.path.append('..')
import mne
from config import fname
import argparse

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)
 
freesurfer_dir = fname.freesurfer_dir

trans_tsss = fname.tsss(subject=subject, session=2, run=2)
info = mne.io.read_info(trans_tsss)
src = mne.setup_source_space(f'sub-{subject:02d}',
                             spacing='ico4',
                             subjects_dir=freesurfer_dir,
                             n_jobs = 4)
src.save(fname.src(subject=subject),overwrite=True)


# bem solution    
model = mne.make_bem_model(subject="sub-%02d" %subject, ico=4,
                           conductivity=(0.3,), # for single layer
                           subjects_dir=freesurfer_dir)
bem = mne.make_bem_solution(model)

mne.write_bem_solution(fname.bem(subject=subject), 
                       bem, overwrite=True, verbose=True)
