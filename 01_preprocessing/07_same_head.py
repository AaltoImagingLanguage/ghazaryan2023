"""
Bring all subjects' heads to the same head position.
"""
import sys
sys.path.append('..')
import subprocess
import argparse
import mne
from config import fname

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)



# specify input and output files
input_file = fname.ave(subject=subject)
output_file = fname.trans_ave(subject=subject)

# bring all subjects evoked data to the same position (subject 7)
trans_file = fname.ave(subject=7)
# save the log
log_file = fname.trans_log(subject=subject)

# run maxfilter
args = ['maxfilter', '-f', input_file, '-o', output_file, '-trans', trans_file, '-v', '-force']
with open(log_file,"w") as log_output:
    subprocess.run(args=args, stdout=log_output, stderr=log_output)
