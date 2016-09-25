import json

import falcon
import jsonschema
from jsonschema.exceptions import ValidationError

from .jsonencoder import encoder as default_encoder


def require_json(req, resp, resource, params):
    if req.method in ('POST', 'PUT', 'PATCH'):
        if req.content_type is None or 'application/json' not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType(
                'This API only supports requests encoded as JSON.',
                href='http://docs.examples.com/api/json')


def parse_json(req, resp, resource, params):
    # if not json data, do nothing
    if req.content_type is None or 'application/json' not in req.content_type:
        return

    # req.stream corresponds to the WSGI wsgi.input environ variable,
    # and allows you to read bytes from the request body.
    #
    # See also: PEP 3333
    if req.content_length in (None, 0):
        # Nothing to do
        return

    body = req.stream.read()
    if not body:
        raise falcon.HTTPBadRequest('Empty request body',
                                    'A valid JSON document is required.')

    try:
        req.context['doc'] = json.loads(body.decode('utf-8'))

    except (ValueError, UnicodeDecodeError):
        raise falcon.HTTPError(falcon.HTTP_753,
                               'Malformed JSON',
                               'Could not decode the request body. The '
                               'JSON was incorrect or not encoded as '
                               'UTF-8.')


def validate_json(req, resp, resource, params):
    if hasattr(resource, "schema") and resource.schema is not None:
        try:
            jsonschema.validate(req.context["doc"], resource.schema)
        except ValidationError as e:
            raise falcon.HTTPBadRequest("Schema Mismatch", str(e))


def dump_json(req, resp, resource):
    if 'result' not in req.context:
        return

    if hasattr(resource, "json_encoder"):
        resp.body = json.dumps(req.context['result'], cls=resource.json_encoder)
    else:
        resp.body = default_encoder.dumps(req.context['result'])
