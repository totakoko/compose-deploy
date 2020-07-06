#!/bin/sh -e

# This script will make a commit in the test repositories, deploy the changes and wait for the changes
# to be effective to mark the build as successful

eval $(ssh-agent -s) > /dev/null
echo "$SSH_PRIVATE_KEY_BASE64" | base64 -d | tr -d '\r' | ssh-add - 2> /dev/null
echo 'gitlab.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsj2bNKTBSpIYDEGk9KxsGh3mySTRgMtXL583qmBpzeQ+jqCMRgBqB98u3z++J1sKlXHWfM9dyhSevkMwSbhoR8XIq/U0tCNyokEi/ueaBMCvbcTHhO7FcwzY92WK4Yt0aGROY5qX2UKSeOvuP4D6TPqKF1onrSzH9bx9XUf2lEdWT/ia1NEKjunUqu1xOB/StKDHMoX4/OKyIzuS0q/T1zOATthvasJFoPrAjkohTyaDUz2LN5JoH839hViyEG82yB+MjcFV5MU3N1l1QL3cVUCh93xSaua1N85qivl+siMkPGbO5xR/En4iEY6K2XPASUEMaieWVNTRCtJ4S8H+9
gitlab.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFSMqzJeV9rUzU4kWitGjeR4PWSa29SPqJ1fVkhtj3Hw9xjLVXVYrU9QlYWrOLXBpQ6KWjbjTDTdDkoohFzgbEY=
gitlab.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAfuCHKVTjquxvt6CM6tdG4SLp1Btn/nOeHHE5UOzRdf' >> ~/.ssh/known_hosts
echo 'github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==' >> ~/.ssh/known_hosts

hash=$CIRCLE_SHA1
branch=$CIRCLE_BRANCH

git config --global user.email "maxime@dreau.fr"
git config --global user.name "Maxime Dréau (CI)"

git clone git@gitlab.com:totakoko/compose-deploy-ci-project-gitlab.git sample-project
cd sample-project
if git fetch origin $branch; then
  git checkout $branch
else
  git checkout -b $branch
fi
sed -ri "s/(compose-deploy-ci:)\w+/\1$hash/" .gitlab-ci.yml
sed -ri "s/(CONTENT=)\w*/\1$hash/" */docker-compose.yml
git add -A
git commit -m "Testing deployment of compose-deploy:$hash"
git push origin $branch
rm -rf sample-project

check_deployment() {
  local label=$1
  local serverURL=$2
  local expectedHash=$3

  local counter=0
  local maxCounter=3
  local sleepTime=5

  # wait for 5 minutes maximum
  while [ $counter -lt $maxCounter ]; do
    local serverHash=$(curl -s --max-time 5 $serverURL)
    if [ "$serverHash" = "$expectedHash" ]; then
      echo "$label deployment succeeded"
      return 0
    fi
    sleep $sleepTime
    counter=$((counter+1))
  done

  echo "$label deployment failed"
  echo "Curl output: $(curl -v --max-time 5 $serverURL)"
  return 1
}

check_deployment "GitLab CI" totakoko.com:8501 $hash

# TODO circle CI and wait for results
