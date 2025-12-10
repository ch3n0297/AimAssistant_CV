# Core modules for Aim Assist System
# Use lazy imports to avoid issues when X display is not available

__all__ = [
    'ScreenCapture',
    'EnemyDetector',
    'Detection',
    'TargetSelector',
    'AimController',
    'MouseController',
]


def __getattr__(name):
    """Lazy import to avoid immediate X display requirement"""
    if name == 'ScreenCapture':
        from .capture import ScreenCapture
        return ScreenCapture
    elif name == 'EnemyDetector':
        from .detector import EnemyDetector
        return EnemyDetector
    elif name == 'Detection':
        from .detector import Detection
        return Detection
    elif name == 'TargetSelector':
        from .target_selector import TargetSelector
        return TargetSelector
    elif name == 'AimController':
        from .controller import AimController
        return AimController
    elif name == 'MouseController':
        from .mouse_control import MouseController
        return MouseController
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
