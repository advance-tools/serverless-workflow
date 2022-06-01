Bump to next version by running **`pipenv run pysemver nextver $(cat version) major/minor/patch/prerelease/build > version`**

Process of Create a Pull-Request:
1) Create a branch for the current Back-Log. e.g. **`git checkout -b current-branch-name`**. This will create branch on your local workspace.
2) Complete all the Back-Log in the local branch.
3) Update the version of the project. e.g. **`pipenv run pysemver nextver $(cat version) major/minor/patch/prerelease/build > version`**
4) Stage files for your Commit. e.g. **`git add /path/to/file_name`**
5) Commit the files. e.g. **`git commit`**<br/>
    Format:<br/>
    ----------------------------------------------------<br/>
     Build no.: DDMMYYYY (i.e. 23122020)            <br/>
    Change Log:<br/>
    -  **`Point-Wise Change Log.`**<br/>

    ----------------------------------------------------<br/>
6) Push your commit to the remote branch **`git push -u origin current-branch-name`**
7) Create a Pull-Request (PR). e.g. **`gh pr create -B dev -b "This pull request is for current-branch-id" -r impriyanshub -a books-backend-workspace --title "Title of the Back-Log from Atlassian"`**
