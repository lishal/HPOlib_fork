#!/usr/bin/env python

##
# wrapping: A program making it easy to use hyperparameter
# optimization software.
# Copyright (C) 2013 Katharina Eggensperger and Matthias Feurer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from argparse import ArgumentParser

import cPickle
from importlib import import_module
import logging
import traceback
import os
import sys
from HPOlib.benchmark_util import get_openml_dataset
import optimizers.tpe.hyperopt_august2013_mod_src.hyperopt as hyperopt
import HPOlib.cv as cv
import numpy as np
from run_nvb import run_nvb

logger = logging.getLogger("HPOlib.optimizers.tpe.tpecall")

__authors__ = ["Katharina Eggensperger", "Matthias Feurer"]
__contact__ = "automl.org"

"""
def pyll_replace_list_with_dict(search_space, indent = 0):
    ""
    Recursively traverses a pyll search space and replaces pos_args nodes with
    dict nodes.
    ""

    # Convert to apply first. This makes sure every node of the search space is
    # an apply or literal node which makes it easier to traverse the tree
    if not isinstance(search_space, hyperopt.pyll.Apply):
        search_space = hyperopt.pyll.as_apply(search_space)

    if search_space.name == "pos_args":
        print " " * indent + search_space.name, search_space.__dict__
        param_dict = {}
        for pos_arg in search_space.pos_args:
            print " " * indent + pos_arg.name
            #param_dict["key"] = pos_arg
    for param in search_space.inputs():
        pyll_replace_list_with_dict(param, indent=indent+2)

    return search_space
"""


def main():
    prog = "python statistics.py WhatIsThis <manyPickles> WhatIsThis <manyPickles> [WhatIsThis <manyPickles>]"
    description = "Return some statistical information"

    parser = ArgumentParser(description=description, prog=prog)

    parser.add_argument("-p", "--space",
                        dest="spaceFile", help="Where is the space.py located?")
    parser.add_argument("-m", "--maxEvals",
                        dest="maxEvals", help="How many evaluations?")
    parser.add_argument("-s", "--seed", default="1",
                        dest="seed", type=int, help="Seed for the TPE algorithm")
    parser.add_argument("-r", "--restore", action="store_true",
                        dest="restore", help="When this flag is set state.pkl is restored in " +
                             "the current working directory")
    parser.add_argument("-fixB",type=int, help="Fix budget each round")
    parser.add_argument("--random", default=False, action="store_true",
                        dest="random", help="Use a random search")
    parser.add_argument("--cwd", help="Change the working directory before "
                                      "optimizing.")
    parser.add_argument("--tid", type=int, help="Which open_ml task id to use.")
    parser.add_argument("--datadir", help="Where to save the open ml data.")

    args, unknown = parser.parse_known_args()

    if args.cwd:
        os.chdir(args.cwd)

    if not os.path.exists(args.spaceFile):
        logger.critical("Search space not found: %s" % args.spaceFile)
        sys.exit(1)
    # First remove ".py"
    space, ext = os.path.splitext(os.path.basename(args.spaceFile))

    # Then load dict searchSpace and out function cv.py
    sys.path.append("./")
    sys.path.append("")

    module = import_module(space)
    search_space = module.space
    fn = cv.main  # doForTPE

    # Now run TPE, emulate fmin.fmin()
    state_filename = "state.pkl"
    if args.restore:
        # We do not need to care about the state of the trials object since it
        # is only serialized in a synchronized state, there will never be a save
        # with a running experiment
        fh = open(state_filename)
        tmp_dict = cPickle.load(fh)
        domain = tmp_dict['domain']
        trials = tmp_dict['trials']
        print trials.__dict__
    else:
        X,y = get_openml_dataset(args.tid, args.datadir)
        y = np.atleast_1d(y)
        if y.ndim == 1:
        # reshape is necessary to preserve the data contiguity against vs
        # [:, np.newaxis] that does not.
            y = np.reshape(y, (-1, 1))
        n_obs = y.shape[0]
        #should change to match SHA
        min_train_size = min(int(1./12.*n_obs),2000)
        #what to do if not all classes appear in training data
        #y_train=y[0:min_train_size]
        #while len(np.unique(y_train))<len(np.unique(y)):
            #min_train_size = min_train_size + int(0.1 * n_obs)
            #y_train=y[0:min_train_size]

        max_train_size=int(2./3.*n_obs)
        k = 0
        seed_and_arms = args.seed
        while True:
            if args.fixB:
                B=4*max_train_size
            else:
                B = int((2**k)*max_train_size)
            k+=1
            print "\nBudget B = %d" % B
            print "\nmin_train_size: " + str(min_train_size) + ", max_train_size: " + str(max_train_size)
            print '###################'
            try:
                num_pulls = int(max_train_size)
                num_arms = int(B/num_pulls)

                while num_pulls>=min_train_size:
                    if num_arms>2:
                        print "Starting num_pulls=%d, num_arms=%d" %(num_pulls,num_arms)
                        best_config = run_nvb(num_arms,num_pulls,fn,search_space,seed_and_arms,state_filename)
                        if num_pulls<max_train_size:
                            # run best_config on full sample size
                            fn(best_config)
                        seed_and_arms = seed_and_arms + num_arms
                    num_pulls = int(num_pulls/2)
                    num_arms = int(B/num_pulls)
            except Exception as e:
                print(traceback.format_exc())

if __name__ == "__main__":
    main()
