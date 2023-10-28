"""
Use ICA to removed EOG and ECG artifacts from the data.
"""
import sys
sys.path.append('..')
import argparse
import mne
from mne.preprocessing import ICA
from config import fname, baseline, reject
import pandas as pd

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

components = pd.read_csv(fname.components)


for session in range(1, 4):
    for run in range(1, 4):
        # load highpass filttered data (ica will be fit on this)
        filt_highpass = mne.io.read_raw_fif(fname.filt_highpass(subject=subject, run=run, session=session),
                                            preload=True)
        # load dirty epochs (ica will be applied on this)
        dirty_epochs = mne.read_epochs(fname.dirty_epo(subject=subject, session=session, run=run))
       
        n_components = 0.999

        print('Fitting ICA')
        ica = ICA(method='fastica', random_state=42, n_components=n_components)
        
        # fit ica on highpass filtered data
        ica.fit(filt_highpass, reject=reject, decim=5, picks='grad')
        print('Fit %d components (explaining at least %0.1f%% of the variance)'
              % (ica.n_components_, 100 * n_components))
        
                    
        current_comp = components.query(f'subject=={subject} and session=={session} and run=={run}').components.iloc[0]       
        
        ica.exclude = [int(i) for i in current_comp.split()]
        
        # Save the ICA decomposition
        ica.save(fname.ica(subject=subject, session=session, run=run))
      
        # apply ICA solution
        clean_epochs = ica.apply(dirty_epochs)
        clean_epochs = clean_epochs.apply_baseline(baseline)
        
        # save clean epochs
        clean_epochs.save(fname.clean_epo(subject=subject, session=session, run=run), overwrite=True)
