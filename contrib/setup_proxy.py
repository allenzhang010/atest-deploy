#! /usr/bin/python


import os
import logging


def run_os_system_command(cmd, ignore_failure=False):
    logging.info("$ " + cmd)
    retcode = os.system(cmd)
    if retcode != 0:
        if not ignore_failure:
            raise Exception("Could not execute command: " + cmd)
    return retcode

proxies = {'our_proxies':
    (
       "export http_proxy=http://web-proxy.houston.hp.com:8088\n",
       "export FTP_PROXY=http://web-proxy.houston.hp.com:8088\n",
       "export ftp_proxy=http://web-proxy.houston.hp.com:8088\n",
       "export HTTPS_PROXY=https://web-proxy.houston.hp.com:8088\n",
       "export https_proxy=https://web-proxy.houston.hp.com:8088\n",
       "export HTTP_PROXY=http://web-proxy.houston.hp.com:8088\n",
       "export noproxy=localhost,127.0.0.1\n"
    )
}

etc_profile_file = '/etc/environment'
evfile_handle = open(etc_profile_file, 'a+')
evfile_handle.writelines(proxies['our_proxies'])
evfile_handle.close()
cmd = "source " + etc_profile_file
run_os_system_command(cmd)
