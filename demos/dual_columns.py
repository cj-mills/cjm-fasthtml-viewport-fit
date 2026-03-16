"""Dual column demo — tests viewport-fit with flex-row parent that has padding.

Reproduces a regression found in the decomposition workflow's Phase 2
(Segment & Align) dual-card-stack layout, where a flex-row parent's
padding-bottom is not counted in _calculateSpaceBelow because the
flex-row detection skips the entire parent including its padding.

Structure (mimics decomp workflow Phase 2):
    div.flex.flex-col.h-full (page root)
      ├── div (header — sibling above)
      ├── div (toolbar — sibling above)
      ├── div.flex.flex-row.p-1 (dual-column area — flex-row WITH padding)
      │   ├── div.w-[60%].flex.flex-col (left column)
      │   │   ├── div (column header)
      │   │   └── div#target-left (target — viewport-fit sizes this)
      │   └── div.w-[40%].flex.flex-col (right column)
      │       ├── div (column header)
      │       └── div#target-right (reference — manually measured)
      └── div (footer — sibling below)
"""

from fasthtml.common import Div, H2, P, Span, Button, Script

from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_sizes, btn_styles

from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import w, h, min_h
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, flex_direction, items, justify, gap, grow,
)
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_viewport_fit.models import ViewportFitConfig
from cjm_fasthtml_viewport_fit.components import render_viewport_fit_script


TARGET_LEFT_ID = "dual-col-target-left"
TARGET_RIGHT_ID = "dual-col-target-right"


def setup():
    """Set up the dual column demo."""

    config = ViewportFitConfig(
        namespace="dual_col_left",
        target_id=TARGET_LEFT_ID,
        min_height=100,
        enable_htmx_settle=False,
        scroll_to_top=False,
        observe_siblings=True,
        debug=True,
    )

    def page_content():
        return Div(
            # --- Page root: flex-col, full height (like SEG_CONTAINER) ---
            Div(
                # Header (like decomp shared header)
                Div(
                    H2("Dual Columns — Flex-Row Padding Test",
                       cls=combine_classes(font_size.xl, font_weight.bold)),
                    P("Tests viewport-fit with a flex-row parent that has padding. "
                      "The left target should fill remaining space correctly.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(p(2)),
                ),

                # Toolbar (like decomp shared toolbar)
                Div(
                    Span("Toolbar area (sibling above dual-column area)",
                         cls=combine_classes(font_size.sm, font_weight.semibold)),
                    Button("Toggle Extra",
                           onclick="document.getElementById('dual-col-extra').classList.toggle('hidden')",
                           cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                    Div(
                        P("Extra toolbar content — tests sibling observer recalculation.",
                          cls=combine_classes(text_dui.base_content, font_size.sm)),
                        id="dual-col-extra",
                        cls=combine_classes("hidden", p(2), bg_dui.success.opacity(20), rounded(), m.t(1)),
                    ),
                    cls=combine_classes(
                        p.x(3), p.y(2), bg_dui.base_200,
                        border.b(), border_dui.base_300,
                        flex_display, items.center, gap(3),
                    ),
                ),

                # Height diagnostic
                Div(
                    Span("Heights: ", cls=font_weight.semibold),
                    Span("", id="dual-col-heights", cls=text_dui.base_content),
                    cls=combine_classes(p(2), bg_dui.base_200, font_size.sm),
                ),

                # --- Dual-column area: flex-row WITH padding (the problematic pattern) ---
                Div(
                    # Left column (60%)
                    Div(
                        # Column header
                        Div(
                            Span("Left Column",
                                 cls=combine_classes(font_size.sm, font_weight.semibold)),
                            Span("viewport-fit target", cls=combine_classes(badge, badge_colors.primary)),
                            cls=combine_classes(
                                flex_display, justify.between, items.center, p(3),
                                bg_dui.base_200, border_dui.base_300, border.b(),
                            ),
                        ),
                        # Target — viewport-fit will size this
                        Div(
                            P("This div is the viewport-fit target. Its height should be "
                              "calculated correctly, accounting for the flex-row parent's "
                              "padding-bottom.",
                              cls=combine_classes(text_dui.base_content, font_size.sm, p(4))),
                            id=TARGET_LEFT_ID,
                            cls=combine_classes(
                                grow(), min_h(0), overflow.hidden,
                                flex_display, flex_direction.col,
                                bg_dui.primary.opacity(10),
                            ),
                        ),
                        cls=combine_classes(
                            w('[60%]'), min_h(0),
                            flex_display, flex_direction.col,
                            border(), overflow.hidden,
                        ),
                    ),

                    # Right column (40%)
                    Div(
                        # Column header
                        Div(
                            Span("Right Column",
                                 cls=combine_classes(font_size.sm, font_weight.semibold)),
                            Span("reference", cls=combine_classes(badge, badge_colors.secondary)),
                            cls=combine_classes(
                                flex_display, justify.between, items.center, p(3),
                                bg_dui.base_200, border_dui.base_300, border.b(),
                            ),
                        ),
                        # Reference div (not viewport-fit, just grows naturally)
                        Div(
                            P("This div grows naturally via flex. Compare its height "
                              "to the left target's calculated height — they should match.",
                              cls=combine_classes(text_dui.base_content, font_size.sm, p(4))),
                            id=TARGET_RIGHT_ID,
                            cls=combine_classes(
                                grow(), min_h(0), overflow.hidden,
                                flex_display, flex_direction.col,
                                bg_dui.secondary.opacity(10),
                            ),
                        ),
                        cls=combine_classes(
                            w('[40%]'), min_h(0),
                            flex_display, flex_direction.col,
                            border(), overflow.hidden,
                        ),
                    ),

                    # This is the key: flex-row WITH padding
                    cls=combine_classes(
                        grow(), min_h(0),
                        flex_display, flex_direction.row, gap(4),
                        overflow.hidden, p(1),
                    ),
                ),

                # Footer (like decomp shared footer)
                Div(
                    Span("Footer area (sibling below dual-column area)",
                         cls=combine_classes(font_size.sm)),
                    cls=combine_classes(
                        p(1), bg_dui.base_100, border.t(), border_dui.base_300,
                        flex_display, justify.between, items.center,
                    ),
                ),

                # Page root classes: flex-col, full height
                cls=combine_classes(
                    w.full, h.full,
                    flex_display, flex_direction.col,
                    p(4), p.b(0),
                ),
            ),

            # Viewport fit script (for left target)
            render_viewport_fit_script(config),

            # Height diagnostic script
            Script(f"""
            (function() {{
                function showHeights() {{
                    const left = document.getElementById('{TARGET_LEFT_ID}');
                    const right = document.getElementById('{TARGET_RIGHT_ID}');
                    const parts = [];
                    if (left) {{
                        const lr = left.getBoundingClientRect();
                        parts.push('left(vf)=' + Math.round(lr.height) + 'px');
                        parts.push('left.style=' + left.style.height);
                    }}
                    if (right) {{
                        const rr = right.getBoundingClientRect();
                        parts.push('right(ref)=' + Math.round(rr.height) + 'px');
                    }}
                    if (left && right) {{
                        const diff = Math.round(left.getBoundingClientRect().height)
                                   - Math.round(right.getBoundingClientRect().height);
                        parts.push('delta=' + diff + 'px');
                    }}
                    const disp = document.getElementById('dual-col-heights');
                    if (disp) disp.textContent = parts.join(' | ');
                }}
                setInterval(showHeights, 500);
                setTimeout(showHeights, 200);
            }})();
            """),

            cls=combine_classes(h.full),
        )

    return dict(
        page_content=page_content,
        title="Dual Columns",
        description="viewport-fit with flex-row parent padding — regression test for dual card-stack layout.",
        badges=[
            ("flex-row", badge_colors.primary),
            ("padding", badge_colors.secondary),
            ("regression", badge_colors.error),
        ],
    )
