from flask_restx import fields

from app.extensions import api


AUTH_LOGIN_SW_MODEL = api.model('AuthUserLogin', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

AUTH_TOKEN_SW_MODEL = api.model('AuthUserToken', {
    'token': fields.String(),
})

AUTH_REQUEST_RESET_PASSWORD_SW_MODEL = api.model('AuthUserResetPassword', {
    'email': fields.String(required=True),
})

AUTH_RESET_PASSWORD_SW_MODEL = api.model('AuthUserResetPasswordToken', {
    'password': fields.String(required=True),
})
