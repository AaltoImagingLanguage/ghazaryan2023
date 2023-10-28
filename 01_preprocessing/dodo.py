"""
Do-it 

"""
import pandas as pd
import sys
sys.path.append("..")

from config import fname, subjects, events_id


DOIT_CONFIG = dict(verbosity=2, sort='definition')

#subjects = get_var("subjects")
#subjects = [int(s) for s in subjects.split()]

coil_order = pd.read_csv(fname.coil_order)

def task_order():
    """Step 00: Re-do the HPI fitting by swapping the coil order"""
    for subject in set(subjects) & set(coil_order['subject'].unique()):
        raw_fnames = []
        raw_fixed_fnames = []
        for _, row in coil_order[coil_order['subject'] == subject].iterrows():
            raw_fnames.append(fname.raw(subject=row.subject, session=row.session, run=row.run))
            raw_fixed_fnames.append(fname.fixed_raw(subject=row.subject, session=row.session, run=row.run))

        yield dict(
            name='%02d' % subject,
            #file_dep=raw_fnames + ['00_coil_order.py'],
            targets=raw_fixed_fnames,
            actions=['python 00_coil_order.py %s' % subject],
        )


def task_tsss():
    """Step 01: apply tSSS"""
    for subject in subjects:
        tsss_fnames = []
        raw_fnames = []
        for session in range(1, 4):
            for run in range(1, 4):
                tsss_fnames.append(fname.tsss(subject=subject, session=session, run=run))
                if len(coil_order.query(f'subject=={subject} and session=={session} and run=={run}')) > 0:
                    raw_fnames.append(fname.fixed_raw(subject=subject, session=session, run=run))
                else:
                    raw_fnames.append(fname.raw(subject=subject, session=session, run=run))
        yield dict(
            name='%02d' % subject,
            #file_dep=raw_fnames + ['01_tsss.py'],
            targets=tsss_fnames,
            actions=['python 01_tsss.py %s' % subject],
            uptodate = [True],
        )


def task_filter():
    """Step 02: filter the data"""
    for subject in subjects:
        tsss_fnames = []
        filt_highpass_fnames = []
        filt_lowpass_fnames = []
        for session in range(1,4):
            for run in range(1,4):
                tsss_fnames.append(fname.tsss(subject=subject, session=session, run=run))
                filt_highpass_fnames.append(fname.filt_highpass(subject=subject, session=session, run=run))
                filt_lowpass_fnames.append(fname.filt_lowpass(subject=subject, session=session, run=run))
        yield dict(
            name='%02d' % subject,
            #task_dep=['tsss'],
            #file_dep=tsss_fnames + ['02_filter.py'],
            targets=filt_highpass_fnames + filt_lowpass_fnames,
            actions=['python 02_filter.py %s' % subject],
            uptodate = [True],
        )
        
def task_epochs():
    """Step 03: Create epochs"""
    for subject in subjects:
        raw_fnames = []
        filt_highpass_fnames = []
        filt_lowpass_fnames = []
        dirty_epo_fnames = []
        eog_epo_fnames = []
        ecg_epo_fnames = []
        for session in range(1,4):
            for run in range(1,4):
                filt_lowpass_fnames.append(fname.tsss(subject=subject, session=session, run=run))
                filt_highpass_fnames.append(fname.filt_highpass(subject=subject, session=session, run=run))
                dirty_epo_fnames.append(fname.dirty_epo(subject=subject, session=session, run=run))
                eog_epo_fnames.append(fname.eog_epo(subject=subject, session=session, run=run))
                ecg_epo_fnames.append(fname.ecg_epo(subject=subject, session=session, run=run))
                if len(coil_order.query(f'subject=={subject} and session=={session} and run=={run}')) > 0:
                    raw_fnames.append(fname.fixed_raw(subject=subject, session=session, run=run))
                else:
                    raw_fnames.append(fname.raw(subject=subject, session=session, run=run))
        yield dict(
            name='%02d' % subject,
            #task_dep=['filter'],
            #file_dep=raw_fnames+filt_highpass_fnames+filt_lowpass_fnames + ['03_epochs.py'],
            targets=dirty_epo_fnames + eog_epo_fnames + ecg_epo_fnames,
            actions=['python 03_epochs.py %s' % subject],
            uptodate = [True],
        )
        
        
def task_ica():
    """Step 04: Use ICA to clean up EOG and ECG artifacts"""
    for subject in subjects:
        clean_epo_fnames = []
        dirty_epo_fnames = []
        filt_highpass_fnames = []
        for session in range(1,4):
            for run in range(1,4):
                clean_epo_fnames.append(fname.clean_epo(subject=subject, session=session, run=run))
                dirty_epo_fnames.append(fname.dirty_epo(subject=subject, session=session, run=run))
                filt_highpass_fnames.append(fname.filt_highpass(subject=subject, session=session, run=run))
        yield dict(
            name='%02d' % subject,
            #task_dep=['epochs'],
            #file_dep=filt_highpass_fnames + dirty_epo_fnames + ['04_ica.py'],
            targets=clean_epo_fnames,
            actions=['python 04_ica.py %s' % subject],
            uptodate = [True],
        )
        
def task_evoked():
    """Step 05: Get the evoked response"""
    for subject in subjects:
        if subject !=10:
            clean_epo_fnames = []
            ave_fnames = fname.ave(subject=subject)
            for session in range(1,4):
                for run in range(1,4):
                    clean_epo_fnames.append(fname.clean_epo(subject=subject, session=session, run=run))
                    
            yield dict(
                name='%02d' % subject,
                #task_dep=['ica'],
                file_dep= clean_epo_fnames + ['05_evokeds.py'],
                targets=[ave_fnames],
                actions=['python 05_evokeds.py %s' % subject],
                uptodate = [True],
            )

def task_matrix():
    """Step 06: Create matricies for decoding"""
    for subject in subjects:
        if subject != 10:
            ave_fnames = fname.ave(subject=subject)
            for modality in ['written', 'spoken', 'picture']:
                mat_fnames = fname.mat(subject=subject, modality=modality)
                yield dict(
                    name=f'{subject:02d}:{modality}',
                   # task_dep=['evoked'],
                   # file_dep= [ave_fnames] + ['06_matrix.py'],
                    targets=[mat_fnames],
                    actions=['python 06_matrix.py %s' % subject],
            )
            
            

def task_same_head():
    """Step 07: Bring evoked data to the same head position"""
    for subject in subjects:
        ave_fname = fname.ave(subject=subject)
        trans_ave_fname = fname.trans_ave(subject=subject)
        yield dict(
            name='%02d' % subject,
            file_dep= [ave_fname] + ['09_same_head.py'],
            targets=[trans_ave_fname],
            actions=['python 07_same_head.py %s' % subject]
        )
            
            
def task_grand_average():
    """Step 08: Get the grand averaged evoked response"""
    trans_ave_fnames = []
    for event_id in events_id:
        grand_ave_fname = fname.grand_ave(event_id=event_id)
        for subject in subjects:
            trans_ave_fnames.append(fname.trans_ave(subject=subject))
        yield dict(
                name=event_id,
                targets=[grand_ave_fname],
                actions=['python 08_grand_ave.py %s' % event_id]
            )
        
def task_grand_average_matrix():
    """Step 09: Create matricies for decoding"""
    grand_ave_fnames = []
    for event_id in events_id:
        grand_ave_fnames.append(fname.grand_ave(event_id=event_id))
    for modality in ['written', 'spoken', 'picture']:
        mat_fnames = fname.grand_ave_mat(modality=modality)
        yield dict(
            name=modality,
            targets=[mat_fnames],
            actions=['python 09_grand_ave_matrix.py'],
    )

 
