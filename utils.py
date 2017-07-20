import numpy as np
import cPickle
import os, sys
import h5py


def load_dataset_per_subject(sub = 1, main_dir = 'data_preprocessed_python/'):

	if (sub < 10):
		sub_code = str('s0' + str(sub) + '.dat')
	else:
		sub_code = str('s' + str(sub) + '.dat')	

	subject_path = os.path.join(main_dir, sub_code)
	subject = cPickle.load(open(subject_path, 'rb'))
	labels = subject['labels']
	data = subject['data']
		
	return data, labels


def split_data_per_subject(sub = 1, segment_duration = 1, sampling_rate = 128, main_dir = 'data_preprocessed_python/'):
	
	data, labels = load_dataset_per_subject(sub, main_dir)
	number_of_samples = segment_duration*sampling_rate
	number_of_trials = data.shape[0]
	number_of_segments = data.shape[2]/number_of_samples

	number_of_final_examples = number_of_trials*number_of_segments

	final_data = []
	final_labels = []

	for trial in xrange(0, number_of_trials):

		data_to_split = data[trial, :, :]
		data_to_split = np.reshape(data_to_split, (number_of_segments, data.shape[1], number_of_samples))
		final_data.append(data_to_split)

		label_to_repeat = labels[trial, :]
		label_repeated = np.tile(label_to_repeat, (number_of_segments, 1))
		final_labels.append(label_repeated)

	final_data_out = np.reshape(np.asarray(final_data), (number_of_final_examples, data.shape[1], number_of_samples))
	final_labels_out = np.reshape(np.asarray(final_labels), (number_of_final_examples, labels.shape[1]))


	return final_data_out, final_labels_out


def create_hdf(subjects_number = 32, hdf_filename = 'DEAP_dataset_subjects_list.hdf'):

	complete_data = []
	complete_labels = []

	for sub in xrange(1, subjects_number+1):

		data_sub, labels_sub = split_data_per_subject(sub)
		complete_data.append(data_sub)
		complete_labels.append(labels_sub)

	complete_data = np.asarray(complete_data)
	complete_labels = np.asarray(complete_labels)	

	complete_dataset_file = h5py.File(hdf_filename, 'w')
	complete_dataset = complete_dataset_file.create_dataset('data', data = complete_data)
	complete_dataset = complete_dataset_file.create_dataset('labels', data = complete_labels)
	complete_dataset_file.close()


def merge_all_subjects_store_as_hdf(hdf_filename_to_read = 'DEAP_dataset_subjects_list.hdf', hdf_filename_to_save = 'DEAP_dataset.hdf'):

	data, labels = read_hdf(hdf_filename_to_read)
	
	data_new = np.reshape(data, (data.shape[0]*data.shape[1], data.shape[2], data.shape[3]))
	labels_new = np.reshape(labels, (labels.shape[0]*labels.shape[1], labels.shape[2]))

	complete_dataset_file = h5py.File(hdf_filename_to_save, 'w')
	complete_dataset = complete_dataset_file.create_dataset('data', data = data_new)
	complete_dataset = complete_dataset_file.create_dataset('labels', data = labels_new)
	complete_dataset_file.close()


def merge_all_subjects_norm_split_store_as_hdf(hdf_filename_to_read = 'DEAP_dataset_subjects_list.hdf', hdf_filename_to_save = 'DEAP_dataset.hdf'):

	data, labels = read_hdf(hdf_filename_to_read)
	
	data = np.reshape(data, (data.shape[0]*data.shape[1], data.shape[2], data.shape[3]))
	labels = np.reshape(labels, (labels.shape[0]*labels.shape[1], labels.shape[2]))

	max_val_0 = np.max(labels[:, 0])
	min_val_0 = np.min(labels[:, 0])
	labels[:, 0] = (labels[:, 0] - min_val_0)/(max_val_0 - min_val_0)

	max_val_1 = np.max(labels[:, 1])
	min_val_1 = np.min(labels[:, 1])
	labels[:, 1] = (labels[:, 1] - min_val_1)/(max_val_1 - min_val_1)

	max_val_2 = np.max(labels[:, 2])
	min_val_2 = np.min(labels[:, 2])
	labels[:, 2] = (labels[:, 2] - min_val_2)/(max_val_2 - min_val_2)
	
	max_val_3 = np.max(labels[:, 3])
	min_val_3 = np.min(labels[:, 3])
	labels[:, 3] = (labels[:, 3] - min_val_3)/(max_val_3 - min_val_3)

	data_eeg = data[:, 0:32, :]
	data_eog = data[:, 32:34, :]
	data_emg = data[:, 34:36, :]
	data_gsr = data[:, 36, :]
	data_resp = data[:, 37, :]
	data_plet = data[:, 38, :]
	data_temp = data[:, 39, :]

	complete_dataset_file = h5py.File(hdf_filename_to_save, 'w')
	complete_dataset = complete_dataset_file.create_dataset('eeg', data = data_eeg)
	complete_dataset = complete_dataset_file.create_dataset('eog', data = data_eog)
	complete_dataset = complete_dataset_file.create_dataset('emg', data = data_emg)
	complete_dataset = complete_dataset_file.create_dataset('gsr', data = data_gsr)
	complete_dataset = complete_dataset_file.create_dataset('resp', data = data_resp)
	complete_dataset = complete_dataset_file.create_dataset('plet', data = data_plet)
	complete_dataset = complete_dataset_file.create_dataset('temp', data = data_temp)
	complete_dataset = complete_dataset_file.create_dataset('labels', data = labels)
	complete_dataset_file.close()


def read_hdf(hdf_filename = 'DEAP_dataset_subjects_list.hdf'):

	open_file = h5py.File(hdf_filename, 'r')
	
	data = open_file['data']
	labels = open_file['labels']

	return data, labels

def read_split_data_hdf(hdf_filename = 'DEAP_dataset.hdf'):

	open_file = h5py.File(hdf_filename, 'r')
	
	data_eeg = open_file['eeg']
	data_eog = open_file['eog']
	data_emg = open_file['emg']
	data_gsr = open_file['gsr']
	data_resp = open_file['resp']
	data_plet = open_file['plet']
	data_temp = open_file['temp']
	labels = open_file['labels']

	return data_eeg, data_eog, data_emg, data_gsr, data_resp, data_plet, data_temp, labels	


if __name__ == '__main__':

	create_hdf(32)
	merge_all_subjects_norm_split_store_as_hdf()

	#data_eeg, data_eog, data_emg, data_gsr, data_resp, data_plet, data_temp, labels = read_split_data_hdf() 