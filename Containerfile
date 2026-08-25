# build
FROM python:3.13-slim AS build
WORKDIR /build

RUN pip install --no-cache-dir build pytest

COPY . .
RUN pip install --no-cache-dir . ".[dev]"
RUN pytest -v
RUN python -m build --wheel

# runtime
FROM python:3.13-slim AS runtime
WORKDIR /runtime

RUN useradd --create-home --shell /usr/sbin/nologin rsml

COPY --from=build /build/dist/*.whl /tmp/

RUN pip install --no-cache-dir /tmp/*.whl
RUN rm -rf /tmp/

RUN mkdir -p /var/lib/rsml
RUN chown rsml:rsml /var/lib/rsml

USER rsml

WORKDIR /home/rsml
VOLUME [ "/var/lib/rsml" ]
ENV RSML_CONFIG=/home/rsml/rsml.toml

EXPOSE 8080 8024

ENTRYPOINT [ "rsml" ]
CMD [ "http" ]
