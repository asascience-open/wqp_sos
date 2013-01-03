from flask import render_template

from pyoos.collectors.wqp.wqp_rest import WqpRest

import dateutil.parser as dateparser
from datetime import timedelta
import pytz

class GetObservation(object):
    def __init__(self, request):
        self.offering = request.args.get("offering", request.args.get("OFFERING", request.args.get("Offering", None)))
        self.obs_props = request.args.get("observedproperty", request.args.get("OBSERVEDPROPERTY", request.args.get("observedProperty", None)))
        self.eventtime = request.args.get("eventtime", request.args.get("EVENTTIME", request.args.get("Eventtime", None)))

    def response(self):        
        if self.offering is None:
                return render_template("error.xml", parameter="offering", value="Value missing")
        if self.obs_props is None:
            return render_template("error.xml", parameter="observedProperty", value="Value missing")
        else:
            self.obs_props = list(set(self.obs_props.split(",")))
    
        wq = WqpRest()
        station = wq.get_metadata(siteid=self.offering)
        if station.failed:
            return render_template("error.xml", parameter="offering", value="Invalid value")

        activities = wq.get_data(siteid=self.offering).activities

        # Filter by observedProperties
        activities = [a for a in activities if len(set(self.obs_props) & set([p.name for p in a.results])) > 0]

        # Filter by eventtime
        if self.eventtime is not None and (isinstance(self.eventtime, unicode) or isinstance(self.eventtime, str)):
            if len(activities) > 0:
                if self.eventtime.lower() == "latest":
                    starting = max([a.start_time for a in activities])
                    ending = starting + timedelta(minutes=1)
                else:
                    starting = dateparser.parse(self.eventtime.split("/")[0])
                    ending = dateparser.parse(self.eventtime.split("/")[1])

                activities = [a for a in activities if starting <= a.start_time and a.start_time <= ending]

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
                if r.name in self.obs_props and r.name not in op_names:
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

        return render_template("getobservation.xml", min_time=min_time, max_time=max_time, station=station, data_block=data_block, observedProperties=set(ops))
