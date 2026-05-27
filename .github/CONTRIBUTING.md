# Contributing to OFP Linux Server Project

We welcome any contributions to the Operation Flashpoint Linux Server project, whether in the form of bug reports, feature suggestions, Docker improvements, or script submissions. When submitting any of those, please follow this documentation to help speed up the process.

# Reporting Bugs

A bug is when the server software does not behave in a way that is expected. It is **not** invalid server configurations, missing game files, or network issues which render the server unable to start.

If you believe you have located a bug in the OFP Linux server Docker image or startup scripts, please report it to the [GitHub Issues](https://github.com/igiteam/ofp-linux-docker/issues).

**Please make sure there is not an issue for your specific bug already!** If you find that someone else has reported a bug you have, please comment on that issue stating you have replicated that bug. Do not make a new issue.

When submitting those bugs, follow these standards:

- The title of the issue should **clearly** and **quickly** explain the issue. A good title would be "Server crashes when loading custom mission with missing addons" or "Container fails to report to OpenSpy master server".

- The description should contain the following information:
  - A complete description of the problem. This should explain what you expect the server to do and what actually happened.
  - Steps to reproduce the bug. It is hard to figure out what the bug truly is if we cannot do it ourselves.
  - Server logs from `docker logs <container_name>`
  - Your `server.cfg` configuration (with passwords redacted)
  - The command used to start the container
  - OFP version (1.96, 1.99, 2.01, etc.)

# How to Contribute

When submitting new code, Docker improvements, or templates to the project, you **must** follow both the standards outlined later in this documentation, along with the following:

- All PRs must contain a reference to an **existing** issue. If there is no issue for your PR to reference, then create a new issue, following the guidelines above.

- PRs may only contain **1** feature, enhancement, or bug fix. Kitchen sinks will be thrown out the window.

## Contribution Areas

We welcome contributions in these specific areas:

| Area                  | Description                                             |
| --------------------- | ------------------------------------------------------- |
| Dockerfile            | Improvements to the OFP Linux server container build    |
| Entrypoint Scripts    | Better config handling, signal trapping, logging        |
| PufferPanel Templates | New game mode templates or improved variables           |
| OpenSpy Integration   | Better reporting, heartbeat handling, API compatibility |
| Documentation         | Fixes, clarifications, or new guides                    |
| Testing               | Automated tests for container builds and server startup |

## Code Standards

### Dockerfile Standards

- Use specific base image tags (not `latest` unless justified)
- Keep layers minimal by combining `RUN` commands
- Clean up apt cache in the same layer
- Document why each dependency is needed

### Bash Script Standards

- Use `#!/bin/bash` shebang
- Enable `set -e` for error handling
- Quote all variables
- Use `[[ ]]` instead of `[ ]` for tests
- Provide helpful error messages

### Template Standards

- Include all required fields: `type`, `display`, `install`, `run`, `data`
- Use descriptive variable names
- Provide sensible defaults
- Document any special requirements

# Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes locally
5. Commit with a clear message (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

# Testing Your Changes

Before submitting a PR, test your changes:

# Test Docker build

docker build -t ofp-server:test .

# Test container startup

docker run -d --name ofp-test -p 2302:2302/udp -e HOSTNAME="Test Server" ofp-server:test

# Check logs for errors

docker logs ofp-test

# Verify server responds

nc -u -v localhost 2303

# Clean up

docker stop ofp-test && docker rm ofp-test
