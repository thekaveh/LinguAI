"""Design tokens — single source of truth for spacing, radius, shadow, motion."""

SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32}
RADIUS  = {"sm": 8, "md": 12, "lg": 14}
SHADOW  = {
    "xs": "0 1px 2px rgba(0,0,0,0.20)",
    "sm": "0 2px 6px rgba(0,0,0,0.25)",
    "md": "0 8px 24px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.40)",
}
MOTION  = {"fast_ms": 120, "slow_ms": 240}
