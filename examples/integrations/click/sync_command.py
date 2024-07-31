from abc import abstractmethod
from typing import Protocol

import click

from dishka import make_container, Provider, Scope, provide, FromDishka
from dishka.integrations.click import setup_dishka


class DbGateway(Protocol):
    @abstractmethod
    def get(self) -> str:
        raise NotImplementedError


class FakeDbGateway(DbGateway):
    def get(self) -> str:
        return "Hello123"


class Interactor:
    def __init__(self, db: DbGateway):
        self.db = db

    def __call__(self) -> str:
        return self.db.get()


class AdaptersProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_db(self) -> DbGateway:
        return FakeDbGateway()


class InteractorProvider(Provider):
    i1 = provide(Interactor, scope=Scope.REQUEST)


@click.group()
def cli(): ...


@cli.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count: int, name: str, interactor: FromDishka[Interactor]):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
        click.echo(interactor())


if __name__ == "__main__":
    container = make_container(AdaptersProvider(), InteractorProvider())
    setup_dishka(container=container, command=cli, auto_inject=True)
    try:
        cli()
    finally:
        container.close()
