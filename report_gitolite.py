#!/bin/env python2

import os
import config


gitstats_cmd=config.gitstats_cmd or "python gitstats"


def getRepo():
    git_config = config.git_config_file  #"/Users/anfeng/works/gitolite-admin/conf/gitolite.conf"
    git_url_prefix =config.git_url_prefix # "git@192.168.1.241"
    filters = config.filter_string.split(',') # test, gitolite-admin

    file = open(git_config,"r") 
    #print file.readlines()

    repos = []
    for line in file.readlines():
        if 'repo ' not in line:
            continue

        b = 0
        for f in filters:
            if f in line:
                b = 1
                continue

        if b:
            continue

        gitpath = line.replace('repo ','').replace('\n','')
        name = gitpath[gitpath.find('/')+1:]
        repos.append({'name':name, 'url':git_url_prefix + ":" + gitpath+ '.git'})

    #print(repos)
    return repos

working_dir = os.path.dirname(os.path.realpath(__file__))

coms = [gitstats_cmd]

for repo in getRepo():
    # if not repo['active']:
        # continue

    if 'branch' not in repo or repo['branch']=='':
        repo['branch'] = config.branch

    repo_path = os.path.join(config.repo_dir, repo['name'], repo['branch'])

    # clone repo if not exists
    if not os.path.exists(repo_path):
        command = 'git clone -b %s %s %s' % (repo['branch'], repo['url'], repo_path)
        print 'clone repo: %s' % command
        result = os.system(command)
        if result != 0:
            continue

    # update repo
    command = 'cd %s && git pull && cd %s' % (repo_path, working_dir)
    print 'update repo: ', command
    os.system(command)

    # generate statistic html
    statistic_dir = os.path.join(config.vis_dir, repo['name'])
    if not os.path.exists(statistic_dir):
        os.makedirs(statistic_dir)

    coms.append(repo_path)
    if config.generate_per_repo:
        command = gitstats_cmd +' %s %s' % (repo_path, statistic_dir)
        print command
        os.system(command)


if config.generate_all_repos:
    statistic_dir = os.path.join(config.vis_dir, 'report')
    coms.append(statistic_dir)
    cmd = ' '.join(coms)
    print(cmd)
    os.system(cmd)

