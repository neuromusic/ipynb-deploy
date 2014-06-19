ipynb-deploy
============

deploy ipython notebook instances on a server

this script assumes a few things:

1. you have fabric installed locally
2. you have anaconda's python environment installed on your server
3. you have supervisor and nginx running on your server
4. supervisor is configured to include .conf files located in `/etc/supervisor.ipython/`
5. nginx is configured to include location .conf files located in `/etc/nginx/conf.d/ipynb/`

run the script locally:

    ipynb_config.py username 8888
    
where `username` is the user that you are setting up a notebook for and `8888` is a unique port. Follow the prompts to login to the server with a user that has sudo priviledges. The script will also prompt you for a password for the user's ipython notebook profile.
