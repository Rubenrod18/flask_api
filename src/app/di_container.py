"""Module for managing dependency injections."""

from dependency_injector import containers, providers

from app import services
from app.helpers.otp_token import OTPTokenManager


class ServiceDIContainer(containers.DeclarativeContainer):
    """Service Dependency Injection Container.

    Notes
    -----
    If you define this class in repositories, serializers or services then it's going to fail because
    circular imports, it only can be used in blueprints.

    """

    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        modules=[
            '.blueprints.auth',
            '.blueprints.documents',
            '.blueprints.roles',
            '.blueprints.tasks',
            '.blueprints.users',
        ]
    )

    # Helpers
    otp_token_manager = providers.Factory(
        OTPTokenManager,
        secret_key=config.secret_key,
        salt=config.salt,
        expiration=config.expiration.as_int(),
    )

    # Services
    auth_service = providers.Factory(services.AuthService)
    document_service = providers.Factory(services.DocumentService)
    role_service = providers.Factory(services.RoleService)
    user_service = providers.Factory(services.UserService)
