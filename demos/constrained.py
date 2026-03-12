"""Constrained container demo — tests viewport-fit with container_id.

Validates that viewport-fit measures against a fixed-height parent container
instead of the browser viewport when container_id is set.

Structure:
    div.h-96 (384px, container_id target)
      ├── div (header bar, ~40px sibling)
      └── div (target) ← viewport-fit sizes this to fill remaining space
"""

from fasthtml.common import Div, H2, P, Span, Button, Script

from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_sizes, btn_styles

from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import w, h
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, flex_direction, items, gap, grow,
)
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow, display_tw
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_viewport_fit.models import ViewportFitConfig
from cjm_fasthtml_viewport_fit.components import render_viewport_fit_script


CONTAINER_ID = "constrained-box"
TARGET_ID = "constrained-target"


def setup():
    """Set up the constrained container demo."""

    config = ViewportFitConfig(
        namespace="constrained",
        target_id=TARGET_ID,
        container_id=CONTAINER_ID,
        enable_htmx_settle=False,
        scroll_to_top=False,
        debug=True,
    )

    def page_content():
        return Div(
            # Description
            Div(
                H2("Constrained Container",
                   cls=combine_classes(font_size._2xl, font_weight.bold)),
                P("viewport-fit with container_id — measures against the h-96 box, not the window. "
                  "The target div should fill remaining space (384px - header - padding).",
                  cls=combine_classes(text_dui.base_content, font_size.sm, m.t(1))),
                cls=combine_classes(m.b(4))
            ),

            # Height diagnostic
            Div(
                Span("Heights: ", cls=font_weight.semibold),
                Span("", id="constrained-heights", cls=text_dui.base_content),
                cls=combine_classes(m.b(4), p(2), bg_dui.base_200, rounded(), font_size.sm),
            ),

            # --- The constrained container (h-96 = 384px) ---
            Div(
                # Header sibling
                Div(
                    Span("Header Bar (sibling of target)",
                         cls=combine_classes(font_size.sm, font_weight.semibold)),
                    Button("Toggle Extra",
                           onclick="document.getElementById('constrained-extra').classList.toggle('hidden')",
                           cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                    Div(
                        P("This extra content tests sibling observation within the container.",
                          cls=combine_classes(text_dui.base_content, font_size.sm)),
                        id="constrained-extra",
                        cls=combine_classes(display_tw.hidden, p(2), bg_dui.success.opacity(20),
                                            rounded(), m.t(1)),
                    ),
                    cls=combine_classes(
                        p.x(3), p.y(2), bg_dui.base_200,
                        border.b(), border_dui.base_300,
                        flex_display, items.center, gap(3),
                    ),
                ),

                # Target div — viewport-fit will size this
                Div(
                    P("This div is the viewport-fit target. Its height should be "
                      "calculated from the container (384px) minus the header bar, "
                      "not from the window height.",
                      cls=combine_classes(text_dui.base_content, font_size.sm, p(4))),
                    Div(
                        Span("", id="constrained-target-height",
                             cls=combine_classes(font_size.sm, text_dui.base_content)),
                        cls=combine_classes(p(4)),
                    ),
                    id=TARGET_ID,
                    cls=combine_classes(bg_dui.primary.opacity(10), overflow.hidden),
                ),

                id=CONTAINER_ID,
                cls=combine_classes(
                    h(96), border(), rounded.lg, overflow.hidden,
                    flex_display, flex_direction.col,
                ),
            ),

            # Viewport fit script
            render_viewport_fit_script(config),

            # Height diagnostic script
            Script(f"""
            (function() {{
                function showHeights() {{
                    const container = document.getElementById('{CONTAINER_ID}');
                    const target = document.getElementById('{TARGET_ID}');
                    const parts = [];
                    if (container) parts.push('container=' + Math.round(container.getBoundingClientRect().height) + 'px');
                    if (target) {{
                        parts.push('target=' + Math.round(target.getBoundingClientRect().height) + 'px');
                        parts.push('minH=' + target.style.minHeight);
                    }}
                    const disp = document.getElementById('constrained-heights');
                    if (disp) disp.textContent = parts.join(' | ');
                    const inner = document.getElementById('constrained-target-height');
                    if (inner && target) inner.textContent = 'Computed height: ' + Math.round(target.getBoundingClientRect().height) + 'px';
                }}
                setInterval(showHeights, 500);
                showHeights();
            }})();
            """),

            cls=combine_classes(p(4)),
        )

    return dict(
        page_content=page_content,
        title="Constrained Container",
        description="viewport-fit with container_id — measures against a fixed-height parent.",
        badges=[
            ("container_id", badge_colors.primary),
            ("h-96", badge_colors.secondary),
            ("sibling observer", badge_colors.accent),
        ],
    )
