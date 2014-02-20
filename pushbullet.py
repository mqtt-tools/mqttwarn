# -*- coding: utf-8 -*-
try:
    from urllib.request import Request, urlopen
except:
    from urllib2 import Request, urlopen

from base64 import encodestring, b64encode
import json
import mimetypes
import os

HOST = "https://api.pushbullet.com/api";

class PushBulletError():
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class PushBullet():
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _request(self, url, postdata=None):
        request = Request(url)
        request.add_header("Accept", "application/json")
        request.add_header("Content-type","application/json");
        auth = "%s:" % (self.apiKey)
        auth = auth.encode('ascii')
        auth = b64encode(auth)
        auth = b"Basic "+auth
        request.add_header("Authorization", auth)
        request.add_header("User-Agent", "pyPushBullet")
        if postdata:
            postdata = json.dumps(postdata)
            postdata = postdata.encode('utf-8')
        response = urlopen(request, postdata)
        data = response.read()
        data = data.decode("utf-8")
        j = json.loads(data)
        return j
        
    def _request_multiform(self, url, postdata, files):
        request = Request(url)
        content_type, body = self._encode_multipart_formdata(postdata, files)
        request.add_header("Accept", "application/json")
        request.add_header("Content-type", content_type);
        auth = "%s:" % (self.apiKey)
        auth = auth.encode('ascii')
        auth = b64encode(auth)
        auth = b"Basic "+auth
        request.add_header("Authorization", auth)
        request.add_header("User-Agent", "pyPushBullet")
        response = urlopen(request, body)
        data = response.read()
        data = data.decode("utf-8")
        j = json.loads(data)
        return j
        
    def _encode_multipart_formdata(self, fields, files):
        '''
        from http://mattshaw.org/news/multi-part-form-post-with-files-in-python/
        '''
        def guess_type(filename):
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        BOUNDARY = '----------bound@ry_$'
        CRLF = '\r\n'
        L = []
        for key,value in fields.iteritems():
            L.append('--'+BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"'%(key))
            L.append('')
            L.append(str(value))
            
        for (key, filename, value) in files:
            L.append('--'+BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"'%(key, filename))
            L.append('Content-Type: %s'%(guess_type(filename)))
            L.append('')
            L.append(value)
            
        L.append('--'+BOUNDARY+'--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def getDevices(self):
        return self._request(HOST + "/devices")["devices"]

    def pushNote(self, device, title, body):
        data = {'type'      : 'note',
                'device_id' : device,
                'title'     : title,
                'body'      : body}
        return self._request(HOST + "/pushes", data)

    def pushAddress(self, device, name, address):
        data = {'type'      : 'address',
                'device_id' : device,
                'name'      : name,
                'address'   : address}
        return self._request(HOST + "/pushes", data)

    def pushList(self, device, title, items):
        data = {'type'      : 'list',
                'device_id' : device,
                'title'     : title,
                'items'     : items}
        return self._request(HOST + "/pushes", data)


    def pushLink(self, device, title, url):
        data = {'type'      : 'link',
                'device_id' : device,
                'title'     : title,
                'url'     : url}
        return self._request(HOST + "/pushes", data)

    def pushFile(self, device, file):
        data = {'type'      : 'file',
                'device_id' : device}
        filedata = ''
        with open(file, "rb") as f:
            filedata = f.read()
        return self._request_multiform(HOST + "/pushes", data, [('file', os.path.basename(file), filedata)])
