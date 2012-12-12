from flask import render_template, make_response, redirect, url_for, request, Response
from wqp_sos import app

from wqp_sos.requests.get_capabilities import GetCapabilities
from wqp_sos.requests.describe_sensor import DescribeSensor
from wqp_sos.requests.get_observation import GetObservation

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('sos'))
    
@app.route('/sos', methods=['GET'])
def sos():
    service = request.args.get("service", request.args.get("SERVICE", request.args.get("Service", None)))
    if service is None:
        return Response(render_template("error.xml", parameter="service", value="Value missing"), mimetype='text/xml')

    req = request.args.get("request", request.args.get("REQUEST", request.args.get("Request", None)))
    if req is None:
        return Response(render_template("error.xml", parameter="request", value="Value missing"), mimetype='text/xml')

    if req.lower() == "getcapabilities":
        gc = GetCapabilities(request)
        return Response(gc.response(), mimetype='text/xml')

    elif req.lower() == "describesensor":
        ds = DescribeSensor(request)
        return Response(ds.response(), mimetype='text/xml')

    elif req.lower() == "getobservation":
        go = GetObservation(request)
        return Response(go.response(), mimetype='text/xml')
            
    else:
        return Response(render_template("error.xml", parameter="request", value="Invalid value"), mimetype='text/xml')

@app.route('/crossdomain.xml', methods=['GET'])
def crossdomain():
    domain = """
    <cross-domain-policy>
        <allow-access-from domain="*"/>
        <site-control permitted-cross-domain-policies="all"/>
        <allow-http-request-headers-from domain="*" headers="*"/>
    </cross-domain-policy>
    """
    response = make_response(domain)
    response.headers["Content-type"] = "text/xml"
    return response
