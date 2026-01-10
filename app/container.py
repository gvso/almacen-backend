from typing import cast

from dependency_injector import containers, providers

from app.controllers.container import ControllerContainer
from app.repos.container import RepoContainer
from app.services.container import ServiceContainer


class ApplicationContainer(containers.DeclarativeContainer):
    repos = cast(RepoContainer, providers.Container(RepoContainer))
    services = cast(ServiceContainer, providers.Container(ServiceContainer))
    controllers = cast(
        ControllerContainer,
        providers.Container(ControllerContainer, repos=repos),
    )


def get_wire_container() -> ApplicationContainer:
    container = ApplicationContainer()
    container.wire(packages=["app.blueprints"])
    return container
