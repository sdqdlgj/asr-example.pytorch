#!/usr/bin/env python
# coding=utf-8
# wujian@17.10.10

import argparse
import numpy as np
import torch as th
import torch.nn as nn
import torch.utils.data as data

from data.seq_dataset import THCHS30
from model import RNN
from torch.autograd import Variable

import common
logger = common.get_logger()
# logger.info("Training RNNs")

# RNN config
hidden_size     = 512
hidden_layer    = 3
dropout         = 0.2

def cross_validate(epoch, nnet, test_loader, tot_frames):
    pos_frames = common.cross_validate(nnet, test_loader, is_rnn=True)
    logger.info('epoch {:2}: accracy = {:.4f}'.format(epoch + 1, pos_frames / tot_frames))

def train(args):
    common.make_dir(args.checkout_dir)
    # nnet 
    nnet = RNN((args.left_context + args.right_context + 1) * args.feat_dim, \
               hidden_layer, hidden_size, args.num_classes, dropout=dropout)
    print(nnet)
    nnet.cuda()

    criterion = nn.CrossEntropyLoss()
    optimizer = th.optim.Adam(nnet.parameters(), lr=args.learning_rate)

    train_dataset = THCHS30(root=args.data_dir, data_type='train')
    train_loader  = data.DataLoader(dataset=train_dataset, batch_size=args.min_batch,
                                    shuffle=True)

    test_dataset = THCHS30(root=args.data_dir, data_type='test')
    test_loader  = data.DataLoader(dataset=test_dataset, batch_size=args.min_batch,
                                    shuffle=True)
    
    cross_validate(-1, nnet, test_loader, test_dataset.num_frames)    
    for epoch in range(args.num_epochs):
        common.train_one_epoch(nnet, criterion, optimizer, train_loader, is_rnn=True)
        cross_validate(epoch, nnet, test_loader, test_dataset.num_frames)    
        th.save(nnet, common.join_path(args.checkout_dir, 'rnn.{}.pkl'.format(epoch + 1)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Trains a simple RNN acoustic model using CE loss function""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve',
        parents=[common.get_default_parser()])
    args = parser.parse_args()
    print(args)
    assert args.num_classes and args.feat_dim
    train(args)
