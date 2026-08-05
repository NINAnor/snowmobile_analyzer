"""Minimal stub for the ``visdom`` package.

The vendored ``audioclip`` training code imports ``visdom`` on the
model-loading path, but the prediction flow never uses it. ``visdom``
cannot be built under uv, so this stub satisfies the import.
"""


class Visdom:
    pass
