import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# Model 1: Temporal convolution + lstm + feature fusion, for arousal classification

class model(nn.Module):
	
	def __init__(self):

		super(model, self).__init__()

		self.features_eeg = nn.Sequential(
			nn.Conv1d(32, 48, kernel_size = 128),		# 384 - 128 + 1 = 257
			nn.BatchNorm1d(48),
			nn.ReLU(),
			nn.Conv1d(48, 64, kernel_size = 128),		# 257 - 128 + 1 = 130
			nn.BatchNorm1d(64),
			nn.ReLU(),
			nn.Conv1d(64, 64, kernel_size = 64),		# 130 - 64 + 1 = 67
			nn.BatchNorm1d(64),
			nn.ReLU(),
			nn.Conv1d(64, 128, kernel_size = 16),		# 67 - 16 + 1 = 52
			nn.BatchNorm1d(128),
			nn.ReLU(),
			nn.Conv1d(128, 128, kernel_size = 16),		# 52 - 16 + 1 = 37
			nn.BatchNorm1d(128),
			nn.ReLU(),
			nn.Conv1d(128, 256, kernel_size = 16),		# 37 - 16 + 1 = 22
			nn.BatchNorm1d(256),
			nn.ReLU(),
			nn.Conv1d(256, 256, kernel_size = 8),		# 22 - 8 + 1 = 15
			nn.BatchNorm1d(256),
			nn.ReLU(),
			nn.Conv1d(256, 256, kernel_size = 8),		# 15 - 8 + 1 = 8
			nn.BatchNorm1d(256),
			nn.ReLU())

		self.features_eeg_flatten = nn.Sequential(			
			nn.Linear(256*8, 1024),
			nn.BatchNorm1d(1024),
			nn.ReLU(),
			nn.Linear(1024, 512),
			nn.BatchNorm1d(512),
			nn.ReLU(),			
			nn.Linear(512, 128))				# Representation to be concatenated
		
		self.features_others = nn.Sequential(
			nn.Conv1d(2, 16, kernel_size = 128),	# 384 - 192 + 1 = 257
			nn.BatchNorm1d(16),
			nn.ReLU(),			
			nn.Conv1d(16, 32, kernel_size = 128),	# 257 - 128 + 1 = 130
			nn.BatchNorm1d(32),
			nn.ReLU(),			
			nn.Conv1d(32, 64, kernel_size = 64),	# 130 - 64 + 1 = 67
			nn.BatchNorm1d(64),
			nn.ReLU(),
			nn.Conv1d(64, 64, kernel_size = 32),	# 67 - 32 + 1 = 34
			nn.BatchNorm1d(64),
			nn.ReLU(),
			nn.Conv1d(64, 128, kernel_size = 16),	# 34 - 16 + 1 = 17
			nn.BatchNorm1d(128),
			nn.ReLU(),
			nn.Conv1d(128, 128, kernel_size = 8),	# 17 - 8 + 1 = 10
			nn.BatchNorm1d(128),
			nn.ReLU())

		self.features_others_flatten = nn.Sequential(			
			nn.Linear(128*10, 512),
			nn.BatchNorm1d(512),
			nn.ReLU(),			
			nn.Linear(512, 128))				# Representation to be concatenated

		self.n_hidden_layers = 1
		self.hidden_size = 64
		self.lstm = nn.LSTM(128 + 128, self.hidden_size, self.n_hidden_layers, bidirectional = False)
		self.fc_lstm = nn.Linear(self.hidden_size*2, 8)

		# Output layer
		self.fc_out = nn.Linear(8, 1)
			

	def forward(self, x):

		mini_batch_size = x.size(0)
		seq_length = x.size(1)
	
		x_eeg = x[:, 0:32, :]

		x_eeg = x_eeg.view(mini_batch_size, seq_length, x_eeg.size(-2), x_eeg.size(-1))

		x_gsr = x[:, 36, :]
		x_temp = x[:, 39, :]

		x_gsr = x_gsr.contiguous()
		x_temp = x_temp.contiguous()
		x_gsr = x_gsr.view(x_gsr.size()[0], 1,  x_gsr.size()[1])
		x_temp = x_temp.view(x_temp.size()[0], 1,  x_temp.size()[1])
		x_others = torch.cat([x_temp, x_gsr], 1)
		x_others = x_others.view(mini_batch_size, seq_length, x_others.size(-2), x_others.size(-1))

		#EEG
		x_eeg = self.features_eeg(x_eeg)
		x_eeg = x_eeg.view(x_eeg.size(0), -1)
		x_eeg = self.features_eeg_flatten(x_eeg)

		#Skin temp and GSR
		x_others  = self.features_others(x_others)
		x_others = x_others.view(x_others.size(0), -1)
		x_others = self.features_others_flatten(x_others)
		
		concatenated_output = torch.cat([x_eeg, x_others], 1)

		# Reshape lstm input 
		concatenated_output.view(seq_length, mini_batch_size, concatenated_output.size(-1))

		# Initial hidden states
		h0 = Variable(torch.zeros(self.n_hidden_layers*2, concatenated_output.size(1), self.hidden_size))  
		c0 = Variable(torch.zeros(self.n_hidden_layers*2, concatenated_output.size(1), self.hidden_size))

		if self.is_cuda():
			h0 = h0.cuda()
			c0 = c0.cuda()	

		seq_out, _ = self.lstm(concatenated_output, (h0, c0))

		output = self.fc_lstm(seq_out)
		output = F.relu(concatenated_output)
		output = F.softmax(self.fc_out(output), 0)

		return output
	
		

		