from flask import render_template

class GetCapabilities(object):
    def __init__(self, request):
        self.request = request

    def response(self):        
        return render_template("getcapabilities.xml")

