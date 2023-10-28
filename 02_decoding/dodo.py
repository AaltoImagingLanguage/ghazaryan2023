"""
Perform cross-validation of regression between brain response and feature vectors under different setups.
"""
import sys
sys.path.append('..')
from config import fname, subjects
from doit import get_var


DOIT_CONFIG = dict(verbosity=2, sort='definition')
tr = get_var("tr", -1)
cum = get_var("cum", -1)
tc = get_var("tc", -1)

def task_bsm():
    """Run zero-shot decoding"""
    for subject in subjects:
        for modality in ['picture']:
            input_fname = fname.mat(subject=subject, modality=modality)
            if tr != -1:
                output_fname = fname.bsm_tr(subject=subject, modality=modality,window=tr)
            elif cum != -1:
                output_fname = fname.bsm_cum(subject=subject, modality=modality)
            elif tc !=-1:
                    output_fname = fname.bsm_tc(subject=subject, modality=modality,window=tc)

            else:
                output_fname = fname.bsm(subject=subject, modality=modality)
            yield dict(
                name=f'{subject:02d}:{modality}',
                targets=[output_fname],
                actions=[f'''python brain_space_map_run.py {input_fname} -o {output_fname} -v -tr {tr} -cum {cum} -tc {tc} -i {subject}'''],
                )


def task_grand_average_bsm():
    """ Run zero-shot decoding on grand_averaged data"""
    for modality in ['picture']:
        input_fname = fname.grand_ave_mat(modality=modality)
        if tr != -1:
            output_fname = fname.bsm_grand_tr(modality=modality,window=tr)
        elif cum != -1:
            output_fname = fname.bsm_grand_cum(modality=modality)
        elif tc !=-1:
            output_fname = fname.bsm_grand_tc(modality=modality,window=tc)

        else:
            output_fname = fname.bsm_grand(modality=modality)
        yield dict(
            name=modality,
            targets=[output_fname],
            actions=[f'''python brain_space_map_run.py {input_fname} -o {output_fname} -v -tr {tr} -cum {cum} -tc {tc}'''],
            )

def task_bsm_run():
    """Run zero-shot decoding"""
    for subject in subjects:
        for vector in ['V1','V2','V4','IT','decoder','word2vec']:
            if vector != "word2vec":
                n = f'CORnet_vectors/CORnet_{vector}.mat'
                pca_f=f'CORnet_vectors/pca_cv/CORnet_{vector}_train.mat'

            else:
                n = 'target_vectors.mat'      
                pca_f='CORnet_vectors/pca_cv/word2vec_train.mat'

            for modality in ['picture']:
                input_fname = fname.mat(subject=subject, modality=modality)
                output_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                if tr != -1:
                    output_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                elif cum != -1:
                    output_fname = fname.bsm_cum_vis_mat(subject=subject, modality=modality,vector=vector)

                yield dict(
                    name=f'{subject:02d}:{modality}:{vector}',
                    targets=[output_fname],
                    actions=[f'''python brain_space_map_run.py {input_fname} -o {output_fname} -v -tr {tr} -cum {cum} -tc {tc} -i {subject} -n {n} -pca {pca_f}'''],
                    )    
                    
def task_bsm_results():
    """Run zero-shot decoding"""
    for subject in subjects:
        for vector in ['V1','V2','V4','IT','decoder','word2vec']:
            if vector != "word2vec":
                n = f'CORnet_vectors/CORnet_{vector}.mat'
                pca_f_test=f'CORnet_vectors/pca_cv/CORnet_{vector}_test.mat'

            else:
                n = 'target_vectors.mat'       
                pca_f_test='CORnet_vectors/pca_cv/word2vec_test.mat'

            for modality in ['picture']:
                input_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                input_fname2 = fname.mat(subject=subject, modality=modality)

                output_fname = fname.bsm_tr_vis_csv(subject=subject, modality=modality,window=tr,vector=vector)

                if tr != -1:
                    input_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                    output_fname = fname.bsm_tr_vis_csv(subject=subject, modality=modality,window=tr,vector=vector)
                    elif cum != -1:
                    input_fname = fname.bsm_cum_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                    output_fname = fname.bsm_cum_vis_csv(subject=subject, modality=modality,vector=vector)

                yield dict(
                    name=f'{subject:02d}:{modality}:{vector}',
                    targets=[output_fname],
                    actions=[f''' python brain_space_map_results.py {input_fname} -m {input_fname2} -o {output_fname} -n {n} -v -pca {pca_f_test} -d euclidean'''],
                    )   
                    

def task_bsm_run_perm():
    """Run zero-shot decoding with permutations for each subject"""
    for subject in subjects:
        for vector in ['V1','V2','V4','IT','decoder','word2vec']:
            if vector != "word2vec":
                n = f'CORnet_vectors/CORnet_{vector}.mat'
                pca_f=f'CORnet_vectors/pca_cv/CORnet_{vector}_train.mat'

            else:
                n = 'target_vectors.mat'      
                pca_f='CORnet_vectors/pca_cv/word2vec_train.mat'

            for perm in range(1000):
                for modality in ['picture']:
                    input_fname = fname.mat(subject=subject, modality=modality)
                    output_fname = fname.bsm_tr_vis_mat_perm(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
                    if tr != -1:
                        output_fname = fname.bsm_tr_vis_mat_perm(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
                    elif cum != -1:
                            output_fname = fname.bsm_cum_vis_mat(subject=subject, modality=modality,vector=vector,perm=perm)

                    yield dict(
                        name=f'{subject:02d}:{modality}:{vector}:{perm}',
                        targets=[output_fname],
                        actions=[f'''python brain_space_map_run.py {input_fname} -o {output_fname} -v -tr {tr} -cum {cum} -tc {tc} -i {subject} -n {n} -pca {pca_f} -p {perm}'''],
                        )    

def task_bsm_results_perm():
    """Run zero-shot decoding"""
    for subject in subjects:
        for vector in ['V1','V2','V4','IT','decoder','word2vec']:
            if vector != "word2vec":
                n = f'CORnet_vectors/CORnet_{vector}.mat'
                pca_f_test='CORnet_vectors/pca_cv/CORnet_{vector}_test.mat'

            else:
                n = 'target_vectors.mat'       
                pca_f_test='CORnet_vectors/pca_cv/word2vec_test.mat'

                for modality in ['picture']:
                    input_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector)
                    input_fname2 = fname.mat(subject=subject, modality=modality)
    
                    output_fname = fname.bsm_tr_vis_csv_perm(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
    
                    if tr != -1:
                        input_fname = fname.bsm_tr_vis_mat(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
                        output_fname = fname.bsm_tr_vis_csv(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
                    elif cum != -1:
                        input_fname = fname.bsm_cum_vis_mat(subject=subject, modality=modality,window=tr,vector=vector,perm=perm)
                        output_fname = fname.bsm_cum_vis_csv(subject=subject, modality=modality,vector=vector,perm=perm)

                    yield dict(
                        name=f'{subject:02d}:{modality}:{vector}:{perm}',
                        targets=[output_fname],
                        actions=[f''' python brain_space_map_results.py {input_fname} -m {input_fname2} -o {output_fname} -n {n} -v -pca {pca_f_test} -d euclidean'''],
                        )
