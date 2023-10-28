"""
STC
"""
import sys
sys.path.append('..')
import mne
from config import fname,triggers
import argparse
import os
from pathlib import Path
import numpy as np


# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)
 
fname_fsaverage_src = os.path.join(fname.freesurfer_dir, 'fsaverage-5.1.0', 'bem',
                                   'fsaverage-5.1.0-ico-4-src.fif')

epochs = mne.read_epochs(fname.epochs_all(subject=subject))["picture"].pick_types("grad")


# EVOKED
inverse_operator = mne.minimum_norm.read_inverse_operator(fname.inv(subject=subject))
all_items_ev = epochs.average().apply_baseline((-0.2,0))       
all_items_stc = mne.minimum_norm.apply_inverse(all_items_ev, inverse_operator,method='dSPM') 
all_items_stc.save(fname.all_items_stc(subject=subject))

# morphing
src_to = mne.read_source_spaces(fname_fsaverage_src)
morph = mne.compute_source_morph(inverse_operator['src'], subject_from=f'sub-{subject:02d}',
                                 subject_to='fsaverage-5.1.0', src_to=src_to,
                                 subjects_dir=fname.freesurfer_dir)

all_items_stc_fsaverage = morph.apply(all_items_stc)
all_items_stc_fsaverage.save(fname.all_items_stc_morphed(subject=subject))

# ITEM LEVEL

items = epochs.event_id
for item in items:
    item_fin = triggers.query('key==@item')['finnish'].iloc[0].strip()[:-3]

    current = epochs[item].average().apply_baseline((-0.2,0))       
    stc = mne.minimum_norm.apply_inverse(current, inverse_operator, method='dSPM') 
    cat = item.split('/')[1]
    item = item.split('/')[2]
    
    stc_f = fname.indiv_item_stc(item=item,subject=subject)
    Path(stc_f).parent.mkdir(parents=True, exist_ok=True)
    stc.save(stc_f)
    
    # morphing    
    src_to = mne.read_source_spaces(fname_fsaverage_src)
    
    stc_morph = mne.compute_source_morph(inverse_operator['src'], subject_from=f'sub-{subject:02d}',
                                         subject_to='fsaverage-5.1.0', spacing= [np.arange(2562), np.arange(2562)],
                                         subjects_dir=fname.freesurfer_dir)
    
    stc_fsaverage = stc_morph.apply(stc)
    stc_f = fname.indiv_item_stc_morphed(item=item, subject=subject)
    Path(stc_f).parent.mkdir(parents=True, exist_ok=True)
    stc_fsaverage.save(stc_f)
