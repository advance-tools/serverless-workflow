git config --global credential.helper 'store --file /workspace/git-credentials' && \
echo "https://${_GIT_USERNAME}:${_GIT_AUTH_TOKEN}@github.com" > /workspace/git-credentials && \

echo "${_GOOGLE_CREDENTIALS}" > /workspace/credentials.json && \

python3 -m pip install --upgrade pip && \
python3 -m pip install pipenv && \

cd /workspace && \
export PIPENV_VENV_IN_PROJECT=1 && \
pipenv uninstall querybuilder && \
pipenv install --ignore-pipfile --dev && \
pipenv install -e git+https://${_GIT_AUTH_TOKEN}@github.com/advance-tools/django-querybuilder.git#egg=querybuilder