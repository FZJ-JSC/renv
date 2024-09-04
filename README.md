# `renv`: Rank-aware `env`

[![DOI](https://zenodo.org/badge/514209943.svg)](https://zenodo.org/badge/latestdoi/514209943)

`renv` changes an environment variable according to the MPI rank / task ID of the process as a prefix to your application.

Say goodbye to your complicated Bash wrapper scripts!

## Usage

Just insert `renv` in the command line before your application, giving the environment variable to change as the single, first argument. Similar to `env` or `xenv`:

```bash
srun -n 2 renv MYVAR ./myapp -a 1
```

This will set MYVAR to 0 for task 0 and 1 for task 1.

### Installation

The program can be installed through pip:

```bash
python3 -m pip install git+https://github.com/FZJ-JSC/renv
```

### Interface

* `-h`: Print help
* `-g`, `--global`: Use global task IDs and not node-local task IDs (i.e. `SLURM_PROCID` instead of `SLURM_LOCALID`)
* `-f`, `--force`: Allow overwrite a pre-existing environment variable
* `-m`, `--map`: Don't simply set the task ID to the environment variable, but first replace it according to a map; i.e. `--map '0: 2'` would set the environment variable for task 0 to 2, and not to 0
* `--separator-map`, `--separator-keyval`: Change the separator for parsing the map and the key-val-pairs, respectively. Default are `,` for entries in the map and `:` to separate keys and values. Use `RENV_SEPARATOR_MAP` and `RENV_SEPARATOR_KEYVAL` to override the behavior globally (the command line option takes precedence, though).

Right now, only Slurm is supported; but other schedulers are prepared. Please file an issue.

## Examples

* Simple usage:
    
    ```shell
    $ srun -n 2 renv ABC env | grep ABC
    ABC=1
    ABC=2
    ```
* Set environment variable CUDA_VISIBLE_DEVICES to 3 for rank 0 and 2 for rank 1:

    ```shell
    $ srun -n 2 renv --map '0:3,1:2' CUDA_VISIBLE_DEVICES env | grep CUDA_VISIBLE_DEVICES
    ```
* Combine both examples by stacking renv:

    ```shell
    $ srun -n 1 renv ABC renv --map '0:2,1:2' CUDA_VISIBLE_DEVICES env | grep "CUDA_VISIBLE_DEVICES\|ABC"
    ```
* Combine with env:

    ```shell
    $ srun -n 1 env ABC=DEF CUDA_VISIBLE_DEVICES=0 renv --map '1:3,2:2' CUDA_VISIBLE_DEVICES env | grep "CUDA_VISIBLE_DEVICES\|ABC"
    ```
