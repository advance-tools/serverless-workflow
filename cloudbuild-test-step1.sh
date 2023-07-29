service postgresql start &&

sudo -u postgres psql --command="create database testdb;" && \
sudo -u postgres psql --command="ALTER USER postgres PASSWORD 'advancedware'" && \

git config --global credential.helper 'store --file /workspace/git-credentials' && \
echo "https://${_GIT_USERNAME}:${_GIT_AUTH_TOKEN}@github.com" > /workspace/git-credentials && \

echo "${_GOOGLE_CREDENTIALS}" > /workspace/credentials.json && \

echo "DATABASE_URL=postgres://postgres:advancedware@localhost:5432/testdb
SECRET_KEY=${_BUILD_ID}
DEBUG=on
CURRENT_HOST=http://localhost:8006
EMAIL_HOST_USER=${_EMAIL_HOST_USER}
EMAIL_HOST_PASSWORD=${_EMAIL_HOST_PASSWORD}" > .env && \

cd /workspace && \
export PIPENV_VENV_IN_PROJECT=1 && \
pipenv uninstall querybuilder && \
pipenv install --ignore-pipfile --dev && \
pipenv install -e git+https://${_GIT_AUTH_TOKEN}@github.com/advance-tools/django-querybuilder.git#egg=querybuilder && \

cd /workspace/serverlessWorkflow && \
pipenv run python manage.py check && \
pipenv run python manage.py migrate --database=default && \
echo "Test REVERSE MIGRATION" && \
pipenv run python manage.py migrate task_services $(cat last_migration.txt) && \
echo "Re Migrate" && \
pipenv run python manage.py migrate --database=default