"""
Get the grand averaged evoked response
"""
import sys
sys.path.append('..')
import mne
from config import fname, subjects
import argparse
from pathlib import Path

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('event_id', type=str)
args = parser.parse_args()
event_id = args.event_id
print('Processing event_id:', event_id)

# create an empty array 
concat_ave = []
# load evoked data for each subject and each event id
for subject in subjects:
    if subject != 10:
        current_evoked = mne.Evoked(fname.trans_ave(subject=subject),condition=event_id)
        # append evoked data
        concat_ave.append(current_evoked)
# change / to - in order to not have problems when you save it
event_id = event_id.replace('/', '-')
# get the grand averaged response
grand_average = mne.grand_average(concat_ave)
# specify where to save the data 
Path(fname.grand_ave(event_id = event_id)).parent.mkdir(parents=True, exist_ok=True)
mne.write_evokeds(fname.grand_ave(event_id=event_id), grand_average)
