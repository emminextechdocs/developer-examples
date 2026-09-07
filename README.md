# Developer examples

Small, testable examples from [Emminex Techdocs](https://emminextechdocs.com), built to make implementation details easy to inspect.

## Examples

| Example | What you will learn |
| --- | --- |
| [HTTP JSON client](http-json-client/README.md) | Handle HTTP errors, malformed JSON, timeouts, and local integration tests |

This collection starts with one tested example. More examples should be added only after their prerequisites, success path, and failure paths have been checked. It is not a downloadable version of every blog tutorial.

## Run all tests

Prerequisites: Node.js 22 or 24. No packages, accounts, or external API keys are needed.

```sh
node --test
```

The tests start a temporary server on `127.0.0.1`, make requests to it, then close it. They do not call external services.

## Add an example

Create a self-contained directory with a README, source code, automated tests, supported versions, expected output, cleanup instructions, and links to official documentation. State production limitations. Never commit `.env` files or client material.

[Read our developer guides](https://emminextechdocs.com/blog) · [Browse documentation templates](https://github.com/emminextechdocs/documentation-templates)
