import nox


@nox.session(python=["3.12", "3.13"])
def tests(session) -> None:  # noqa: ANN001
    session.run("uv", "sync", external=True)
    session.run("uv", "run", "pytest", external=True)
