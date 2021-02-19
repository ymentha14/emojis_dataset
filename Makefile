.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = emojivec
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements:
	#$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
start_jupy:
	@jupyter lab --ip 0.0.0.0 --port 8888 --allow-root

dataset:
	@python3 src/analysis/postprocessing.py -v=0.8 -l=3

all_results:
	@python3 src/main.py

build_image:
	@docker build -t emoji_dataset .

run_container:
	@docker run -it \
	-e USER=$USER \
	-e REPO_DIR=/app \
	-v ${DATA_DIR}:/app/data \
	-v ${SRC_DIR}:/app/src \
	-v ${NOTEBOOKS_DIR}:/app/notebooks \
	-v ${WORD2VEC_DIR}:/app/emoji2vec/emoji2vec/data/word2vec \
	-v ${RESULTS_DIR}:/app/results \
	-v ${CREDS_DIR}:/app/creds \
	-v ${REPO_DIR}/emoji2vec:/app/emoji2vec \
	-p 8080:8080 \
	-p 8888:8888 \
	emoji_dataset


## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	black src
	flake8 src
