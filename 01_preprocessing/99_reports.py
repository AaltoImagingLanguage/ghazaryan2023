"""
Generate an HTML report with quality control figures.
"""
import sys
sys.path.append('..')
import argparse
import mne
from mne.preprocessing import read_ica
from config import fname

# Be verbose
mne.set_log_level('INFO')

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

for session in range(1, 4):
    for run in range(1, 4):
        tsss = mne.io.read_raw_fif(fname.tsss(subject=subject, run=run, session=session))
        lowpass = mne.io.read_raw_fif(fname.filt_lowpass(subject=subject, run=run, session=session))
 
        ica = read_ica(fname.ica(subject=subject, session=session, run=run))
        eog_epochs = mne.read_epochs(fname.eog_epo(subject=subject, session=session, run=run))  
        eog_inds, eog_scores = ica.find_bads_eog(eog_epochs)

        components = ica.plot_components(show=False)

        dirty_epochs = mne.read_epochs(fname.dirty_epo(subject=subject, session=session, run=run))
        clean_epochs = mne.read_epochs(fname.clean_epo(subject=subject, session=session, run=run))
        properties = ica.plot_properties(dirty_epochs, picks=eog_inds, psd_args={'fmax': 35.},
                                         image_args={'sigma': 1.}, show=False)
        
        subject_info = 'session-' + str(session) + '_run-' + str(run)
        
        # add plots to report
        with mne.open_report(fname.report(subject=subject)) as report:
            report.add_figs_to_section(
                [tsss.plot_psd(show=False)],
                ['PSD before filtering'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [lowpass.plot_psd(show=False)],
                ['PSD after filtering'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_slider_to_section(
                components,
                ['ICA components %d' % i for i in range(len(components))],
                title='ICA components',
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [ica.plot_scores(eog_scores, show=False)],
                ['Component correlation with EOG'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [ica.plot_sources(eog_epochs.average(), exclude=eog_inds,show=False)],
                ['Excluded eog components with respect to eog average'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_slider_to_section(
                properties,
                ['Properties of excluded ICA components %d' % i for i in range(len(properties))],
                title ='ICA excluded components',
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [ica.plot_overlay(eog_epochs.average(), exclude=eog_inds, show=False)],
                ['Eog epochs before and after excluding components'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [dirty_epochs.average().plot(picks = 'grad',spatial_colors=True)],
                ['Dirty evoked'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
            report.add_figs_to_section(
                [clean_epochs.average().plot(picks = 'grad',spatial_colors=True)],
                ['Clean evoked'],
                section = 'Sensor-level ' + subject_info,
                replace = True)
            
        report.save(fname.report_html(subject=subject), overwrite=True, open_browser=False)
