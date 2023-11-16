#!/bin/bash
# This script will be run when the container starts to create the conda environment from an environment.yml file

# Split the dependencies on commas, which we'll use as a delimiter
IFS=',' read -ra DEPS <<< "$PROJECT_DEPENDENCIES"

# Create the environment.yml file
echo "name: myenv" > environment.yml
echo "dependencies:" >> environment.yml
for dep in "${DEPS[@]}"; do
  echo "  - $dep" >> environment.yml
done

# Create the conda environment using the environment.yml file
mamba env create -f environment.yml

# Activate the environment
source activate myenv

# Keep the container running
# tail -f /dev/null

jupyter server --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password='' --allow-root
