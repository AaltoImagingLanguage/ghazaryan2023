"""
Re-do the HPI fitting by swapping the coil order.
Based on the tutorial: https://neurospinmeg.wordpress.com/troubleshooting/
"""
import sys
sys.path.append("..")
import os
import subprocess
import argparse
import mne
from config import fname
from shutil import copyfile
import pandas as pd

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

coil_order = pd.read_csv(fname.coil_order)

runs_to_fix = coil_order.loc[coil_order['subject'] == subject]

for index, row in runs_to_fix.iterrows():
    session = row["session"]
    run = row["run"]
    order = row["order"]
     
    # if a derivative directory does not exist for the current subject, create one              
    os.makedirs(fname.session_dir(subject=subject, session=session), exist_ok=True)
        
    # specify where to save correct hpifit information 
    coil_info = fname.coils(subject=subject, run=run, session=session)
    
    # specify the raw file
    raw = fname.raw(subject=subject, run=run, session=session)
    
    # specify where to save fixed raw file
    fixed_raw = fname.fixed_raw(subject=subject, run=run, session=session)
    
    # make a copy of the raw file (we'll replace the bad hpi parameters 
    # with the fixed ones)
    copyfile(raw, fixed_raw)
    
    # Subject 11 has an issue in session 3, run 1 and maxfiltering identifies
    # this as a corrupt file. For this subject we will use the head
    # transformation matrix from run 2 of the same session. For all other
    # subjects we the same raw file and change the coil order. 
    if subject == 11 and run == 1:
        raw_coil = fname.raw(subject=subject, run=2, session=session)
    else:
        raw_coil = fname.raw(subject=subject, run=run, session=session)
        
    # save the hpifit parameters (using the right ordering of the coils) on 
    # the coil_info file
    coil_arg = ['hpifit_bin/hpifit',\
                '-file', raw_coil, '-swap', order.replace(" ",""),'-output',coil_info]
    subprocess.run(args=coil_arg)
                
    # replace the parameters in the copy of the raw file
    copy_hpi_arg = ['copy_trans_fiff','-f', coil_info, fixed_raw,'-r']
    subprocess.run(args=copy_hpi_arg)
