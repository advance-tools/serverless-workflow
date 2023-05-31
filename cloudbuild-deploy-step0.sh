git config --global credential.helper 'store --file /workspace/git-credentials' && \
echo "https://${_GIT_USERNAME}:${_GIT_AUTH_TOKEN}@github.com" > /workspace/git-credentials && \

echo "${_GOOGLE_CREDENTIALS}" > /workspace/credentials.json && \

python3 -m pip install --upgrade pip && \
python3 -m pip install pipenv && \

cd / && \
git clone https://github.com/advance-tools/django-querybuilder.git && \
cd /workspace && \
pipenv uninstall querybuilder && \
pipenv install --ignore-pipfile --deploy && \
pipenv install -e /django-querybuilder && \
mkdir /workspace/django-querybuilder && \
cp -r /django-querybuilder/* /workspace/django-querybuilder/ && \

cd /workspace/serverlessWorkflow && \
pipenv requirements > /workspace/requirements.txt