"""Sibling observer demo — tests L0 (direct) and L1 (ancestor) observation.

Demonstrates viewport-fit height measurement with two observation scenarios:
- L0: Direct sibling toggle (info bar beside the target)
- L1: Ancestor-level sibling toggle (header above the target's wrapper)

The target is nested inside a wrapper div to test that the ancestor-walking
sibling observer correctly detects changes at all DOM levels.
"""

from fasthtml.common import Div, H2, P, Span, Button

from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_sizes, btn_styles

from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, flex_direction, flex_wrap, flex, items, gap,
)
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow, display_tw
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_viewport_fit.models import ViewportFitConfig
from cjm_fasthtml_viewport_fit.components import render_viewport_fit_script


def setup():
    """Set up the sibling observer demo.

    Returns dict with config, page_content callable, title, and description.
    """
    config = ViewportFitConfig(
        namespace="sibling",
        target_id="sibling-target",
        debug=True,
    )

    content_items = [
        P(f"Item {i + 1}: Sample content that fills the viewport-fitted area",
          cls=combine_classes(p(2), m.y(1), bg_dui.base_200, rounded.lg))
        for i in range(50)
    ]

    def page_content():
        return Div(
            # Header with L1 toggle
            Div(
                Div(
                    H2("Sibling Observer Demo",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    Button("Toggle Header Info (L1)",
                           onclick="document.getElementById('header-extra').classList.toggle('hidden')",
                           cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                    cls=combine_classes(flex_display, items.center, gap(4)),
                ),
                P("The blue area fills remaining viewport height. "
                  "Toggle buttons add/remove content to test sibling observation at different DOM levels. "
                  "Check console for debug output.",
                  cls=combine_classes(text_dui.base_content, font_size.sm, m.t(2))),
                Div(
                    P("This extra header content is a L1 ancestor-level sibling of the target. "
                      "The target is nested inside a wrapper div, so this is NOT a direct sibling. "
                      "The ancestor-walking observer detects this change.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    id="header-extra",
                    cls=combine_classes(display_tw.hidden, p(3), bg_dui.warning.opacity(20),
                                        border.t(), border_dui.warning, rounded.lg, m.t(2)),
                ),
                cls=combine_classes(p(4), bg_dui.base_200, border.b(), border_dui.base_300),
            ),

            # Content wrapper (adds one level of nesting)
            Div(
                # Info bar with L0 toggle
                Div(
                    Span("Info bar (direct sibling of target)",
                         cls=combine_classes(font_size.sm, text_dui.base_content)),
                    Button("Toggle Details (L0)",
                           onclick="document.getElementById('info-extra').classList.toggle('hidden')",
                           cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                    Div(
                        P("This extra detail is a L0 direct sibling expansion. "
                          "Both old and new observer implementations detect this change.",
                          cls=combine_classes(text_dui.base_content, font_size.sm)),
                        id="info-extra",
                        cls=combine_classes(display_tw.hidden, p(3), bg_dui.success.opacity(20),
                                            border.t(), border_dui.success, rounded.lg, m.t(1)),
                    ),
                    cls=combine_classes(p.x(4), p.y(2), bg_dui.base_100, border.b(),
                                        border_dui.base_300, flex_display,
                                        items.center, flex_wrap.wrap, gap(3)),
                ),

                # Target element (nested inside wrapper)
                Div(
                    *content_items,
                    id="sibling-target",
                    cls=combine_classes(overflow.y.auto, bg_dui.info.opacity(10),
                                        border(2), border_dui.info, rounded.lg, p(2)),
                ),

                cls=combine_classes(flex_display, flex_direction.col, flex(1)),
            ),

            # Footer
            Div(
                Span("Footer: This should always be visible at the bottom of the viewport.",
                     cls=combine_classes(font_size.sm, text_dui.base_content)),
                cls=combine_classes(p(3), bg_dui.base_200, border.t(),
                                    border_dui.base_300, font_size.sm),
            ),

            # Viewport fit script
            render_viewport_fit_script(config),

            cls=combine_classes(flex_display, flex_direction.col),
        )

    return dict(
        config=config,
        page_content=page_content,
        title="Sibling Observer",
        description="Tests L0 (direct) and L1 (ancestor-level) sibling observation with nested target.",
        badges=[("L0 + L1", badge_colors.primary), ("Nested target", badge_colors.secondary)],
    )
