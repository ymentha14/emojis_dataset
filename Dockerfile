FROM python:3.6.9
COPY ./ ./app
WORKDIR ./app
RUN apt-get update && \
    apt-get -y install curl && \
    apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates && \
    curl -sL https://deb.nodesource.com/setup_12.x | bash && \
    apt-get -y install nodejs

RUN apt-get -y install make

RUN python3 -m venv env
# Install dependencies:
RUN . env/bin/activate
RUN git clone https://github.com/ymentha14/emoji2vec.git emoji2vec/emoji2vec

RUN pip install -r requirements.txt
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager
CMD [ "/bin/bash" ]
