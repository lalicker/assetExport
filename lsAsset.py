#!/usr/bin/env python3

import logging
import argparse
import urllib.request
import urllib.parse
import json
import csv

from storageHandler import StorageHandler

#TODO Add meaningful logging
#logging.basicConfig(level=logging.ERROR, filename='/var/log/lsAsset.log')
#logging.basicConfig(level=logging.ERROR, filename='./lsAsset.log')

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
    url = 'https://anypoint.mulesoft.com/exchange/api/v2/assets/search'
    method = 'GET'
    headers = {'Authorization': 'Bearer '+t}
    params = {}
    params['masterOrganizationId'] = m
    if o is not None:
        params['organizationId'] = o
    params['limit'] = 20
    params['offset'] = 0
    out = list()
    while True:
        req = urllib.request.Request(url+'?%s' % urllib.parse.urlencode(params),None,headers,None,False,method)
        try:
            with urllib.request.urlopen(req) as res:
                jsRes = json.loads(res.read().decode('utf-8'))
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
    url = 'https://anypoint.mulesoft.com/accounts/api/me'
    method = 'GET'
    headers = {'Authorization': 'Bearer '+t}
    req = urllib.request.Request(url, None,headers, None, False, method)
    try:
        with urllib.request.urlopen(req) as res:
            js = json.loads(res.read().decode('utf-8'))
        
        return js['user']['organizationId']
    except BaseException:
        print('Invalid credentials or bad response exception')
        raise
        #TODO: Handle Errors more granularly


def authenticatePassword(u,p):
    url = 'https://anypoint.mulesoft.com/accounts/login'
    method = 'POST'
    values = {'username': u, 'password': p}
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data, {}, None, False, method)
    try:
        with urllib.request.urlopen(req) as res:
            js = json.loads(res.read().decode('utf-8'))
        return js['access_token']
    except BaseException:
        print('Invalid credentials or bad response exception')
        raise
        #TODO: Handle Errors more granularly

def authenticateClientCredentials(ci,cs):
    url = 'https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token'
    method = 'POST'
    values = {'client_id': ci, 'client_secret': cs, 'grant_type': 'client_credentials'}
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data, {}, None, False, method)
    try:
        with urllib.request.urlopen(req) as res:
            js = json.loads(res.read().decode('utf-8'))
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

if __name__ == '__main__':
### Setup resources needed to run program
    args = initArgParse()

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
