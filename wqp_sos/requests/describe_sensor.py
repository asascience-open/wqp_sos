from flask import render_template

from pyoos.collectors.wqp.wqp_rest import WqpRest

class DescribeSensor(object):
    def __init__(self, request):
        self.procedure = request.args.get("procedure", request.args.get("PROCEDURE", request.args.get("Procedure", None)))

    def response(self):
        if self.procedure is None:
            return render_template("error.xml", parameter="procedure", value="Value missing")

        wq = WqpRest()
        station = wq.get_metadata(siteid=self.procedure)
        if station.failed:
            return render_template("error.xml", parameter="procedure", value="Invalid value")
            
        activities = wq.get_data(siteid=self.procedure).activities

        # Get unique observedProperties
        ops = []
        op_names = []
        for a in activities:
            for r in a.results:
                if r.name not in op_names:
                    op_names.append(r.name)
                    ops.append(r)

        return render_template("describesensor.xml", station=station, observedProperties=set(ops))