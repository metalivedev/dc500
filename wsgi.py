import json
import sys
from datetime import datetime
from os import stat

TAILSIZE=1000

def timestamp():
    return datetime.now().isoformat()

def perr(s):
    curtime=timestamp()
    # Uncomment the next line to print messages to stderr
    #sys.stderr.write(curtime+' PERR: '+s+'\n')

def getDCenv():
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
    return env

def getlogname(suffix,env):
    base='-'.join([env['DOTCLOUD_PROJECT'],
                   env['DOTCLOUD_ENVIRONMENT'],
                   env['DOTCLOUD_SERVICE_NAME'],
                   env['DOTCLOUD_SERVICE_ID'],
                   ])
    return base+suffix

def gettail(fname,length):
    filesize=stat(fname).st_size
    length=min(filesize,length)
    perr('Filename='+fname+' size='+str(filesize)+':'+str(length))

    with open(fname,'r') as f:
        f.seek(-length,2)
        rval=f.read(length)
    return '[tail of last '+str(length)+' bytes of '+fname+']\n[...]'+rval

def application(environ, start_response):
    status = '200 OK'
    logdir = '/var/log/nginx/'
    response_headers = [('Content-type', 'text/html')]

    env=getDCenv()
    query=environ['QUERY_STRING']

    if(len(query)):
        if('die' == query.lower()):
            sys.exit(timestamp()+' Real error generated by user click on "here".')
        if(query[0:3].isdigit()):
            status=query

    accesslog=logdir+getlogname('.access.log',env)
    access=gettail(accesslog,TAILSIZE)
    perr('accesslog='+access)

    errorlog=logdir+getlogname('.error.log',env)
    error=gettail(errorlog,TAILSIZE)
    perr('errorlog='+error)

    uwsgilog='/var/log/supervisor/uwsgi.log'
    uwsgi=gettail(uwsgilog,TAILSIZE)
    # No sense in doing a perr for uwsgi since perr goes to stderr goes to uwsgi log
    
    urlbase='http://'+environ['HTTP_HOST']

    start_response(status, response_headers)
    return [
        '<html><body>',
        'I just returned '+status+' at '+timestamp()+'<br>\n',
        'Reload with <a href="'+urlbase+'">200</a><br>\n',
        'Cause a real <a href="'+urlbase+'?die">500</a><br>\n',
        'Return a 500 as if from a function: <a href="'+urlbase+'?500">fake 500</a><br>\n',
        'Return a <a href="'+urlbase+'?502">502</a>(this will cause the service to go out of rotation for 30 seconds)<br>\n',
        '<h3>Access Log</h3><pre>',str(access),'</pre>\n',
        '<h3>Error Log </h3><pre>',str(error), '</pre>\n',
        '<h3>UWSGI Log </h3><pre>',str(uwsgi), '</pre>\n',
        '</body></html>\n'
        ]
