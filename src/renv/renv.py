#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Author: Andreas Herten, JSC, Forschungszentrum Jülich

import sys
import argparse
import os

def cli():
    epilog_raw=r"""
    Examples:
      Set environment variable ABC to 0 for task 0 and 1 for task 1:
      $ srun -n 2 renv ABC env | grep ABC
      ABC=1
      ABC=2

      Set environment variable CUDA_VIS to 3 for rank 0 and 2 for rank 1:
      $ srun -n 2 renv --map '0:3,1:2' CUDA_VIS env | grep CUDA_VIS

      Combine both examples by stacking renv:
      $ srun -n 1 renv ABC renv --map '0:2,1:2' CUDA_VIS env | grep 'CUDA_VIS\\|ABC'
      """
    parser = argparse.ArgumentParser(
        description="renv: Set environment variables specific to MPI rank.",
        epilog=epilog_raw,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("ENVVAR", type=str, nargs=1, help="Environment variable to set")
    parser.add_argument(
        "-g",
        "--global",
        dest="glob",
        action="store_true",
        help="Use global rank indices; default: node-local indices",
    )
    parser.add_argument(
        "-s",
        "--source",
        choices=["slurm", "mpi", "pmi"],
        help=argparse.SUPPRESS,
        default="slurm",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing env var"
    )
    parser.add_argument(
        "--separator-map", type=str, default=os.environ.get("RENV_SEPARATOR_MAP", ","), help="Separator for individual map entries; overwrite globally with RENV_SEPARATOR_MAP"
    )
    parser.add_argument(
        "--separator-keyval", type=str, default=os.environ.get("RENV_SEPARATOR_KEYVAL", ":"), help="Separator for key-value-pairs (key<sep>val) in the map entries; overwrite globally with RENV_SEPARATOR_KEYVAL"
    )
    parser.add_argument(
        "-m",
        "--map",
        type=str,
        help='dict-like string to map task IDs to values; example: --map "1: ABC, 2: DEF"',
    )
    parser.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command to run under new environment; renv can be stacked",
    )

    args = parser.parse_args()
    main(args)

def main(args):
    env = os.environ.copy()

    rank_env_vars = {"slurm": {"global": "SLURM_PROCID", "local": "SLURM_LOCALID"}}

    if args.glob is True:
        lookup_str = rank_env_vars[args.source]["global"]
    else:
        lookup_str = rank_env_vars[args.source]["local"]

    if lookup_str not in env:
        print(f"No MPI environment, {lookup_str} not found")
        raise SystemExit(1)

    # Parse map, if it exists
    if args.map is not None:
        task_map = {}
        # parse map and remove quotes around values
        _task_map = args.map.split(args.separator_map)
        for keyval in _task_map:
            _keyval = keyval.split(args.separator_keyval)
            key = _keyval[0]
            value = _keyval[1].strip().strip("\"'")
            task_map[key] = value

    env_var = args.ENVVAR[0]

    # Check if env var is already defined
    if env_var in env and not args.force:
        print(f"{env_var} is already defined; fix or launch with --force")
        raise SystemExit(1)

    # Apply map, if it exists
    if args.map is not None:
        if env[lookup_str] in task_map:
            env[env_var] = task_map[env[lookup_str]]
    else:
        env[env_var] = env[lookup_str]

    # Replace current process by env-fixed process, if cmd exists
    if args.cmd is not None:
        sys.stdout.flush()
        sys.stderr.flush()
        os.execvpe(args.cmd[0], args.cmd, env)


if __name__ == "__main__":
    cli()
