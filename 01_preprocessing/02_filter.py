"""
Apply bandpass filters to the data.
"""
import sys
sys.path.append('..')
import argparse
import mne
from config import fname, n_jobs

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

for session in range(1, 4):
    for run in range(1, 4):
        # Load the tSSS transformed data.
        tsss = mne.io.read_raw_fif(fname.tsss(subject=subject, run=run, session=session),
                                   preload=True)
        
        # as the data has already been high passed filtered during maxfiltering, 
        # we only apply a low pass filter
        tsss_lowpass = tsss.copy().filter(
            None,40, l_trans_bandwidth='auto',
            h_trans_bandwidth='auto', filter_length='auto', phase='zero',
            fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)
        
        # Highpass the EOG channels to > 1Hz (autoreject should work better)
        picks_eog = mne.pick_types(tsss_lowpass.info, meg=False, eog=True)
        tsss_lowpass.filter(
            1., None, picks=picks_eog, l_trans_bandwidth='auto',
            filter_length='auto', phase='zero', fir_window='hann',
            fir_design='firwin', n_jobs=n_jobs)
        
        # Highpass the data to > 1Hz
        # we will fit ICA on this and will apply to lowpass filtered data
        tsss_highpass = tsss.copy().filter(
            1., None, l_trans_bandwidth='auto',
            h_trans_bandwidth='auto', filter_length='auto', phase='zero',
            fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)
        
        # save the data
        f_lowpass = fname.filt_lowpass(subject=subject, run=run, session=session)
        tsss_lowpass.save(f_lowpass, overwrite=True)
            
        f_highpass = fname.filt_highpass(subject=subject, run=run, session=session)
        tsss_highpass.save(f_highpass, overwrite=True)
