# Catalog resource ownership

This context distinguishes reviewed Pack content from its upstream sources and
the resources made available to a host through installation or on-demand access.

## Language

**Catalog Resource**:
A resource owned by a Pack in the Catalog Project, with its reviewed contract
and provenance.
_Avoid_: Installed resource when referring to the authored resource.

**Upstream Resource**:
A resource maintained by an independent upstream project from which a Catalog
Resource may be copied or adapted.

**Catalog Adaptation**:
A Catalog Resource maintained as a deliberate variation of an Upstream Resource.
_Avoid_: Exact copy when referring to an adaptation.

**Installed Resource**:
A resource made available to a host through a Pack installation.
_Avoid_: Catalog Resource when referring to the installed instance.

**On-demand Skill Access**:
Use of a Catalog Resource of kind skill without installing that resource in the
target project.

**Packy CLI Skill**:
The agent-facing skill that explains how to discover and obtain skills through
the Packy CLI.
