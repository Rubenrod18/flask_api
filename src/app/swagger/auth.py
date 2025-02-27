from flask_restx import fields

from app.extensions import api

auth_login_sw_model = api.model(
    'AuthUserLogin',
    {
        'email': fields.String(required=True),
        'password': fields.String(required=True),
    },
)

auth_token_sw_model = api.model('AuthUserToken', {'access_token': fields.String(), 'refresh_token': fields.String()})

auth_user_reset_password_sw_model = api.model(
    'AuthUserResetPassword',
    {
        'email': fields.String(required=True),
    },
)

auth_user_reset_password_token_sw_model = api.model(
    'AuthUserResetPasswordToken',
    {'password': fields.String(required=True), 'confirm_password': fields.String(required=True)},
)
