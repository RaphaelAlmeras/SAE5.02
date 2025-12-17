#!/bin/bash
docker exec -it ansible-runner ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/deploy_web.yml
