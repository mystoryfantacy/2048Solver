
from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.merge import Add
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.optimizers import Adam
import keras.backend as K

from keras.utils import np_utils

import numpy as np
import pickle

class PolicyValueNet():
    def __init__(self, model_file = None):
        self.l2_const = 1e-4
        self.create_policy_value_net()
        self._loss_train_op()

        if model_file:
            net_params = pickle.load(open(model_file, 'rb'))
            self.model.set_weights(net_params)

    def create_policy_value_net(self):
        def CustomConv2D(filters, kernel_size):
            return Conv2D(filters=filters, kernel_size=kernel_size, padding="same",
                    data_format="channels_first", activation="relu",
                    kernel_regularizer=l2(self.l2_const))

        in_x = network = Input((1, 4, 4))
        network = CustomConv2D(32, (3, 3))(network)
        network = CustomConv2D(64, (3, 3))(network)
        network = CustomConv2D(128, (3, 3))(network)

        policy_net = CustomConv2D(4, (1,1))(network)
        policy_net = Flatten()(policy_net)
        self.policy_net = Dense(4, activation="softmax", kernel_regularizer=l2(self.l2_const))(policy_net)

        value_net = CustomConv2D(12, (1,1))(network)
        value_net = Flatten()(value_net)
        self.value_net = Dense(12, activation="softmax", kernel_regularizer=l2(self.l2_const))(policy_net)

        self.model = Model(in_x, [self.policy_net, self.value_net])

        #self.policy_value = self.model.predict
        self.predict = self.model.predict

    def _loss_train_op(self):

        opt = Adam()
        losses = ['categorical_crossentropy', 'categorical_crossentropy']
        self.model.compile(optimizer=opt, loss=losses)

        def train(state, probs, score_vec, lr):
            K.set_value(self.model.optimizer.lr, lr)
            self.model.fit(state, [probs, score_vec], batch_size = len(state), verbose = 0)

        self.train_step = train

    def get_policy_param(self):
        net_params = self.model.get_weights()
        return net_params

    def save_model(self, model_file):
        net_params = self.get_policy_param()
        pickle.dump(net_params, open(model_file, 'wb'), protocol=2)
