#!/bin/bash
docker exec -it ansible-runner ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/cleanup_docker.yml
