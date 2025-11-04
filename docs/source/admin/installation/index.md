# Installation

```{important}
Please note that Pytition uses a “plug and play” approach (simple default configurations) to facilitate installation and discovery, which is **NEITHER SECURE NOR EFFICIENT**. When you are ready, please refer to these [production recommendations](../configuration/prod.md) for safe installation.
```

This documentation is designed for **two types of installations**:

- actual **production use**, which must be efficient and secure
- **quick installation** for beta testing the tool, for example.

If you plan to install Pytition for editing source code purpose, or even contributing to it, please refer to the [developer guides](../../dev/index.md).

## Installation methods

You can install Pytition in various ways, depending on your needs and environment:

- [**Manual installation**](./manual.md): for maximum control and flexibility. Suitable for production environments where you want to customize every aspect of the installation.
- [**Docker installation**](./docker.md): using Docker containers for easy deployment and management. Ideal for those familiar with containerization.
- [**Multi-domain installation**](./multi_domain.md): to host multiple Pytition instances on a single server. Useful for service providers (like [CHATONS](https://www.chatons.org/)).
- [**YunoHost installation**](./yunohost.md): a simplified installation method using the YunoHost platform. Perfect for users seeking an easy setup process.

```{toctree}
:maxdepth: 2
:hidden:

manual
docker
multi_domain
yunohost
```
