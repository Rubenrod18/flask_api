"""Containers module."""

from dependency_injector import containers, providers

from app import serializers, services


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            '.blueprints.auth',
            '.blueprints.documents',
            '.blueprints.roles',
            '.blueprints.tasks',
            '.blueprints.users',
        ]
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
