"""
===========
Config file
===========
Configuration parameters for the study.
"""

import os
from socket import getfqdn
from fnames import FileNames
import pandas as pd

###############################################################################
# Determine which user is running the scripts on which machine and set the path
# where the data is stored and how many CPU cores to use. This is probably the
# only section you need to modify to replicate the pipeline as presented in van
# Vliet et al. 2018.

user = os.environ['USER']  # Username of the user running the scripts
host = getfqdn()  # Hostname of the machine running the scripts

study_path = "evidence_accumulation"
n_jobs = 1
else:
    raise RuntimeError('Please edit scripts/config.py and set the study_path '
                       'variable to point to the location where the data '
                       'should be stored and the n_jobs variable to the '
                       'number of CPU cores the analysis is allowed to use.')


###############################################################################
# These are all the relevant parameters for the analysis. You can experiment
# with changing these.

subjects = list(range(1, 21))


# Maximum number of ICA components to reject
n_eog_components = 2  # ICA components that correlate with eye blinks
n_ecg_components = 2  # ICA components that correlate with eye blinks


# Time window (relative to stimulus onset) to use for extracting epochs
epoch_tmin, epoch_tmax = -0.2, 1.1

# Time window to use for computing the baseline of the epoch
baseline = (-0.2, 0)

# Thresholds to use for rejecting epochs that have a too large signal amplitude
reject = dict(grad=3E-10)

# All "good" subjects
#subjects = [s for s in sorted(map_subjects.keys()) if s not in bad_subjects]

# Read trigger codes for items
events_file = study_path + "/stimuli/events_id.csv"

triggers = pd.read_csv(events_file)
events_id = dict(zip(triggers.key, triggers.value))

deriv_dir = study_path+"/bids/derivatives"
annot_dir = study_path + "derivatives/annotations"
data_dir = study_path+"/bids"
manual_dir = study_path+"/manual_select_files"

# map categories to corresponding indecies
categories = {'animals': 1,
              'body': 2,
              'buildings': 3,
              'characters': 4,
              'nature': 5,
              'tools': 6,
              'vehicles': 7}

###############################################################################
# Templates for filenames
#
# This part of the config file uses the FileNames class. It provides a small
# wrapper around string.format() to keep track of a list of filenames.
# See fnames.py for details on how this class works.
fname = FileNames()

# raw files and main paths

fname.add('bids_base', 'sub-{subject:02d}_ses-{session:02d}_task-naming_run-{run:02d}')
fname.add('study_path', data_dir)
fname.add('annot_path', annot_dir)
fname.add('deriv_path', deriv_dir)
fname.add('manual_path', manual_dir)
fname.add('archive_dir', '{study_path}/archive')
fname.add('meg_dir', '{study_path}/derivatives/meg-derivatives')
fname.add('subjects_dir', '{study_path}/subjects')
fname.add('subject_dir', '{meg_dir}/sub-{subject:02d}')
fname.add('session_dir', '{subject_dir}/ses-{session:02d}')
fname.add('raw', '{study_path}/sub-{subject:02d}/ses-{session:02d}/meg/{bids_base}_meg.fif')
fname.add('freesurfer_dir', '{deriv_path}/freesurfer/')
fname.add('bad_channels', '{manual_path}/bad_channels.csv')
fname.add('coil_order', '{manual_path}/coil_order.csv')
fname.add('components', '{manual_path}/ica_components.csv')



# preprocessing
fname.add('coils', '{session_dir}/{bids_base}_coils_meg.fif')
fname.add('fixed_raw', '{session_dir}/{bids_base}_fixed_raw_meg.fif')
fname.add('tsss', '{session_dir}/{bids_base}_tsss_meg.fif')
fname.add('tsss_log', '{session_dir}/{bids_base}_tsss_meg_log.txt')
fname.add('tsss_head', '{session_dir}/{bids_base}_tsss_meg_head_pos.pos')
fname.add('filt_lowpass', '{session_dir}/{bids_base}_tsss_lowpass_meg.fif')
fname.add('filt_highpass', '{session_dir}/{bids_base}_tsss_highpass_meg.fif')
fname.add('dirty_epo', '{session_dir}/{bids_base}_dirty-epo.fif')
fname.add('eog_epo', '{session_dir}/{bids_base}_eog-epo.fif')
fname.add('ecg_epo', '{session_dir}/{bids_base}_ecg-epo.fif')
fname.add('ica', '{session_dir}/{bids_base}-ica.fif')
fname.add('clean_epo', '{session_dir}/{bids_base}_clean-epo.fif')
fname.add('ave', '{subject_dir}/averaged/sub-{subject:02d}_ave.fif')
fname.add('annot', '{annot_path}/sub-{subject:02d}/ses-{session:02d}/{bids_base}_annotations.fif')
fname.add('mat', '{subject_dir}/matrices/sub-{subject:02d}_modality-{modality}_1s.mat')



# grand ave
fname.add('trans_ave', '{subject_dir}/averaged/sub-{subject:02d}_trans_ave.fif')
fname.add('trans_log', '{subject_dir}/averaged/sub-{subject:02d}_trans_log.txt')
fname.add('grand_ave','{meg_dir}/grand_ave/items/{event_id}-grand-ave.fif')
fname.add('grand_ave_mat','{meg_dir}/grand_ave/matrices/modality-{modality}.mat')

# zero_shot 
fname.add('zeroshot', '{subject_dir}/zeroshot/sub-{subject:02d}_modality-{modality}-results.mat')
fname.add('zeroshot_result', '{subject_dir}/zeroshot/sub-{subject:02d}_modality-{modality}-results.csv')
fname.add('zeroshot_tr', '{subject_dir}/zeroshot/sub-{subject:02d}_modality-{modality}-tr-results.mat')
fname.add('zeroshot_result_tr', '{subject_dir}/zeroshot/sub-{subject:02d}_modality-{modality}-tr-results.csv')



# zero_shot grand_ave
fname.add('zeroshot_mat_grand','{meg_dir}/grand_ave/zeroshot/modality-{modality}.mat')
fname.add('zeroshot_result_grand', '{meg_dir}/grand_ave/zeroshot/modality-{modality}-results.csv')
fname.add('zeroshot_mat_grand_tr','{meg_dir}/grand_ave/zeroshot/modality-{modality}-tr.mat')
fname.add('zeroshot_result_grand_tr', '{meg_dir}/grand_ave/zeroshot/modality-{modality}-tr-results.csv')
fname.add('zeroshot_mat_grand_ch','{meg_dir}/grand_ave/zeroshot/channelwise/mat/{modality}/modality-{modality}_channel-{channel}-tr.mat')
fname.add('zeroshot_result_grand_ch', '{meg_dir}/grand_ave/zeroshot/channelwise/results/{modality}/modality-{modality}_channel-{channel}-tr-results.csv')

#trajectories
fname.add('cum_traject','{subject_dir}/trajectories/sub-{subject:02d}_modality-{modality}_leftout-{cv}_cum_1s_non_std.csv')
fname.add('tr_traject','{subject_dir}/trajectories/sub-{subject:02d}_modality-{modality}_leftout-{cv}_tr_1s_non_std.csv')
fname.add('cum_shuffle_traject','{subject_dir}/trajectories/sub-{subject:02d}_modality-{modality}_leftout-{cv}_perm-{perm}_shuffled_cum.csv')

# zero shot presentation order
fname.add('mat_order', '{subject_dir}/matrices/order/picture/{matrix_type}/sub-{subject:02d}_ses-{session:02d}_rep-{rep}_type-{matrix_type}_modality-picture.mat')


# SNR check
fname.add('ave_snr', '{subject_dir}/averaged/snr/sub-{subject:02d}_rep-{rep}_ave.fif')
fname.add('mat_snr', '{subject_dir}/matrices/snr/{modality}/sub-{subject:02d}_modality-{modality}_rep-{rep}.mat')
fname.add('zeroshot_snr', '{subject_dir}/zeroshot/snr/{modality}/sub-{subject:02d}_modality-{modality}_rep-{rep}_results.mat')
fname.add('zeroshot_result_snr', '{subject_dir}/zeroshot/snr/{modality}/sub-{subject:02d}_modality-{modality}_rep-{rep}_results.csv')

# epoch arrays
fname.add('epoch_arr', '{subject_dir}/epoch_data/sub-{subject:02d}_modality-{modality}_epoch_data.npy')
fname.add('epochs_all', '{subject_dir}/epoch_data/sub-{subject:02d}_all-epochs.fif')

# cross subjects
fname.add('zeroshot_cross', '{subject_dir}/zeroshot/cross/sub-{subject:02d}_modality-{modality}_trainsub-{trainsubject:02d}_results.mat')
fname.add('zeroshot_cross_results', '{subject_dir}/zeroshot/cross/sub-{subject:02d}_modality-{modality}_trainsub-{trainsubject:02d}_results.csv')

# evoked pic
fname.add('ave_pic', '{deriv_path}/meg-derivatives/sub-{subject:02d}/averaged/sub-{subject:02d}_pic-ave.fif')
fname.add('trans_ave_pic', '{deriv_path}/meg-derivatives/sub-{subject:02d}/averaged/sub-{subject:02d}_pic_trans-ave.fif')
fname.add('trans_pic_log', '{deriv_path}/meg-derivatives/sub-{subject:02d}/averaged/sub-{subject:02d}_pic_trans-ave_log.txt')


# brain space mapping

## within subject
fname.add('bsm', '{subject_dir}/brain-space/sub-{subject:02d}_modality-{modality}-results.csv')
fname.add('bsm_tc', '{subject_dir}/brain-space/sub-{subject:02d}_modality-{modality}-tc-{window}-results.csv')
fname.add('bsm_tr', '{subject_dir}/brain-space/sub-{subject:02d}_modality-{modality}-tr-{window}-results.csv')
fname.add('bsm_cum', '{subject_dir}/brain-space/sub-{subject:02d}_modality-{modality}-cum-results.csv')


#fname.add('bsm_tr_vis', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-tr-{window}-{vector}-results.csv')
#fname.add('bsm_cum_vis', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-cum-{vector}-results.csv')

# visual
fname.add('bsm_tr_vis_mat', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-tr-{window}-{vector}-results.mat')
fname.add('bsm_cum_vis_mat', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-cum-{vector}-results.mat')
fname.add('bsm_tr_vis_csv', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-tr-{window}-{vector}-results.csv')
fname.add('bsm_cum_vis_csv', '{subject_dir}/brain-space/visual_model/sub-{subject:02d}_modality-{modality}-cum-{vector}-results.csv')


# visual perm
fname.add('bsm_tr_vis_mat_perm', '{subject_dir}/brain-space/visual_model/perm/{vector}/sub-{subject:02d}_modality-{modality}-tr-{window}-{vector}-{perm}-results.mat')
fname.add('bsm_cum_vis_mat_perm', '{subject_dir}/brain-space/visual_model/perm/{vector}/sub-{subject:02d}_modality-{modality}-cum-{vector}-{perm}-results.mat')
fname.add('bsm_tr_vis_csv_perm', '{subject_dir}/brain-space/visual_model/perm/{vector}/sub-{subject:02d}_modality-{modality}-tr-{window}-{vector}-{perm}-results.csv')
fname.add('bsm_cum_vis_csv_perm', '{subject_dir}/brain-space/visual_model/perm/{vector}/sub-{subject:02d}_modality-{modality}-cum-{vector}-{perm}-results.csv')


## across subjects
fname.add('bsm_cross', '{subject_dir}/brain-space/cross/sub-{subject:02d}_modality-{modality}_trainsub-{trainsubject:02d}_results.csv')
fname.add('bsm_cross_tc', '{subject_dir}/brain-space/cross/tc/sub-{subject:02d}_modality-{modality}_trainsub-{trainsubject:02d}_tc-{window}-results.csv')


## grand_average
fname.add('bsm_grand','{meg_dir}/grand_ave/brain-space/modality-{modality}.csv')
fname.add('bsm_grand_tc', '{meg_dir}/grand_ave/brain-space/modality-{modality}-tc-{window}-results.csv')
fname.add('bsm_grand_tr', '{meg_dir}/grand_ave/brain-space/modality-{modality}-tr-{window}-results.csv')
fname.add('bsm_grand_cum', '{meg_dir}/grand_ave/brain-space/modality-{modality}-cum-results.csv')

## RSA files
fname.add('trans_coreg','{subject_dir}/source/sub-{subject:02d}-trans.fif')
fname.add('src','{subject_dir}/source/sub-{subject:02d}-ico4-src.fif')
fname.add('bem','{subject_dir}/source/sub-{subject:02d}-ico4-bem-sol.fif')
fname.add('fwd','{subject_dir}/source/sub-{subject:02d}-ico4-fwd-sol.fif')
fname.add('noise_cov','{subject_dir}/source/sub-{subject:02d}-noise-cov.fif')
fname.add('inv','{subject_dir}/source/sub-{subject:02d}-inv.fif')
fname.add('all_items_stc','{subject_dir}/source/sub-{subject:02d}-all_stc')
fname.add('all_items_stc_morphed','{subject_dir}/source/sub-{subject:02d}-all_stc-morphed')
fname.add('indiv_item_stc','{subject_dir}/source/stcs/indiv/sub-{subject:02d}_{item}_stc')
fname.add('indiv_item_stc_morphed','{subject_dir}/source/stcs/morphed/sub-{subject:02d}_{item}_stc-morphed')
fname.add('rsa','{subject_dir}/source/stcs/morphed/rsa/{analysis_type}/{window_size}/sub-{subject:02d}_rsa_{t}')
fname.add('rsa_stats','{meg_dir}/grand_ave/rsa_results/{analysis_type}_{window_size}_rsa_results.mat')
#visual
fname.add('rsa_visual','{subject_dir}/source/stcs/morphed/rsa/visual/{analysis_type}/{window_size}/sub-{subject:02d}_rsa_{t}_{level}')
fname.add('rsa_stats_visual','{meg_dir}/grand_ave/rsa_results/visual/{analysis_type}_{window_size}_rsa_{level}_results.mat')
fname.add('rsa_stats_visual_t','{meg_dir}/grand_ave/rsa_results/visual/timepoints/{analysis_type}/{level}/{analysis_type}_{window_size}_time-{time}_rsa_{level}_results.mat')


# Filenames for MNE reports
fname.add('reports_dir', '{study_path}/derivatives/reports')
fname.add('report', '{reports_dir}/sub-{subject:02d}-report.h5')
fname.add('report_html', '{reports_dir}/sub-{subject:02d}-report.html')

# For FreeSurfer and MNE-Python to find the MRI data
os.environ["SUBJECTS_DIR"] = fname.subjects_dir

# For BLAS to use the right amount of cores
os.environ['OMP_NUM_THREADS'] = str(n_jobs)
