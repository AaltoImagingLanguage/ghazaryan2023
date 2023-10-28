#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from config import fname,subjects,triggers
from doit import get_var


DOIT_CONFIG = dict(verbosity=2, sort='definition')
sl = get_var("sl", -1)
cum = get_var("cum", -1)

def task_src_bem():
    """Step 02: compute surface-based source space"""
    for subject in subjects:
        trans_tsss = fname.tsss(subject=subject, session=2, run=2)
        src_bem = [fname.src(subject=subject)+fname.bem(subject=subject)]
        yield dict(
            name='%02d' % subject,
            file_dep=[trans_tsss] + ['02_src_bem.py'],
            targets=src_bem,
            actions=['python 02_src_bem.py %s' % subject],
           # uptodate = [True],
        )
        
def task_fwd_inv():
    """Step 03: compute forward model and inverse solution"""
    for subject in subjects:
        src_bem = [fname.src(subject=subject)+fname.bem(subject=subject)]
        epochs = [fname.epochs_all(subject=subject)]
        output = [fname.fwd(subject=subject), fname.noise_cov(subject=subject),fname.inv(subject=subject)]
        yield dict(
            name='%02d' % subject,
            #task_dep = ['src_bem'],
            file_dep= src_bem + epochs + ['03_forward.py'],
            targets = output,
            actions=['python 03_forward.py %s' % subject],
        )

def task_stc():
    """Step 04: Obtain source time courses"""
    for subject in subjects:
        epochs = [fname.epochs_all(subject=subject)]
        inv = [fname.inv(subject=subject)]
        avg_f = [fname.all_items_stc(subject=subject), fname.all_items_stc_morphed(subject=subject)]
        pic_items = [i.strip()[:-3] for i in triggers['finnish'] if "pic" in i]
        item_f = []
        for i in pic_items:
            item_f += [fname.indiv_item_stc(item=i,subject=subject), 
                       fname.indiv_item_stc_morphed(item=i,subject=subject)]            
        yield dict(
            name='%02d' % subject,
            #task_dep = ['fwd_inv'],
            file_dep= epochs + inv + ['04_stc.py'],
            targets = avg_f + item_f,
            actions=['python 04_stc.py %s' % subject],
        )

def task_rsa():
    """Step 05: Run RSA"""
    for subject in subjects:
        pic_items = [i.strip()[:-3] for i in triggers['finnish'] if "pic" in i]
        item_f = []
        for i in pic_items:
            item_f += [fname.indiv_item_stc(item=i,subject=subject), 
                       fname.indiv_item_stc_morphed(item=i,subject=subject)] 
        if sl != -1:
            output_fname = []
            for t in range(0, 1000, 20*int(sl)):
                output_fname.append(fname.rsa(subject=subject,analysis_type="sliding",
                                         window_size=sl, t=t))
        if cum != -1:
            output_fname = []
            for t in range(0, 1000, 20*int(cum)):
                output_fname.append(fname.rsa(subject=subject,analysis_type="cumulative",
                                         window_size=cum, t=t))
        else:
            output_fname = [fname.rsa(subject=subject,analysis_type="full",
                              t=1000,window_size=1000)]
        yield dict(
                name=f'{subject:02d}',
                targets=output_fname,
                actions=[f'''python 05_rsa.py {subject} -cum {cum} -sl {sl}'''],
	)
