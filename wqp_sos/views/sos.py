from flask import render_template, make_response, redirect, url_for, request, Response
from wqp_sos import app

from pyoos.collectors.wqp.wqp_rest import WqpRest
import dateutil.parser as dateparser
from datetime import timedelta
import pytz

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('sos'))
    
@app.route('/sos', methods=['GET'])
def sos():
    service = request.args.get("service", request.args.get("SERVICE", request.args.get("Service", None)))
    if service is None:
        return Response(render_template("error.xml", parameter="service", value=service), mimetype='text/xml')

    req = request.args.get("request", request.args.get("REQUEST", request.args.get("Request", None)))
    if req is None:
        return Response(render_template("error.xml", parameter="request", value=req), mimetype='text/xml')

    if req.lower() == "getcapabilities":
        return Response(render_template("getcapabilities.xml"), mimetype='text/xml')

    if req.lower() == "describesensor" or req.lower() == "getobservation":

        procedure = request.args.get("procedure", request.args.get("PROCEDURE", request.args.get("Procedure", None)))
        offering = request.args.get("offering", request.args.get("OFFERING", request.args.get("Offering", None)))
        obs_props = request.args.get("observedproperty", request.args.get("OBSERVEDPROPERTY", request.args.get("observedProperty", None)))

        if req.lower() == "describesensor":
            if procedure is None:
                return Response(render_template("error.xml", parameter="procedure", value=procedure), mimetype='text/xml')
            siteid = procedure

        if req.lower() == "getobservation":
            if offering is None:
                return Response(render_template("error.xml", parameter="offering", value=offering), mimetype='text/xml')
            if obs_props is None:
                return Response(render_template("error.xml", parameter="observedProperty", value=op), mimetype='text/xml')
            else:
                obs_props = list(set(obs_props.split(",")))

            siteid = offering
    
        wq = WqpRest()
        station = wq.get_metadata(siteid=siteid)
        activities = wq.get_data(siteid=siteid).activities

        if req.lower() == "describesensor":
            # Get unique observedProperties
            ops = []
            op_names = []
            for a in activities:
                for r in a.results:
                    if r.name not in op_names:
                        op_names.append(r.name)
                        ops.append(r)

            return Response(render_template("describesensor.xml", station=station, observedProperties=set(ops)), mimetype='text/xml')
            
        elif req.lower() == "getobservation":
            # Filter by observedProperties
            activities = [a for a in activities if len(set(obs_props) & set([p.name for p in a.results])) > 0]

            # Filter by eventtime
            eventtime = request.args.get("eventtime", request.args.get("EVENTTIME", request.args.get("Eventtime", None)))

            if eventtime is not None and (isinstance(eventtime, unicode) or isinstance(eventtime, str)):
                if len(activities) > 0:
                    if eventtime.lower() == "latest":
                        starting = max([a.start_time for a in activities])
                        ending = starting + timedelta(minutes=1)
                    else:
                        starting = dateparser.parse(eventtime.split("/")[0])
                        ending = dateparser.parse(eventtime.split("/")[1])

                    activities = [a for a in activities if starting <= a.start_time and a.start_time < ending]

            min_time = "never"
            max_time = "never"
            if len(activities) > 0:
                # Extract timerange using Python here, instead of in Jinja2
                all_times = [a.start_time for a in activities]
                min_time = min(all_times)
                max_time = max(all_times)

            # Get observedProperties
            ops = []
            op_names = []
            for a in activities:
                for r in a.results:
                    if r.name in obs_props and r.name not in op_names:
                        op_names.append(r.name)
                        ops.append(r)
                    
            rows = []
            for a in activities:
                match = False
                row = [(a.start_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))]
                for obp in ops:
                    for r in a.results:
                        if r.name == obp.name:
                            row.append(r.value)
                            match = True
                            break
                    if match == True:
                        break
                    else:
                        row.append("None")
                rows.append(",".join(row))

            data_block = "\n".join(rows)

            return Response(render_template("getobservation.xml", min_time=min_time, max_time=max_time, station=station, data_block=data_block, observedProperties=set(ops)), mimetype='text/xml')

    else:
        return Response(render_template("error.xml", parameter="request", value=req), mimetype='text/xml')

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
