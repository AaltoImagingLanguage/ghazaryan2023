"""
Run MegIn's maxfilter program on the data.
"""
import sys
sys.path.append('..')
import os
import subprocess
import argparse
import mne
from config import fname
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
bad_channels = pd.read_csv(fname.bad_channels)


for session in range(1, 4):
    for run in range(1, 4): 
              
        # if deriv directory does not exist, create one              
        if not os.path.exists(fname.session_dir(subject=subject, session=session)): 
            os.makedirs(fname.session_dir(subject=subject, session=session))        
               
        output_file = fname.tsss(subject=subject, run=run, session=session)
        
        # specify which file to use as head coordinate transformation file
        # in this case we use second run of the second session
        trans_file =  fname.raw(subject=subject, run=2, session=2)
        
        # specify where to save head coordinates
        # this may be used later to visualise head movements 
        head_file  = fname.tsss_head(subject=subject, run=run, session=session)
        
        # extract bad channels of the current subject
        current_bad = bad_channels.query(f'subject=={subject} and session=={session} and run=={run}').channels.iloc[0]
        
        args = ['maxfilter', '-o', output_file, '-trans',
                trans_file, '-movecomp', 'inter', '-st', '60', '-ds', '2',
                '-v', '-autobad', 'off', '-hpicons', '-hp', head_file, '-origin', 'fit',
                '-frame', 'head', '-bad'] +  current_bad.split() 
        
        # check whether the subject had hpi fit erreor
        order = coil_order.query(f'subject=={subject} and session=={session} and run=={run}')
        if len(order) > 0:
            # use fixed raw file with correct hpi fit parameters
            input_file = fname.fixed_raw(subject=subject, run=run, session=session)
            
            # extract the correct coil order
            correct_order = (order.order).iloc[0]
            
            # maxfilter must take into account the good order  
            args = args + ['-f', input_file,'-hpiperm'] + correct_order.split()
        else: 
            # otherwise use the initial raw file
            input_file = fname.raw(subject=subject, run=run, session=session)
            args = args + ['-f', input_file]
            
        # run maxfilter, save the log 
        with open(fname.tsss_log(subject=subject, run=run, session=session), "w") as log_output:
            subprocess.run(args=args, stdout=log_output, stderr=log_output)
