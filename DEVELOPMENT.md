# Development Guide

## Creating the test VM

The *tests* directory contains a Vagrantfile that spawns a Debian 9 VM.

- First install [Vagrant](https://www.vagrantup.com/downloads.html) (version >= 2)
- Then boot the VM.

```sh
sudo apt install -y virtualbox
cd tests
vagrant up --provider=virtualbox
```

To clear the VM:

```sh
cd tests
vagrant destroy -f && vagrant up
```

Note that you can take advantage of snapshots to speedup the clearing process.

## Tests

### Unit

Some unit tests exist for the custom ansible module.

```sh
python -B -m unittest discover -p "*_test.py" playbooks/library
```

### End to End

There are two ways of testing, using a docker image (preferred way) or using directly Ansible.


#### Requirements

Installing [direnv](https://direnv.net) or a similar tool is recommended to automatically load environment variables from files inside your directory.
Direnv automatically loads variables inside *.envrc* files.

- Create a *.envrc*.

```sh
cat <<EOF > .envrc
export MODULES_ROOT="$PWD"/test/sample-infra
export SSH_HOST=10.10.10.10
EOF
```


#### Using the docker image

Building the docker image and running it is the preferred way of testing as you don't need to install Ansible on your machine.

- Install [direnv](https://direnv.net) to automatically load environment variables from *.envrc*.
- Add the following variables in your *.envrc*.

```sh
cat <<EOF >> .envrc
export SSH_FINGERPRINT='$(ssh-keyscan -H 10.10.10.10)'
export SSH_PRIVATE_KEY='$(cat ~/.vagrant.d/insecure_private_key)'
EOF
```

- Then build the Docker image and run it against the VM.

```sh
docker build -t totakoko/compose-deploy:dev . && docker run -it --rm \
  -v "$MODULES_ROOT:/modules:ro" \
  -e SSH_HOST \
  -e SSH_FINGERPRINT \
  -e SSH_PRIVATE_KEY \
  totakoko/compose-deploy:dev
```


#### Using the ansible script

- First install [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).
- Add the following to your *~/.ssh/config*.

```
Host 10.10.10.10
  User root
  IdentityFile ~/.vagrant.d/insecure_private_key
```

- Add the server fingerprint to your known hosts

```sh
ssh-keyscan -H 10.10.10.10 >> ~/.ssh/known_hosts
```

- Finally, run the deployment script against the VM.

```sh
./run.sh deploy
```
