# utils.py
from flask import request, make_response, jsonify
import xmltodict

def to_xml(data, root='response'):
    # xmltodict requires dict
    return xmltodict.unparse({root: data}, pretty=True)

def respond(data, status=200, root='response'):
    fmt = request.args.get('format', 'json').lower()
    if fmt == 'xml':
        xml_str = to_xml(data, root=root)
        resp = make_response(xml_str, status)
        resp.headers['Content-Type'] = 'application/xml'
        return resp
    else:
        resp = make_response(jsonify(data), status)
        resp.headers['Content-Type'] = 'application/json'
        return resp
