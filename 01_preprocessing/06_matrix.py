'''
Obtain data matrices suitable for the zero-shot learning algorithm.
'''
import sys
sys.path.append('..')
import argparse
from config import fname, events_id, triggers, categories
import mne
import numpy as np
import scipy.io 
from pathlib import Path

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

# we'll append data to these empty arrays later
spoken_data = []
written_data = []
picture_data = []
category_info = []
trigger_info = []

for event_id in events_id:
    # load evoked data for the current item
    current_evoked = mne.Evoked(fname.ave(subject=subject),condition=event_id)
    # crop and resample the data
    current_evoked.crop(0, 1)
    current_evoked.resample(50)
    
    # if the event_id contains "picture" string, append to picture data
    if 'picture' in event_id:
        picture_data.append(current_evoked.data)
        
        for key, value in categories.items():
            if key in event_id:
                category_info.append(value)
        
        # as all triggers are repeated in each category, we calculate it only once on picture data
        # extarct corresponding finnish word
        current_trigger = (triggers.finnish[triggers.key== event_id].iloc[0].strip())[:-3]
        trigger_info.append(current_trigger)
    
    # do the same for written and spoken words
    elif 'written' in event_id:
        written_data.append(current_evoked.data)
        
    elif 'spoken' in event_id:
        spoken_data.append(current_evoked.data)

spoken = np.array(spoken_data)
written= np.array(written_data)
picture = np.array(picture_data)
trigger_info = np.array(trigger_info)
cat_info= np.array(category_info)

Path(fname.mat(subject=subject,modality ='spoken')).parent.mkdir(parents=True, exist_ok=True)
scipy.io.savemat(fname.mat(subject=subject, modality='spoken'),
                 {'megdata' : spoken, 'items' :trigger_info, 'cat_index': cat_info})
scipy.io.savemat(fname.mat(subject=subject, modality='written'),
                 {'megdata' : written, 'items' :trigger_info, 'cat_index': cat_info})
scipy.io.savemat(fname.mat(subject=subject, modality='picture'),
                 {'megdata' : picture, 'items' :trigger_info, 'cat_index': cat_info})
