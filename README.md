# Developer examples

Small, testable examples from [Emminex Techdocs](https://emminextechdocs.com), built to make implementation details easy to inspect.

## Examples

| Example | What you will learn |
| --- | --- |
| [Senior developer deep dives](deep-dives/README.md) | PostgreSQL, Redis, Kafka, RabbitMQ, Prometheus, Grafana, NGINX, OpenTelemetry, BuildKit, and Kubernetes failure behavior |
| [HTTP JSON client](http-json-client/README.md) | Handle HTTP errors, malformed JSON, timeouts, and local integration tests |

The HTTP client runs with Node alone. The [senior developer deep dives](deep-dives/README.md) add ten Docker-backed experiments with separate prerequisites and recorded failure-path evidence.

## Run the HTTP client tests

Prerequisites: Node.js 22 or 24. No packages, accounts, or external API keys are needed.

```sh
node --test
```

The tests start a temporary server on `127.0.0.1`, make requests to it, then close it. They do not call external services.

## Add an example

Create a self-contained directory with a README, source code, automated tests, supported versions, expected output, cleanup instructions, and links to official documentation. State production limitations. Never commit `.env` files or client material.

[Read our developer guides](https://emminextechdocs.com/blog) · [Browse documentation templates](https://github.com/emminextechdocs/documentation-templates)

## License

This repository's original code, documentation, and templates are available under the [MIT License](LICENSE). You may use, modify, and redistribute them, including commercially, provided you retain the copyright and license notice.

This license does not grant trademark rights to the Emminex Techdocs name or logo, or license content on linked websites. Third-party material retains its own license.
