#! /usr/bin/python
'''
Created on July 3, 2013

@author: Allen Zhang <zhi-qiang.zhang@hp.com>

Deploy the autotest git source code(dev branch) to cirrusvm01.chn.hp.com:
python /home/allen/git/Autotest/contrib/deploy_cirrus.py -p /home/allen/git/Autotest -r cirrusvm01.chn.hp.com -f

Deploy development work(Eclipse) source code(dev branch) to cirrus01.chn.hp.com
python /home/allen/git/Autotest/contrib/deploy_cirrus.py -p /home/allen/git/Autotest -r cirrusvm01.chn.hp.com -f -l

'''

import os.path
from optparse import OptionParser
import logging
import subprocess
import signal
import string
import shutil
import random
import crypt
import re
from string import Template

'''
Allen's dev VM private key. for gerrit access available for Autotest.git repos
'''
KEY_FOR_GIT_ACCESS = """
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA7n87GpO6rsgQhisWw03KRWtipV2Hu0rXOl443v11oWb5DmFF
j/g0pwoUBdUcoQgHZB5NDeG1cUuaNneJUZCIpdqD6gG1zXob4a6PUX44UfoEIWwB
u7zXeEPGNkbWz6Lo0+0VckXdXN1QI4HSYTRS0+9XMtqZnYTDSx1XZ1RdBRsjaJts
/ULVTuBUYiVzobYjmxwFeuXLJmYFBkWm0peEXYofB9iYua9N4vyt/fRjHfSkbGH5
XIWaNYpCi+8TFYTV03Vk9QFPhRA5U/lud4nhFdYBnhmxopWO3sqjKbtcgPVXwSz7
ESKsijYnBoNcfAFx+1LF7XehMFfJ3aAHjib++QIBIwKCAQAbQb2coytHLM6wP3BQ
1bC3efylL0K2UbIyjmzmSNo+VOlDeNS//xv11UQd7HhM6vmHyPLdA9o41XC1xIS4
3VFyClg4ADII2sFbnuvOzJi46V+OyoPa8QKuqKjwQpw0/KzlBScFvtd4U86k+OTX
6LkCRz0qYiAvQl92TH8EfquLjdoyW8mKprFSTA8Or8R6ILsfSOszTSgS9h660s1f
TbDa4tpfOCFJ8PAAxAKqPCLhFtNauO/S8bHjNdD1tEAbgzIkzTPDzPP2YyyZP5gE
KuIL+hiBLKojmJPujh2Jjv0CFhEIWjkW5TtXdQ5h71EznlBnEJBVRQHbdsM6eRzm
Pdi7AoGBAPdXYqhDwJZI3f7KEsHLi2gNcAgC/b6sW8TTo0hBEqs34bZ19qMBF9KF
j2TpOSi1atioHuN9AkfsgVGJLvG17++nVqeQuD33tzhhr+6yxZwymNmjP0Hcilwr
nQepNvtBeg8lgYLtXb7MZ0TTnRrGpn3JBTK6yFj3qCFhrmTJBMEbAoGBAPbYlaE8
T6916NHXkLqpjFY77fN3BO3UILNP7dmPnQ2qZ3HQttJxm0dWujHDLQk3AhJqcONp
wH3E8gyc1vBu2O9qGzhzB7rhdTq1XQ2gTQr6cNGQk58OlCRL0hkM4TttOjOSlgSb
byaAjqRZ+DsxsbSsfKRIk3f4YHw8TeXmhRV7AoGAHESATb6ZqsZ/xVjsM2e4KSYb
bqFBkiJToXdF3F81VWV44acU323W1jsmVKzwlvApd9izEq8zde8kuNx6ZMRV74DW
tBCKFbXpDcIFel2S7UeccKTxSVsIf4/0sGscOfjav+cHfK1pzKmlZvOc7R4EZiWa
Ma7yU0+A7d9HIXYPLAMCgYEA78sVAwdjWf2DFP1Kw/UpPdPRNabRlpONev0wMm5A
y3JV3EcX/6GPhyEMpV6DhUthGTQzJg71gX19a1aHp7wjMbeIKDU6tYqPIxaU6KpZ
eGD/4YUhsHSP6L6u1oGKVvxkbJ0GwqWfLLdl/r3MkUY3mZGdpudqrw6JnUHlRbtc
tccCgYEAtm8bO1GMI/a2kSHZVjjpJ9V4uMToGSmS2W5h8Kb9xS8awt3E8nhpmc7n
ttF55GppqKK5u7G90S+Z+mWzt4nk8rJafPAPEsAEbIcHOyKqPFqLzRmdz/NWQeXH
ODHOHnFPlVcvAcL8bnuVKzLYDM8rlUlZTkhxFeBwvWa/g3uFXq0=
-----END RSA PRIVATE KEY-----
"""

shadow_config = """
[AUTOTEST_WEB]
# Machine that hosts the database
host: localhost
# Name of the autotest database
database: autotest_web
# DB backend
db_type: mysql
# DB user
user: autotest
# DB password. You must set a different password than the default
password: cirrus
# Timeout for jobs (hours)
# (if scheduled but does not get to run, it will be aborted)
job_timeout_default: 24
# Maximum runtime for jobs (hours)
# (if it gets to run but does not complete, it will be aborted)
job_max_runtime_hrs_default: 8


[SERVER]
# Hostname of the autotest RPC server. You should set a different hostname
hostname: $hostname
# Turn on RPC Logging
rpc_logging: True
# RPC log path. Note that webserver user needs to be able to write to that path
rpc_log_path: /usr/local/autotest/logs/rpcserver.log
# Time in hours to wait before giving up on crash collection. A timeout of 0
# means crash collection is skipped unless the host is already available.
crash_collection_hours_to_wait: 0.3

[SCHEDULER]
# Where to send emails with scheduler failures to
# (usually an administrator of the autotest setup)
notify_email: csi.cirrus.bj@hp.com
# Where the emails seem to come from (usually a noreply bogus address)
notify_email_from: autotest

[INSTALL_SERVER]
# Install server type
type: cobbler
# URL for xmlrpc_server, such as http://foo.com/cobbler_api
xmlrpc_url: http://$cobbler_server/cobbler_api
# XMLRPC user, in case the server requires authentication
user: cobbler
# XMLRPC password, in case the server requires authentication
password: mclinux
# Profile to install by default on your client machine
fallback_profile: rh6.2_srv_x86_64-sut
# By default use current profile from install server, if False: will default to 'Do_not_install'
use_current_profile: False

"""


GIT_REPOS_DIR = "/usr/local/"


def parse_cmd_line():
    parser = OptionParser()
    parser.add_option("-f", "--force",
                      help='force removal of existing installation',
                      action="store_true", dest="force")
    parser.add_option("-r", "--remote_host",
                      help='where to install',
                      action="store", dest="remote_host")
    parser.add_option("-a", "--autotest_host",
                      help='what to set as autotest rpc host',
                      action="store", dest="autotest_host")
    parser.add_option("-p", "--autotest_path",
                      help='/path/dir/to/your/autotest',
                      action="store", dest="autotest_path")
    parser.add_option("-l", "--local_autotest",
                      help="install local autotest bits",
                      action="store_true", dest="local_autotest")
    return parser


def run_os_system_command(cmd, ignore_failure=False):
    logging.info("$ " + cmd)
    retcode = os.system(cmd)
    if retcode != 0:
        if not ignore_failure:
            raise Exception("Could not execute command: " + cmd)
    return retcode


def _check_output(args, ignore_failure=False, stderr=subprocess.STDOUT, \
                  preexec_fn=None):
    logging.debug("$ " + ' '.join(args))
    process = subprocess.Popen(args, stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT, preexec_fn=preexec_fn)
    output, err = process.communicate()
    retcode = process.poll()
    if stderr == subprocess.STDOUT:
        output += str(err)
    if retcode:
        if not ignore_failure:
            err_text = 'Command {0} returned exitcode={1}, {2}'.format("$" + \
                        ' '.join(args), retcode, output)
            logging.error(err_text)
            raise Exception("command failed, see below for output:\n\n" + \
                            output)
    return output


def kill_process_if_running(processname):
    found = False
    for line in os.popen('ps -eo "%p|%a"'):
        fields = line.split("|")
        pid = fields[0]
        process = fields[1]
        if process.find(processname) > 0:
            logging.info("Killing " + processname + " " + pid)
            os.kill(int(pid), signal.SIGHUP)
            found = True
    if not found:
        logging.info("Not found: " + processname + " ")


def prepare_git():
    logging.info("Create the SSH key directory and the private key file. " +
                 "Set appropriate permissions.")
    key_location = "/root/.ssh"
    key_file = key_location + "/id_rsa"
    if not os.path.exists(key_location):
        os.mkdir(key_location, 0700)

    priv_key_filehandle = open(key_file, 'w')
    priv_key_filehandle.write(KEY_FOR_GIT_ACCESS)
    priv_key_filehandle.close()

    os.chmod(key_file, 0600)

    logging.info("Create the directory where Git repos will be cloned.")
    if(not os.path.exists(GIT_REPOS_DIR)):
        os.mkdir(GIT_REPOS_DIR, 0755)

    ssh_wrapper_file = "/root/ssh_wrapper_for_git"
    logging.info("Setting up the SSH wrapper file for Git (" +\
                 ssh_wrapper_file + ")...")
    filehandle = open(ssh_wrapper_file, 'w')
    filehandle.write(r"#!/bin/sh" + "\n")
    filehandle.write(r"exec ssh -o StrictHostKeyChecking=false $*" + "\n")
    filehandle.close()
    # Set execute permission for the file.
    os.chmod(ssh_wrapper_file, 0700)
    # Setup GIT_SSH env var to point to this file.
    os.environ["GIT_SSH"] = ssh_wrapper_file
    logging.info("git preparation completed.")


class install_autotest:
    def __init__(self, app_path, evfile='/etc/environment'):
        self.app_path = app_path
        self.setup_blofly_repos()
        self.setup_epel_repos()
        allevs = list()
        try:
            allevs = open(evfile).read().split("\n")
        except Exception:
            pass
        for ev in allevs:
            try:
                (k, v) = ev.split("=")
                os.environ[k] = v.strip('"')
            except Exception:
                pass
        logging.debug("Created installation object")

    def setup_blofly_repos(self):
        file_contents = """
[blofly-repo]
name=Blofly Server 6.3 DISC Repository
baseurl=http://linux.usa.hp.com/blofly/mrepo/RHEL-6.3Server-x86_64/disc1/
enable=1
gpgcheck=0

[blofly-Server-Repo]
name=Blofly Server 6.3 Repository
baseurl=http://linux.usa.hp.com/blofly/mrepo/RHEL-6.3Server_Supplementary-x86_64/RPMS.os/
enabled=1
gpgcheck=0

[blofly-Server-Supp-Repo]
name=Blofly Server 6.3 Supplementary Repository
baseurl=http://linux.usa.hp.com/blofly/mrepo/RHEL-6.3Server_Supplementary-x86_64/RPMS.os/
enabled=1
gpgcheck=0
"""
        repofile_handle = open("/etc/yum.repos.d/blofly.repo", 'w')
        repofile_handle.write(file_contents)
        repofile_handle.close()

    def setup_epel_repos(self):
        logging.info("Setting up EPEL 6 repo pointing to mint-fileserver...")
        file_contents = """
[mint-epel-6]
name=(on mint-fileserver) Extra Packages for Enterprise Linux 6 - $basearch
baseurl=http://mint-fileserver.usa.hp.com/cobbler/epel/6/$basearch
enabled=1
gpgcheck=0
"""
        repofile_handle = open("/etc/yum.repos.d/mint-epel-6.repo", 'w')
        repofile_handle.write(file_contents)
        repofile_handle.close()

    def install_basic_software(self):
        logging.info("Installing Basic Software")
        _check_output(["yum", "-y", "groupinstall", "Development"])
        _check_output(["yum", "-y", "groupinstall", "Web Server"])
        _check_output(["yum", "-y", "groupinstall", "MySQL Database server"])
        _check_output(["yum", "-y", "groupinstall", "MySQL Database client"])
        logging.info("Installing Python addons")
        _check_output(["yum", "-y", "install", "python-devel"])
        _check_output(["yum", "-y", "install", "python-storm-mysql-0.19-1.el6.x86_64"])
        _check_output(["yum", "-y", "install", "python-ldap"])
        _check_output(["yum", "-y", "install", "python-matplotlib"])
        _check_output(["yum", "-y", "install", "python-paramiko"])
        _check_output(["yum", "-y", "install", "expect"])
        logging.info("Installing pip")
        _check_output(["easy_install", "pip"])
        logging.info("Installing django")
        _check_output(["pip", "uninstall", "-y", "Django"], ignore_failure=True)
        _check_output(["rm", "-fr", "/usr/lib/python2.6/site-packages/django"], ignore_failure=True)
        _check_output(["pip", "install", "Django==1.4.3"])
        logging.info("Installing PIL")
        _check_output(["pip", "install", "PIL"])
        logging.info("Done Installing Basic Software")

    def upgrade_basic_software(self):
        logging.info("Upgrading Basic Software")
        logging.info("Stop apache")
        _check_output(["apachectl", "-k", "stop"])
        logging.info("Upgrading django")
        _check_output(["pip", "uninstall", "-y", "Django"], ignore_failure=True)
        _check_output(["rm", "-fr", "/usr/lib/python2.6/site-packages/django"], ignore_failure=True)
        _check_output(["pip", "install", "--upgrade", "--force-reinstall", "Django==1.4.3"])
        logging.info("Running django: " + _check_output(["django-admin.py", "--version"]))
        logging.info("Updating simplejson")
        _check_output(["pip", "install", "--upgrade", "simplejson"])
        logging.info("Starting apache")
        _check_output(["apachectl", "-k", "start"])
        logging.info("Done Upgrading Basic Software")

    def remove_autotest(self):
        """
        Kill the autotest related processes and delete
        /usr/local/autotest directory!!
        """
        logging.info("Removing existing autotest")
        logging.info("Remove autotest droppings")
        _check_output(["userdel", "autotest"], ignore_failure=True)
        for f in ['/etc/httpd/conf.d/z_autotest.conf',
                  '/etc/httpd/conf.d/z_autotest-web.conf',
                  '/etc/httpd/conf.d/autotest.conf']:
            if os.path.lexists(f):
                logging.info("Remove " + f)
                os.remove(f)
        logging.info("Stop apache")
        _check_output(["apachectl", "-k", "stop"])
        logging.info("Stop autotest deamons")
        kill_process_if_running("/autotest-scheduler-watcher ")
        kill_process_if_running("/autotest-scheduler ")
        logging.info("Remove autotest directory")
        if os.path.exists('/usr/local/autotest'):
            shutil.rmtree('/usr/local/autotest')
        logging.info("Removing existing autotest completed")

    def remove_autotest_database(self):
        """
        Drop the whole database before reinstall!!
        """
        logging.info("Drop autotest_web database")
        _check_output(["mysqladmin", "drop", "autotest_web", "-u",\
                "autotest", "--password=cirrus", "-f"], ignore_failure=True)
        logging.info("=" * 40)

    def install(self, force, autotest_local_install_path):
        """
        Install autotest bits here!!
        """
        self.remove_autotest()
        self.remove_autotest_database()
        if autotest_local_install_path:
            logging.info("Getting local copy of autotest")
            logging.info("rsync -az --delete " + autotest_local_install_path + " /usr/local/autotest/ --timeout 120")
            _check_output(["rsync", "-az", "--delete",
                                  autotest_local_install_path + "/",
                                  "/usr/local/autotest/",
                                  "--timeout", "120"])
        else:
            os.chdir('/usr/local')
            logging.info("git clone ssh://zhazhiqi@depot01.chn.hp.com:29418/Autotest.git autotest in /usr/local/ directory")
            output = _check_output(["git", "clone",
                                    "ssh://zhazhiqi@depot01.chn.hp.com:29418/Autotest.git",
                                    "autotest"])
            logging.debug(output)
            os.chdir('/usr/local/autotest')
            logging.info("git checkout dev")
            output = _check_output(["git", "checkout", "dev"])
            logging.debug(output)
        os.chdir('/usr/local/autotest')
        logging.info("./utils/build_externals.py")
        run_os_system_command("./utils/build_externals.py")
        run_os_system_command("/usr/local/autotest/contrib/install-autotest-server.sh -u cirrus -d cirrus -n")
        logging.debug('Change mod on logs dir')
        run_os_system_command("touch /usr/local/autotest/logs/rpcserver.log")
        run_os_system_command("chmod 666 /usr/local/autotest/logs/rpcserver.log")
        logging.debug('Create autotest symlink')
        run_os_system_command("ln -s  /usr/local/autotest/cli/autotest-rpc-client /usr/local/autotest/cli/atest")

    def config_global_config_ini(self, autotest_host):
        """
        Repleace the $hostname placeholder in the template
        file shadow_config.ini file, and then write it to
        the target variable file.
        """
        target = "/usr/local/autotest/shadow_config.ini"
        logging.info("Configuring " + target)
        shadow_config_text = Template(shadow_config).safe_substitute(
                            hostname=autotest_host)
        f = open(target, 'w')
        f.write(shadow_config_text)
        f.close()

    def add_single_user(self, user, passwd, is_super, first_user):
        import MySQLdb as mdb
        script = "/usr/bin/htpasswd"

        def getsalt(chars=string.letters + string.digits):
            return random.choice(chars) + random.choice(chars)

        if first_user:
            opt = " -cb"
        else:
            opt = " -b"
        cmd = script + opt + " /etc/autotest_pw" + " " + user + ' "' + passwd + '"'
        logging.info("DOING: '" + cmd + "'")
        retcode = os.system(cmd)
        if retcode != 0:
            raise Exception("Could not execute script " + script)

        pw = crypt.crypt(passwd, getsalt())

        cmd = ["useradd", "-b", "/home", "-c", "Autotest admin account", '-p', pw, user]
        logging.info("DOING: '" + " ".join(cmd) + "'")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        unused_output, errors = p.communicate()
        if errors:
            match = re.match('.*(already|file) exists.*', errors)
            if not match:
                raise Exception("Failed to create user at_admin: " + errors)

        # force the user into the autotest MQSQL DB
        # export AUTOTEST_USER=user_name; /usr/local/autotest/autotest-rpc-client user list
        os.putenv("AUTOTEST_USER", user)
        cmd = ["/usr/local/autotest/cli/autotest-rpc-client", "user", "list"]
        logging.info("DOING: '" + " ".join(cmd) + "'")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, errors = p.communicate()
        logging.info(output)
        if errors:
            logging.info("User list failed: " + errors)
        if is_super:
            con = mdb.connect('localhost', 'root', 'cirrus', 'autotest_web')
            cur = con.cursor()
            cmd = "update auth_user set is_superuser=true where username='" + \
                user + "'"
            logging.info("DOING: '" + cmd + "'")
            cur.execute(cmd)

    def add_users(self):
        """
        now create users neccessary for the setup for Cirrus BJ team members
        """
        logging.info("Adding users")
        self.add_single_user('at_admin', 'at_admin', True, True)
        self.add_single_user('allen', 'cirrus', False, False)
        self.add_single_user('edwin', 'cirrus', False, False)
        self.add_single_user('christy', 'cirrus', False, False)
        self.add_single_user('simon', 'cirrus', False, False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    cmd_parser = parse_cmd_line()
    (options, args) = cmd_parser.parse_args()
    if options.remote_host:
        repo_top_dir = options.autotest_path
        if not repo_top_dir:
            logging.error("Must specify the local autotest home dir" +
                          " path if using remote option.")
            exit(1)
        if options.local_autotest:
            logging.info("Rsyncing local autotest to remote host: {0}".format(
                options.remote_host))
            run_os_system_command("rsync -az --delete " +\
                "--rsh='ssh -l root' {0}/ root@{1}:/root/autotest/".format(
                            repo_top_dir, options.remote_host) +\
                " --timeout 120")
            cmd = "/root/autotest/contrib/deploy_cirrus.py " +\
                "-f -l -p /root/autotest/ -a " + options.remote_host
            logging.info("=" * 40)
            logging.info("Setup proxy for your remote host: " + \
                         options.remote_host)
            cmd_setup_proxy = "/root/autotest/contrib/setup_proxy.py"
            run_os_system_command("ssh root@{0} '{1}'".format(
                options.remote_host, cmd_setup_proxy))
            logging.info("=" * 40)
        else:
            logging.info("Just rsyncing cirrus_setup_wrapper dir to \
remote host".format(options.remote_host))
            run_os_system_command("rsync -az --delete " +\
            "--rsh='ssh -l root' {0}/contrib/ root@{1}:/root/autotest/".format(
                                       repo_top_dir, options.remote_host) +\
            " --exclude cgi-bin --exclude virt --timeout 120")
            cmd = "/root/autotest/deploy_cirrus.py " +\
                "-f -p /root/autotest/ -a " + options.remote_host
            logging.info("=" * 40)
            logging.info("Setup proxy for your remote host: " + \
                         options.remote_host)
            cmd_setup_proxy = "/root/autotest/setup_proxy.py"
            run_os_system_command("ssh root@{0} '{1}'".format(
                options.remote_host, cmd_setup_proxy))
            logging.info("=" * 40)
        run_os_system_command("ssh root@{0} '{1}'".format(
            options.remote_host, cmd))
    else:
        if os.path.exists("/usr/local/autotest"):
            if not options.force:
                logging.error("Error: There is already existing app \
instance!! Please use -f")
                exit(1)
        if not options.autotest_host:
            logging.error("Must specify the -a(autotest_host) option!!!")
            exit(1)
        if options.autotest_path:
            repo_top_dir = options.autotest_path
        else:
            logging.info("=" * 40)
            logging.error("options.autotest_path should not be NONE!!! \
Error Occured!!!")
            logging.info("=" * 40)
            exit(1)
        prepare_git()
        inst = install_autotest('/usr/local/autotest')
        if options.local_autotest:
            autotest_local_install_path = options.autotest_path
        else:
            autotest_local_install_path = None
        inst.install_basic_software()
        inst.install(options.force, autotest_local_install_path)
        inst.config_global_config_ini(autotest_host=options.autotest_host)
        inst.add_users()
        inst.upgrade_basic_software()
        logging.info("Installation Completed!! Enjoy!!!")
    exit(0)
