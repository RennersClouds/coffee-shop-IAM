import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
# from urllib.request import urlopen



'''
THIS IS AN INTENDED ADDED JWT FOR PROJECT SUBMISSION REVIEW PURPOSE ONLY!!

eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjlPTnhPZFYtS3MzN0NjbnhnN3cxNSJ9.eyJpc3MiOiJodHRwczovL2Rldi1jbWM2cDVrOC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjMwYTNkNTk3NTE1OTNlOGM3MGZlNmY5IiwiYXVkIjoibXlhcHAiLCJpYXQiOjE2NjE2Nzk0NjYsImV4cCI6MTY2MTY4NjY2NiwiYXpwIjoiOGZpMVlkdnVLVkpxTnQxcG9VVVlCYkJscU9yUlR5Z20iLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.cW5UQJpjBBCkelpYaJOPThm8B6OggMbpuyorOvQH0JN_EFOHghukQJoLldvuJtCnCVeNORJUuKPP45Q17kiHUF-D3uEFADopzx6ljx33kOOsdXdFMmDGfUoAlcevWEXe07UuKsGUafmKixP1Jox8hnKND5Q35U6m1V8X5cEbRq7EwFNARthIdaIJmAXVbZrtwf9ciSrCNyhieecuYTr_yy6sBfisXPzew-L126uloqk4_e4S9LXKC6abtJEtlUHi6OltarOfx1Xzh_bYIZ1cAbklfDQRf7xk4FAN-i13t13ydYAtPMA7dTM12QqLr6qNmCnGnv7Qhy5Xva80Xi9Akw

'''


AUTH0_DOMAIN = 'dev-cmc6p5k8.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'myapp'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError({
            'success': False,
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
 
    header = request.headers['Authorization']
    split_header = header.split(' ')
    if len(split_header) != 2:
        raise AuthError({
            'success': False,
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    elif split_header[0].lower() != 'bearer':
        raise AuthError({
            'success': False,
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
 
    token = split_header[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):

    if 'permissions' not in payload:
        raise AuthError({
            'success': False,
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'success': False,
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True
    

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):

    url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    the_keys = json.loads(url.read())
    unverified_header = jwt.get_unverified_header(token)
    
    rsa_key = {}
    
    if 'kid' not in unverified_header:
        raise AuthError({
            'success': False,
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)


    for key in the_keys['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
                raise AuthError({
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator