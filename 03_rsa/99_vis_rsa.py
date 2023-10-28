"""
Visualize RSA results.
"""
import mne
import numpy as np
import matplotlib.pyplot as plt
import scipy.io 
import sys
from config import fname
from mpl_toolkits.axes_grid1 import make_axes_locatable
import  matplotlib.font_manager
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42


#%%
levels = ['V1','V2','V4','IT','word2vec']

for level in levels:
    print(level)
    # load a sample rsa file 
    rsa_f = fname.rsa(subject=1,analysis_type="cumulative",
                      t=20,window_size=1)      
    stc = mne.read_source_estimate(rsa_f)
    
    # load rsa stats results
    results = scipy.io.loadmat(fname.rsa_stats_visual(analysis_type="cumulative",window_size=1,level=level))
    
    all_X = results['all_X']
    all_clusters = results['all_clusters']
    all_T = results['all_T']
    all_p = results['all_p']
    
    
    # decide on colorbar limits
    cb_max_l = []
    for i in range(1,len(all_X)):
        # get RSA values of the current time window
        X = all_X[i].mean(axis=0)
        cb_max_l.append(np.max(X))
    
    cb_max = np.round(np.max(cb_max_l),2)
    cb_min = 0
    cb_mean=cb_max-(cb_max-cb_min)/2
    
    
    def plot_rsa_results(current_clusters, sig_cluster_ids, stc=stc,subjects_dir=fname.freesurfer_dir):  
        # get the vertices of interest
        _,n_times, n_vertices = current_clusters.shape # (n_clusters, 1, 5124)
        current_clusters = current_clusters.reshape(-1,n_times*n_vertices)  
        vertices = np.where(current_clusters[sig_cluster_ids]!=0)[1]
        
        # create an empty array and populate with rsa values of significant vertices
        # use stc as a placeholder for temp
        temp = np.zeros((n_times, n_vertices))
        temp[:,vertices] = X[:,vertices]
        stc_sig = stc.copy()
        stc_sig._data = temp.T
        
        # visualize
        mne.viz.set_3d_backend('pyvista')
        brain = stc_sig.plot(subject='fsaverage-5.1.0', subjects_dir=subjects_dir,
                             cortex='bone', hemi = 'split',
                             background="white",spacing='ico4',
                             view_layout='vertical',
                             size=(800, 400),views=['lateral'],
                             colormap = "inferno",transparent=True,
                             clim=dict(kind='value',lims=[cb_min,cb_mean,cb_max]),
                             surface = 'pial',colorbar=False)
        
        # remove white space around the brain and return the figure
        screenshot = brain.screenshot()
        brain.close()   
        nonwhite_pix = (screenshot != 255).any(-1)
        nonwhite_row = nonwhite_pix.any(1)
        nonwhite_col = nonwhite_pix.any(0)
        cropped_screenshot = screenshot[nonwhite_row][:, nonwhite_col]
        return cropped_screenshot
    
    
    fig, axes =  plt.subplots(2, 4,figsize=[15,7.5])
    
    # loop from 4 to 49
    for idx, i in enumerate(range(4,33,4)):
        # get RSA values of the current time window
        X = all_X[i].mean(axis=0)
        # get RSA stats data
        current_clusters = all_clusters[0][i]
        sig_cluster_ids = np.where(all_p[0][i][0]<0.05)[0]
        # visualize current time winsow
        current_window_fig = plot_rsa_results(current_clusters,sig_cluster_ids)
        
        
        if (idx+1)<=4:
            row = 0
            column = idx
        else:
            row = 1
            column = idx-4
            
        print(row,column)
       
        axes[row,column].imshow(current_window_fig)
        axes[row,column].set_title('{}-{} ms'.format(0, (i+1)*20),fontsize=12,fontname = 'Arial')
        axes[row,column].axis('off')
        axes[row,column].aspect='equal'
    
    
    plt.subplots_adjust(bottom=0.3, top=0.7, hspace=0)
    f = fig
    cbar_ax = fig.add_axes([0.91, 0.35, 0.01, 0.3])
    clim = dict(kind='value',lims=[cb_min,cb_mean,cb_max])
    cbar = mne.viz.plot_brain_colorbar(cbar_ax, clim, colormap="inferno", label='RSA score')
    text = cbar_ax.yaxis.label
    font = matplotlib.font_manager.FontProperties(family='Arial', size=12)
    text.set_font_properties(font)
    cbar.ax.tick_params(labelsize=10) 
    
    f.show()
    
    
    f.savefig(f"RSA_corrmap_{level}.pdf",bbox_inches='tight',dpi=300)

#sliding
    # load a sample rsa file 
    rsa_f = fname.rsa(subject=1,analysis_type="sliding",
                      t=20,window_size=1)      
    stc = mne.read_source_estimate(rsa_f)
    
    # load rsa stats results
    results = scipy.io.loadmat(fname.rsa_stats_visual(analysis_type="sliding",window_size=1,level=level))
    
    all_X = results['all_X']
    all_clusters = results['all_clusters']
    all_T = results['all_T']
    all_p = results['all_p']
    
    # decide on colorbar limits
    cb_max_l = []
    for i in range(1,len(all_X)):
        # get RSA values of the current time window
        X = all_X[i].mean(axis=0)
        cb_max_l.append(np.max(X))
    
    cb_max_new = np.round(np.max(cb_max_l),2)
    cb_min_new = 0
    cb_mean_new=(cb_max-cb_min)/2
    
    # take cumulative cbmax, cb_mean
    
    fig, axes =  plt.subplots(2, 4,figsize=[15,7.5])
    
    # loop from 4 to 49
    for idx, i in enumerate(range(4,33,4)):
        # get RSA values of the current time window
        X = all_X[i].mean(axis=0)
        # get RSA stats data
        current_clusters = all_clusters[0][i]
        sig_cluster_ids = np.where(all_p[0][i][0]<0.05)[0]
        # visualize current time winsow
        current_window_fig = plot_rsa_results(current_clusters,sig_cluster_ids)
        
        
        if (idx+1)<=4:
            row = 0
            column = idx
        else:
            row = 1
            column = idx-4
            
        print(row,column)
       
        axes[row,column].imshow(current_window_fig)
        axes[row,column].set_title('{}-{} ms'.format(i*20, (i+1)*20),fontsize=12,fontname = 'Arial')
        axes[row,column].axis('off')
        axes[row,column].aspect='equal'
    
    
    plt.subplots_adjust(bottom=0.3, top=0.7, hspace=0)
    f = fig
    cbar_ax = fig.add_axes([0.91, 0.35, 0.01, 0.3])
    clim = dict(kind='value',lims=[cb_min,cb_mean,cb_max])
    cbar = mne.viz.plot_brain_colorbar(cbar_ax, clim, colormap="inferno", label='RSA score')
    text = cbar_ax.yaxis.label
    font = matplotlib.font_manager.FontProperties(family='Arial', size=12)
    text.set_font_properties(font)
    cbar.ax.tick_params(labelsize=10) 
    
    f.show()
    
    f.savefig(f"RSA_sliding_corrmap_{level}.pdf",bbox_inches='tight',dpi=300)
