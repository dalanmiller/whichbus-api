from flask import Flask, jsonify, request
import sys
import requests
import pprint
import json
import os

wb = Flask(__name__)

AgencyMap = { 
    'KCM': 1, 
    'ST': 40,    
}

@wb.route("/")
def hello():
    return "Hello World!"

@wb.route("/routes")
@wb.route("/routes/<int:id>")
def routes(id = None):

    if id == None:
        rjson = requests.get('http://otp.whichb.us:8080/opentripplanner-api-webapp/ws/transit/routes', headers={'Content-Type':'application/json'})
        print rjson
        print rjson.headers

        old_json = json.loads(rjson.content)

        new_json = []

        for x in old_json['routes']:
            d = {}
            d.update({'id':x['TransitRoute']['id']['id']})
            d.update({'agency':x['TransitRoute']['id']['agency']})
            d.update({'shortname':x['TransitRoute']['routeShortName']})
            d.update({'longname':x['TransitRoute']['routeLongName']})
            d.update({'url':x['TransitRoute']['url']})
            new_json.append(d)

        return json.dumps(new_json)


    return "Routes coming soon"


@wb.route('/stops')
def stop():
    if 'lat' in request.args.keys() and 'lon' in request.args.keys():
        r = requests.get('http://otp.whichb.us:8080/opentripplanner-api-webapp/ws/transit/stopsNearPoint?lat=%s&lon=%s' % ( request.args['lat'], request.args['lon']) )

        rjson = json.loads(r.content)
        new_json = []

        pprint.pprint(rjson)

        for value in rjson['stops']:
            stop = value['Stop']
            new_json.append(
                dict(
                    name  = stop['stopName'],
                    code = stop['stopCode'],
                    lat = stop['lat'],
                    lon = stop['lon'],
                    id = stop['id']['id'],
                    agency = stop['id']['agency'],
                    routes = [dict(id=x['AgencyAndId']['id'], agency=x['AgencyAndId']['agencyId']) for x in stop['routes']]
                    )
                )

        return json.dumps(new_json)


    return 'Testing'

@wb.route("/stops/<id>")
@wb.route("/stops/<agency>/<id>")
def stops(id = None, agency = None):

    if id and agency:
        # rstop = requests.get('http://beta.whichb.us/stop/%s.json' % (id))
        return stops("%s_%s" % (AgencyMap[agency], id))
    elif id:
        print id
        rsched = requests.get('http://beta.whichb.us/stop/%s/schedule.json' % (id))
        rstop = requests.get('http://beta.whichb.us/stop/%s.json' % (id))
        schedjson = json.loads(rsched.content)
        stopjson = json.loads(rstop.content)
        new_json = {}

        stopjson.pop('distance')
        stopjson.pop('routes')

        return jsonify(stopjson)

    return "Your stop request failed =("


if __name__ == "__main__":
    if '--debug' in sys.argv:
        wb.debug = True
    port = int(os.environ.get('PORT', 5000))
    wb.run(host='0.0.0.0', port=port)