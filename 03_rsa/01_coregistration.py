"""
Perform coregistration for RSA.
"""
import sys
sys.path.append('..')
import mne
from config import fname

subject = 20
trans_tsss = fname.tsss(subject=subject, session=2, run=2)
info = mne.io.read_info(trans_tsss)

#%% coregister
coreg = mne.gui.coregistration(
    subject=f'sub-{subject:02d}',
    subjects_dir=fname.freesurfer_dir,
    inst=trans_tsss,
    trans=None,
    orient_to_surface=True,
    mark_inside=True,
    head_high_res=True,
    head_inside=True
)

#%% check coregistration
mne.viz.plot_alignment(
    info,
    trans=fname.trans_coreg(subject=subject),
    subject=f'sub-{subject:02d}',
    subjects_dir=fname.freesurfer_dir,
    surfaces='brain',
    show_axes=True,
    dig=True,
    eeg=[],
    meg='sensors',
    coord_frame='meg'
)
