#!/bin/bash
#SBATCH --account=rrg-bengioy-ad    # Yoshua pays for your job
#SBATCH --gres=gpu:1                    # Request GPU "generic resources"
#SBATCH --cpus-per-task=2               # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=15G                       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=48:00:00                 # The job will run for 24 hours max
#SBATCH --output /scratch/ostapeno/output/SSCL/slurm_out.out  # Write stdout in $SCRATCH
#SBATCH --error  /scratch/ostapeno/output/SSCL/slurm_out.err  # Write stderr in $SCRATCH



source ~/ENVS/SSCl/bin/activate
export  WANDB_API_KEY=174b08e7eb88b0c57624f63c9590418be3bc4607

mkdir $SLURM_TMPDIR/SSCL
mkdir $SLURM_TMPDIR/SSCL/wandb
export WANDB_MODE=dryrun
module load httpproxy
export WANDB_DIR=$SLURM_TMPDIR/SSCL/wandb/
mkdir $SLURM_TMPDIR/data
cd /home/ostapeno/projects/rrg-bengioy-ad/ostapeno/dev/SSCL/
wandb off

function cleanup(){
    echo "Cleaning up and transfering files from $SLURM_TMPDIR to $SCRATCH/SSCL"
    cp -r $SLURM_TMPDIR/SSCL/* $SCRATCH/SSCL/
    ##wandb sync $SCRATCH/SSCL/wandb/ # Not guaranteed to work given CC's network restrictions.
}

trap cleanup EXIT
echo "Calling python -u main.py task-incremental \
    --data_dir $SLURM_TMPDIR/data \
    --log_dir_root $SLURM_TMPDIR/results \
    --run_number ${SLURM_ARRAY_TASK_ID:-0} \
    '${@:1}'"

python -u main.py task-incremental-semi-sup \
    --data_dir /home/ostapeno/projects/rrg-bengioy-ad/ostapeno/dev/SSCL/data \
    --log_dir_root $SLURM_TMPDIR/SSCL \
    --run_number ${SLURM_ARRAY_TASK_ID:-0} \
    "${@:1}"

exit
