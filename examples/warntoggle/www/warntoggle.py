#!/usr/bin/python

import json

def index(req):

    filename = "/var/www/html/warntoggle/warntoggle.json"
    writetoggles = {}
    readtoggles = {} 
    scriptname = __file__.split('/')[-1:][0]

    # write form data to the file if applicable

    if bool(req.form): 

        for k,v in req.form.items():
            writetoggles[k] = eval(str(v))

        with open(filename, 'w') as outfile: 
            json.dump(writetoggles, outfile)
            outfile.close()

    # read data from the file

    with open(filename, 'r') as infile:
        readtoggles = json.load(infile)
        infile.close()

    # display the form

    html  = "<html><body><h1>mqttwarn notification toggles</h1>"
    html += "<table>"
    html += "<form action=\"" + scriptname + "\" method=\"post\">"

    for key in sorted(readtoggles.keys()):
        if readtoggles[key] == True:
            block_checked = " checked"
            notify_checked = ""
        else:
            block_checked = ""
            notify_checked = " checked"

        html += "<tr><td>" + key + "</td><td><input type='radio' name='" + key + "' value='True'" + block_checked + ">Block <input type='radio' name='" + key + "' value='False'" + notify_checked+ ">Notify</td></tr>"

    html += "</table><br/>"
    html += "<nobr><input type='submit' value='Submit'> <a href='" + scriptname + "'>reload</a></nobr>"
    html += "</form>"
    html += "</body></html>"

    return html 
