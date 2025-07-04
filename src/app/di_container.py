"""Module for managing dependency injections."""

from dependency_injector import containers, providers

from app import services
from app.helpers.otp_token import OTPTokenManager
from app.providers.google_drive import GoogleDriveFilesProvider, GoogleDrivePermissionsProvider


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

    # Providers
    gdrive_files_provider = providers.Factory(
        GoogleDriveFilesProvider,
        credentials=None,
        service_account_path=config.gdrive.service_account_path,
        enable_google_drive=config.gdrive.enable,
    )
    gdrive_permissions_provider = providers.Factory(
        GoogleDrivePermissionsProvider,
        credentials=None,
        service_account_path=config.gdrive.service_account_path,
        enable_google_drive=config.gdrive.enable,
    )

    # Services
    auth_service = providers.Factory(services.AuthService)
    document_service = providers.Factory(
        services.DocumentService,
        gdrive_files_provider=gdrive_files_provider,
        gdrive_permissions_provider=gdrive_permissions_provider,
    )
    role_service = providers.Factory(services.RoleService)
    user_service = providers.Factory(services.UserService)
