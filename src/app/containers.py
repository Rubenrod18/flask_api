"""Containers module."""

from dependency_injector import containers, providers

from app import serializers, services
from app.helpers.otp_token import OTPTokenManager


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        modules=[
            '.blueprints.auth',
            '.blueprints.documents',
            '.blueprints.roles',
            '.blueprints.tasks',
            '.blueprints.users',
            '.serializers.auth',
        ]
    )

    # Helpers
    otp_token_manager = providers.Factory(
        OTPTokenManager,
        secret_key=config.secret_key,
        salt=config.salt,
        expiration=config.expiration.as_int(),
    )

    # Serializers
    document_serializer = providers.Factory(serializers.DocumentSerializer)
    document_serializer.add_attributes(exclude=('internal_filename',))
    role_serializer = providers.Factory(serializers.RoleSerializer)
    user_serializer = providers.Factory(serializers.UserSerializer)

    # Services
    auth_service = providers.Factory(services.AuthService)
    document_service = providers.Factory(services.DocumentService)
    role_service = providers.Factory(services.RoleService)
    task_service = providers.Factory(services.TaskService)
    user_service = providers.Factory(services.UserService)
