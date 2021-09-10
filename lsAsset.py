#!/usr/bin/env python3

import logging
import argparse
import urllib.request
import urllib.parse
import json
import csv

from storageHandler import StorageHandler

#TODO Add meaningful logging
#logging.basicConfig(level=logging.ERROR, filename='./lsAsset.log')
#logging.basicConfig(level=logging.DEBUG, filename='./lsAsset.debug.log')

def initArgParse():
    parser = argparse.ArgumentParser(description='List Assets from Anypoint Exchange')
    parser.add_argument('--username','-u', required=False)
    parser.add_argument('--password','-p', required=False)
    parser.add_argument('--client-id','-c', required=False,dest='clientId')
    parser.add_argument('--client-secret','-s', required=False,dest='clientSecret')
    parser.add_argument('--organizationId','-o', required=False)
    parser.add_argument('--masterOrganizationId','-m', required=False)
    parser.add_argument('--output-file','-f',required=False,dest='output')
    parser.add_argument('--database','-d',required=False)
    return parser.parse_args()

def getAssets(t,o,m):
    path = 'exchange/api/v2/assets/search'
    headers = {'Authorization': 'Bearer '+t}
    params = {}
    params['masterOrganizationId'] = m
    if o is not None:
        params['organizationId'] = o
    params['limit'] = 20
    params['offset'] = 0
    out = list()
    while True:
        try:
            response = getAPI(path, params, headers)
            jsRes = json.loads(response)
        except BaseException:
            print('Something went wrong')
            raise
            #TODO: Handle Errors more granularly
        if len(jsRes) == 0:
            return out
        else:
            out.extend(jsRes)
            params['offset']+=params['limit']

def getOrgId(t):
    path = 'accounts/api/me'
    headers = {'Authorization': 'Bearer '+t}
    try:
        response = getAPI(path, None, headers)
        js = json.loads(response)
        return js['user']['organizationId']
    except BaseException:
        print('Invalid credentials or bad response exception')
        raise
        #TODO: Handle Errors more granularly


def authenticatePassword(u,p):
    path = 'accounts/login'
    values = {'username': u, 'password': p}
    try:
        response = postAPI(path, values)
        js = json.loads(response)
        return js['access_token']
    except BaseException:
        print('Invalid credentials or bad response exception')
        raise
        #TODO: Handle Errors more granularly

def authenticateClientCredentials(ci,cs):
    path = 'accounts/api/v2/oauth2/token'
    values = {'client_id': ci, 'client_secret': cs, 'grant_type': 'client_credentials'}
    try:
        response = postAPI(path, values)
        js = json.loads(response)
        return js['access_token']
    except BaseException:
        print('Invalid credentials or bad response exception')
        raise

def authenticate(u,p,ci,cs):
    if u is not None and p is not None:
        return authenticatePassword(u,p)
    elif ci is not None and cs is not None:
        return authenticateClientCredentials(ci,cs)
    else:
        raise BaseException('No credentials provided, provide  username and password or client id and client secret')

def getAPI(path, parameters = None, headers = {}):
    return callAPI(path, parameters, None, headers, 'GET')

def postAPI(path, data, headers={}):
    return callAPI(path, None, data, headers, 'POST')

def callAPI(path, parameters, data, headers, method):
    url = scheme + '://' + domain + '/'
    url += path
    if parameters is not None:
        url += '?%s' % urllib.parse.urlencode(parameters)
    logging.debug('path: %s, parameters: %s, data: %s, headers: %s, method: %s',path, parameters, data, headers, method)
    if data is not None:
        data = urllib.parse.urlencode(data).encode('ascii')
    headers = {} if headers is None else headers
    req = urllib.request.Request(url, data, headers, None, False, method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode('utf-8')
    except BaseException:
        print('Error with request')

if __name__ == '__main__':
### Setup resources needed to run program
    args = initArgParse()
    scheme = 'https'
    domain = 'anypoint.mulesoft.com'

### get bearer token
### handle bad credentials
    token = authenticate(args.username,args.password,args.clientId,args.clientSecret)

### get org ID if not provided
    if args.masterOrganizationId is None:
        args.masterOrganizationId = getOrgId(token)

###get assets
    assets = getAssets(token, args.organizationId, args.masterOrganizationId)

### store assets to db
    if args.database is not None:
        sh = StorageHandler(args.database+".db")
        for asset in assets:
            sh.upsertAsset(asset['organizationId'],asset['groupId'],asset['assetId'],asset['version'],asset['minorVersion'],asset['versionGroup'],asset['description'],asset['isPublic'],asset['name'],asset['contactName'],asset['contactEmail'],asset['type'],asset['status'],asset['createdAt'],asset['createdById'])

### format and export
    keys = assets[0].keys()
    if args.output is not None:
        outfile = open(args.output, 'w', newline='')
        csvWriter = csv.DictWriter(outfile,fieldnames=keys)
        csvWriter.writeheader()
        for asset in assets:
            csvWriter.writerow(asset)
    else:
        print(','.join(keys))
        for asset in assets:
                print(','.join(map(str,asset.values())))
