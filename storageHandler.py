#!/usr/bin/env python3

import sqlite3

class StorageHandler(object):

    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row

        cur = self.conn.cursor()

        cur.execute('create table if not exists assets(organizationId text, groupId text, assetId text, version text, minorVersion text, versionGroup text, description text, isPublic integer, name text, contactName text, contactEmail text, type text, status text, createdAt text, createdById text, UNIQUE(organizationId, groupId, assetId, version, minorVersion) ON CONFLICT IGNORE)')
        self.conn.commit()
    
    def __del__(self):
        self.conn.close()

    def upsertAsset(self, organizationId, groupId, assetId, version, minorVersion, versionGroup, description, isPublic, name, contactName, contactEmail, type, status, createdAt, createdById):
        cur = self.conn.cursor()
        
        cur.execute('INSERT or IGNORE INTO assets (organizationId, groupId, assetId, version, minorVersion, versionGroup, description, isPublic, name, contactName, contactEmail, type, status, createdAt, createdById) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(organizationId, groupId, assetId, version, minorVersion, versionGroup, description, isPublic, name, contactName, contactEmail, type, status, createdAt, createdById))
        self.conn.commit()
        cur.close()
        
    def getAsset(self, assetId):
        cur = self.conn.cursor()

        res = cur.execute('SELECT * from assets where assetId=?', (assetId,)).fetchall()
        cur.close()
        return res

    def getAllAssets(self):
        cur = self.conn.cursor()

        res = cur.execute('SELECT * from assets').fetchall()
        cur.close()
        return res
    
    def toDict(self,l):
        d = dict()
        for k in l.keys():
            d[k] = l[k]
        return d;


if __name__ == '__main__':
    ### tests can be added here if needed and run directly
