"""
Get the evoked response
"""
import sys
sys.path.append('..')
import argparse
from config import fname, events_id
import mne
from pathlib import Path


# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

     
epochs_clean_list = []
for session in range(1, 4):
    for run in range(1, 4):
        epochs_clean_list.append(mne.read_epochs(fname.clean_epo(subject=subject,session=session,run=run),
                                                 proj=False, preload=True, verbose=None))

epochs_clean = mne.concatenate_epochs(epochs_clean_list)

evokeds = [epochs_clean[event].average(picks="grad") for event in events_id]

Path(fname.ave(subject=subject)).parent.mkdir(parents=True, exist_ok=True)
mne.write_evokeds(fname.ave(subject=subject), evokeds)


epochs_clean.pick_types("grad")
epochs_clean.save(fname.epochs_all(subject=subject))
