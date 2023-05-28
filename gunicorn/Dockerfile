FROM python:3.8-slim

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME /workspace
WORKDIR $APP_HOME

# Create and switch to a new user
# RUN useradd advancedware
# USER advancedware

COPY ./django-querybuilder /django-querybuilder
COPY ./requirements.txt .

RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Copy local code to the container image.
COPY ./serverlessWorkflow ./serverlessWorkflow/
# COPY ./static ./static/
COPY ./credentials.json .

ENV GOOGLE_APPLICATION_CREDENTIALS="/workspace/credentials.json"

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8000

WORKDIR ${APP_HOME}/serverlessWorkflow/

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 serverlessWorkflow.wsgi:application