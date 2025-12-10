# Overlay modules for Aim Assist System
# Use lazy imports to avoid issues when X display is not available

__all__ = ['OverlayWindow', 'OverlayManager']


def __getattr__(name):
    """Lazy import to avoid immediate X display requirement"""
    if name == 'OverlayWindow':
        from .hud import OverlayWindow
        return OverlayWindow
    elif name == 'OverlayManager':
        from .hud import OverlayManager
        return OverlayManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
