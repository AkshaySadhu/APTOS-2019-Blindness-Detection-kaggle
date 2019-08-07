from model import MainModel
from torch import optim
import torch.nn as nn
import os
from logger import Logger
from libs.earlystopping import EarlyStopping

import torch, random
import numpy as np

def seed_torch(seed=13):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed) # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


class Config:
    def __init__(self, batch_size=32, lr=0.00015, p_horizontalflip=0.4):
        ## INFO ABOUT EXPERIMENT
        self.logsFileName = 'LOGS'
        self.seed = 13

        seed_torch(self.seed)

        if os.path.exists('./Logs/' + self.logsFileName + '.csv'):
            self.df_logger = Logger(self.logsFileName + '.csv', 'df')
            self.experiment_name = 'exp{}'.format(len(self.df_logger.logsFile)) + '_end_epoch'
        else:
            self.experiment_name = 'exp{}'.format(0) + '_end_epoch'
        self.data_type = 'new_comp_quadratic_kappa'

        self.img_size = 256

        ## MODEL PARAMETERS
        self.weights_dir = './Model_weights/'
        self.model_type = 'ResNet101'

        self.model = MainModel(model_type=self.model_type).get_model()
        if self.model_type == 'ResNext101_32x16d':
            for param in self.model.parameters():
                param.requires_grad = False
            self.model.fc = torch.nn.Linear(2048, 1)

        self.pytorch_total_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        self.lr = lr
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.scheduler = None
        self.criterion = nn.MSELoss()
        self.model_param_list = [self.model, self.optimizer, self.scheduler]

        ## EARLY STOPPING
        self.early_stopping_patience = 8
        self.early_stopping = EarlyStopping(self.early_stopping_patience)
        self.early_stopping_loss = "pytorch" #kappa

        ## TRAINING & VALIDATION SETUP
        self.num_workers = 16
        self.n_epochs = 50
        self.batch_size = batch_size
        self.valid_type = 'HoldOut' #CV
        self.valid_size = 0.2
        self.n_folds = 5 ## for CV!



        ## TRANSFORMER AND DATASET
        self.p_horizontalflip = p_horizontalflip

        ## PRINT FREQUENCY
        self.print_frequency = 25
