
# coding=utf-8

import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, request
import urllib2
from google.appengine.api import mail
app = Flask(__name__)

from google.appengine.ext import ndb
class acticle(ndb.Model):
    """Sub model for representing an author."""
    title = ndb.StringProperty(indexed=False)
    timestr = ndb.StringProperty(indexed=False)
    acticlestr = ndb.StringProperty(indexed=False)
    mail = ndb.StringProperty(indexed=False)

# class mailinfor(ndb.Model):
#     mailstr = ndb.StringProperty(indexed=False)


@app.route('/')
def hello_world():
    return 'Hello World!'
#
# @app.route('/mail')
# def intmail():
#     try:
#         mailinforlist = mailinfor.query(ancestor=ndb.Key('mail', 'mailinfor'))
#         m = mailinforlist.fetch(1)
#         maillist = m[0]
#     except:
#         maillist = mailinfor(parent=ndb.Key('mail', 'mailinfor'))
#         maillist.mailstr=''
#         maillist.put()
#     return maillist.mailstr

@app.route('/check')
def check():
    global timestr, acticlestr
    id = request.args.get('id', '')
    try:
        req = urllib2.Request('http://book.qidian.com/info/%s#Catalog' % id)
        response = urllib2.urlopen(req, timeout=60)
        responseStr = response.read()


        titlenum_start = str(responseStr).rfind('最近更新') + len('最近更新')
        subresponseStr = responseStr[titlenum_start:]
        timestr = subresponseStr[0:19]
        titlenum_start = str(subresponseStr).find('title="') + len('title="')
        titlenum_stop = str(subresponseStr).find('"', titlenum_start)

        titlestr = subresponseStr[titlenum_start:titlenum_stop].replace('\r','').replace('\n','')

        acticlestr = titlestr


    except urllib2.URLError, e:
        resultstr = 'error'
        return resultstr



    try:
        ar_query = acticle.query(ancestor=ndb.Key(id, 'acticle'))
        arlist = ar_query.fetch(1)
        ar = arlist[0]
        if ar.titlestr == titlestr:
            return ('same:%s \n %s' % (titlestr,acticlestr))
    except:
        ar = acticle(parent=ndb.Key(id, 'acticle'))


    ar.acticlestr = acticlestr.replace('<br>', '\n\r').replace('&nbsp;', ' ')
    ar.timestr = ''
    ar.title = titlestr


    if ar.mail != None and ar.mail != '':
        message = mail.EmailMessage(subject='[更新提醒]' +titlestr + ' ')
        message.sender = 'wuzhi2010@gmail.com'
        message.to = ar.mail
        message.body = ar.acticlestr
        message.send()
    else:
        ar.mail = ''

    ar.put()
    return ('change:%s %s \n %s' % (titlestr, timestr,acticlestr))

if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=True)
