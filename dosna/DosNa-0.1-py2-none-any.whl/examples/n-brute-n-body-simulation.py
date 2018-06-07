#!/usr/bin/env python

from argparse import ArgumentParser

import numpy as np

# import dosna as dn

K = 6.67*1e-11
STEPS = 10
DELTATIME = 0.1
MAX_MASS = 10**24
MAX_POS, MAX_VEL = 100, 100
DIM = 2
BODIES = 3
PARTS = 2


def parse_args():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--bodies', '-b', type=int, default=1000)
    arg_parser.add_argument('--parts', '-p', type=int, default=1000)
    arg_parser.add_argumment('-k', type=float, default=10**6)
    arg_parser.add_argument('--steps', '-t', type=int, default=1000)
    arg_parser.add_argument('--deltatime', '-d', type=float, default=0.1)
    arg_parser.add_argument('--visualize', '-v', action="store_true",
                            default=False)
    arg_parser.add_argument('--engine', type=str, default="cpu")
    arg_parser.add_argument('--backend', type=str, default="backend")
    arg_parser.add_argument('--connection', type=str, default="dosna-con")
    arg_parser.add_argument('--connection-options', dest='connection_options',
                            nargs='+', default=[])
    return arg_parser.parse_args()


def parse_dosna_conection_options(connection, options):
    connection_config = {"name": connection}
    connection_config.update(dict(item.split('=')
                             for item in options))
    return connection_config


def generate_initial_data(total_parts, mass_range, x_range, y_range, vx_range,
                          vy_range):
    pass


def compute_gravity_forces(masses, rva_xy):
    f_xy = np.full(shape=(len(masses), 2))
    return f_xy

def compute_elastic_forces(masses, rva_xy):
    pass


def main():
    args = parse_args()
    # dn.use(engine=args.engine, backend=args.backend)
    # connection = dn.Connection(
    #     *parse_dosna_conection_options(args.connection,
    #                                    args.connection_options))
    data = np.full(shape=(args.bodies, args.parts, args.steps, 3, DIM),
                   fill_value=0)
    masses, rva_xy = generate_initial_data()
    # dataset = connection.create_dataset('b_p_t_rva_xy',
    #                                     shape=(args.bodies, args.parts, args.steps, 3, 2),
    #                                     chunk_size=(1, args.parts, 1, 3, 2))


if __name__ == "__main__":
    main()
