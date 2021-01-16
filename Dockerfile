ARG BASE_CONTAINER=ucsdets/datascience-notebook:2020.2-stable
FROM $BASE_CONTAINER
LABEL maintainer="UC San Diego ITS/ETS <ets-consult@ucsd.edu"
USER root
RUN pip install --no-cache-dir seaborn twarc tweepy python-dotenv
COPY /run_jupyter.sh /
RUN chmod 755 /run_jupyter.sh
USER $NB_UID