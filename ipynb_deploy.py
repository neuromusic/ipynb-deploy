#!/usr/bin/env python

from fabric.api import env, sudo, local
from fabric.contrib.files import append, exists
from fabric.operations import put
from fabric.context_managers import settings
from fabric.utils import abort
from IPython.lib import passwd

# supervisor config file location
SUPERVISOR_CONF = "/etc/supervisor.ipython/{u}.conf"

# template for supervisor config files
SUPERVISOR_CONF_TEMPLATE = """
[program:ipynb-{u}]
command = /usr/local/anaconda/bin/ipython notebook --profile={u}
user = {u}
directory = /home/{u}/
stdout_logfile = /home/{u}/logs/ipython_supervisor.log
redirect_stderr = true
environment=HOME="/home/{u}"
"""

# nginx config file location
NGINX_CONF = "/etc/nginx/conf.d/ipynb/{u}.conf"

# template for nginx config files
NGINX_CONF_TEMPLATE = """
location  /ipynb/{u}/ {{

    proxy_pass         http://127.0.0.1:{p};

    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-NginX-Proxy true;
    proxy_redirect off;

    # WebSocket Support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;

}}
"""

# ipython notebook config file location
IPYNB_CONF = "/home/{u}/.ipython/profile_{u}/ipython_notebook_config.py"

# ipython notebook config file location
IPYNB_CONF_TEMPLATE = """
# Configuration file for ipython-notebook.
# auto-generated

c = get_config()
c.NotebookApp.base_url = '/ipynb/{u}/'
c.NotebookApp.open_browser = False
c.NotebookApp.base_kernel_url = '/ipynb/{u}/'
c.NotebookApp.port = {p}
c.NotebookApp.password = u'{hpw}'
c.IPKernelApp.pylab = 'inline'
c.NotebookManager.notebook_dir = u'/home/{u}/'

"""

def backup_config(config_file):
    if exists(config_file,use_sudo=True):
        sudo('mv {f} {f}.orig'.format(f=config_file))

def user_config(username,port):
    with settings(sudo_user=username,warn_only=True):
        # append anaconda path to .bashrc
        append('/home/%s/.bashrc' % username,'export PATH=/usr/local/anaconda/bin:$PATH',use_sudo=True)

        # create log dir
        sudo('mkdir /home/%s/logs' % username)    
        sudo('touch /home/%s/logs/ipython_supervisor.log' % username) 

        # create ipython notebook profile
        sudo('ipython profile create %s' % username,user=username)
        # sudo('chmod -r {u} /home/{u}/.ipython'.format(u=username),user=root)

        # get hashed password
        hashed = passwd()

        # write ipynb config file
        ipynb_config_file = IPYNB_CONF.format(u=username)
        backup_config(ipynb_config_file)
        append(filename=ipynb_config_file,
               text=IPYNB_CONF_TEMPLATE.format(u=username,
                                               p=port,
                                               hpw=hashed,
                                               ),
               use_sudo=True,
               )

def system_config(username,port):
    # write supervisor config file
    supervisor_config_file = SUPERVISOR_CONF.format(u=username)
    backup_config(supervisor_config_file)
    append(filename=supervisor_config_file,
           text=SUPERVISOR_CONF_TEMPLATE.format(u=username),
           use_sudo=True,
           )
    # write nginx
    nginx_config_file = NGINX_CONF.format(u=username)
    backup_config(nginx_config_file)
    append(filename=nginx_config_file,
           text=NGINX_CONF_TEMPLATE.format(u=username,p=port),
           use_sudo=True,
           )

def system_update(username):
    # supervisorctl update
    sudo('/usr/local/anaconda/bin/supervisorctl update')
    sudo('/usr/local/anaconda/bin/supervisorctl %s restart' % username)

    # restart nginx
    sudo('service nginx restart')

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="the username to setup")
    parser.add_argument("port", help="the port this notebook will run on")
    args = parser.parse_args()
  
    user_config(args.username,args.port)
    system_config(args.username,args.port)
    system_update(args.username) 