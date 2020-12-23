FROM python:3.8
COPY ./ ./app
WORKDIR ./app

RUN python3 -m venv env
# Install dependencies:
RUN . env/bin/activate
RUN git clone https://github.com/ymentha14/emoji2vec.git emoji2vec/emoji2vec

RUN pip install -r requirements.txt
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager
CMD [ "/bin/bash" ]



