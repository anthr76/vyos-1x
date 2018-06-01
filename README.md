# vyos-1x: VyOS 1.2.0+ configuration scripts and data

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=vyos%3Avyos-1x&metric=coverage)](https://sonarcloud.io/component_measures?id=vyos%3Avyos-1x&metric=coverage)

VyOS 1.1.x had its codebase split into way too many submodules for no good reason, which made it hard
to navigate or write meaningful changelogs. As the code undergoes rewrite in the new style in VyOS 1.2.0+,
we consolidate the rewritten code in this package.

If you just want to build a VyOS image, the repository you want is [vyos-build](https://github.com/vyos/vyos-build).
If you also want to contribute to VyOS, read on.

## Package layout

```
interface-definitions  # Configuration interface (i.e. conf mode command) definitions
op-mode-definitions    # Operational command definitions
src
    conf_mode/  # Configuration mode scripts
    op_mode/    # Operational mode scripts
    completion/ # Completion helpers
    validators/ # Value validators
    helpers/    # Misc helpers
    migration-scripts # Migration scripts
    tests/      # Unit tests

python/  # Python modules

scripts/ # Build-time scripts
schema/  # XML schemas
```

## Interface/command definitions

Raw node.def files for the old backend are no longer written by hand or generated by custom sciprts.
They are all now produced from a unified XML format that supports a strict subset of the old backend
features. In particular, it intentionally does not support embedded shell scripts, default values,
and value "types", instead delegating those tasks to external scripts.

Configuration interface definitions must conform to the schema found in schema/interface_definition.rng
and operational command definitions must conform to schema/op-mode-definition.rng
Schema checks are performed at build time, so a package with malformed interface definitions will not build.

## Configuration scripts

The guidelines in a nutshell:

* Use separate functions for retrieving configuration data, validating it, and generating taret config
* Use a template processor when the format is more complex than just one line (jinja2 and pystache are acceptable options) 

## Tests

Tests are executed at build time, you can also execute them by hand with:

```
make test
```
