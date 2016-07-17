# deployment script for all datapipes

import os
import json
import shutil
from distutils.dir_util import copy_tree

import boto3
import boto3.session

def deploy():

    session = boto3.session.Session(profile_name='personal')

    deploy_lambdas(session)


def deploy_lambdas(session):

    for function_name in os.listdir('lambda/src'):
        generate_zip(function_name)
        deploy_lambda_function(session, function_name)


def deploy_lambda_function(session, function_name):

    # load in configs
    function_cfg = json.load(open('lambda/conf/{}.json'.format(function_name)))
    default_cfg = json.load(open('lambda/conf/defaults.json'))
    default_cfg.update(function_cfg)
    cfg = default_cfg

    lambda_client = session.client('lambda')

    # emoji = '\xF0\x9F\x92\xA9' # poo
    # emoji = '\xF0\x9F\x8D\xA5' # fish cake
    # emoji = '\xF0\x9F\x8D\xBA' # beer
    emoji = '\xF0\x9F\x8D\x95' # pizza

    print ''

    try:

        # function already exists, so update it
        print '{}  checking if function exists: {}'.format(emoji, function_name)
        lambda_client.get_function_configuration(
                FunctionName=function_name)

        print '\t{}  updating function configuration: {}'.format(emoji, function_name)
        lambda_client.update_function_configuration(
                FunctionName=function_name,
                Role=session.resource('iam').Role(cfg['role']).arn,
                Handler=cfg['handler'],
                Description=cfg.get('description', None),
                Timeout=cfg['timeout'],
                MemorySize=cfg['memory'],
                VpcConfig=cfg.get('vpc', {}))

        print '\t{}  updating function code: {}'.format(emoji, function_name)
        lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=open('_deploy/_zip/{}.zip'.format(function_name), 'rb').read())
    except:

        # function is new, so create it
        print '\t{}  creating new function: {}'.format(emoji, function_name)
        lambda_client.create_function(
                FunctionName=function_name,
                Runtime=cfg['runtime'],
                Role=session.resource('iam').Role(cfg['role']).arn,
                Code={
                    'ZipFile': open('_deploy/_zip/{}.zip'.format(function_name), 'rb').read()
                    },
                Handler=cfg['handler'],
                Description=cfg.get('description', None),
                Timeout=cfg['timeout'],
                MemorySize=cfg['memory'],
                VpcConfig=cfg.get('vpc', {}))

    print ''

def generate_zip(function_name):

    # wipe function folder if exists
    dir_path = '_deploy/{}'.format(function_name)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    else:
        os.mkdir(dir_path)

    # copy code, modules, etc to directory
    copy_tree('lambda/pkg/', dir_path)
    copy_tree('lambda/src/{}'.format(function_name), dir_path)

    zip_path = '_deploy/_zip/{}.zip'.format(function_name)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # zip contents of dir
    shutil.make_archive('_deploy/_zip/{}'.format(function_name), 'zip', dir_path)

if __name__ == '__main__':
    deploy()

