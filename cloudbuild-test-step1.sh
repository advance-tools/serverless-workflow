service postgresql start &&

sudo -u postgres psql --command="create database testdb;" && \
sudo -u postgres psql --command="ALTER USER postgres PASSWORD 'advancedware'" && \

git config --global credential.helper 'store --file /workspace/git-credentials' && \
echo "https://${_GIT_USERNAME}:${_GIT_AUTH_TOKEN}@github.com" > /workspace/git-credentials && \

echo "${_GOOGLE_CREDENTIALS}" > /workspace/credentials.json && \

echo "DATABASE_URL=postgres://postgres:advancedware@localhost:5432/testdb
SECRET_KEY=${_BUILD_ID}
DEBUG=on
CURRENT_HOST=https://8006.b4a38cb432e26a5e97be783ab28b237e.codespace.advancedware.in/
EMAIL_HOST_USER=noreply@advancedware.in
EMAIL_HOST_PASSWORD=bot@advancedware" > .env && \

cd / && \
git clone https://github.com/advance-tools/django-querybuilder.git && \

cd /workspace && \
pipenv uninstall querybuilder && \
pipenv install --ignore-pipfile --dev && \

pipenv install -e /django-querybuilder && \

mkdir /workspace/django-querybuilder && \
cp -r /django-querybuilder/* /workspace/django-querybuilder/ && \

cd /workspace/serverlessWorkflow && \
pipenv run python manage.py check && \
pipenv run python manage.py migrate --database=default && \
echo "Test REVERSE MIGRATION" && \
pipenv run python manage.py migrate task_services $(cat last_migration.txt) && \
echo "Re Migrate" && \
pipenv run python manage.py migrate --database=default