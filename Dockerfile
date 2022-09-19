FROM willhallonline/ansible:2.9.27-alpine-3.15

LABEL maintainer="maxime@dreau.fr"

ENV ANSIBLE_CONFIG=/compose-deploy/ansible.cfg
ENV SSH_FROM_ENV=true
ENV MODULES_ROOT=/modules

COPY . /compose-deploy
RUN ln -s /compose-deploy/run.sh /usr/local/bin/compose-deploy

WORKDIR /compose-deploy
ENTRYPOINT ["compose-deploy"]
CMD ["deploy"]
