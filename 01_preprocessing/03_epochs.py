"""
Create epochs.
"""
import sys
sys.path.append('..')
import os
import argparse
import mne
from mne.preprocessing import create_eog_epochs, create_ecg_epochs
from config import fname, baseline, reject, events_id, epoch_tmin, epoch_tmax

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)



for session in range(1,4):
    for run in range(1,4):
        
        # eog epochs will be created on this
        filt_highpass = mne.io.read_raw_fif(fname.filt_highpass(subject=subject, run=run, session=session),
                                            preload=True)
       
        # ecg epochs will be created on this
        raw = mne.io.read_raw_fif(fname.raw(subject=subject, run=run, session=session),
                                  preload=True).filter(1.,40)
        
        # dirty epochs will be created on this (later ica will be applied on this)
        filt_lowpass = mne.io.read_raw_fif(fname.filt_lowpass(subject=subject, run=run, session=session),
                                           preload=True)
                                  
        # Make epochs
        events = mne.find_events(filt_lowpass, stim_channel='STI101', shortest_event=2, min_duration=0.003)
            
        # Compensate for projector delay for visual stimuli (event_id > 70)
        events[events[:, 2] > 70, 0] += int(round(0.0345 * filt_lowpass.info['sfreq']))
    
        # create dirty epochs and save
        dirty_epochs = mne.Epochs(filt_lowpass, events, events_id, epoch_tmin, epoch_tmax,
                                  baseline=baseline, preload=True)       
        dirty_epochs.save(fname.dirty_epo(subject=subject, session=session, run=run), overwrite=True)
        
        # for some of the subjects the number of eog epochs was too low due to some problems in EOG channels
        # for this subjects the data was annotated so that the eog epochs reflect real eog activity
        if os.path.exists(fname.annot(subject=subject, session=session,run=run)): 
            annot_from_file = mne.read_annotations(fname.annot(subject=subject,session=session,run=run))
            filt_highpass.set_annotations(annot_from_file)
         
        # for subject 14 and 20, in some of the runs EOG062 channel was broken
        elif (subject == 14 and session == 3) or (subject == 20 and session == 2 and run ==3):
            filt_highpass.info['bads'].append('EOG062')    
                
        # create eog epochs and save them
        eog_epochs = create_eog_epochs(filt_highpass, reject=reject) 
        eog_epochs.apply_baseline((None, None))
        eog_epochs.save(fname.eog_epo(subject=subject, session=session, run=run))
        
        # after tsss the function couldn't find the remaining ecg activity
        # for this reason ecg was built on raw data
        
        # create ecg epochs and save them
        ecg_epochs = create_ecg_epochs(raw, reject=reject) 
        ecg_epochs.apply_baseline((None, None))
        ecg_epochs.save(fname.ecg_epo(subject=subject, session=session, run=run)) 
