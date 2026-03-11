"""Table layout prototype — tests viewport-fit with CSS table display.

Validates the approach of using a regular block wrapper as the viewport-fit
target around a CSS table. Auto-fit measures actual rendered row height from
the DOM (no fixed row_height config) and uses overflow-based validation.

Uses `display: contents` on slot wrappers so table-row children participate
in the parent table layout, enabling automatic column width coordination
between header and body.

Structure under test:
    div (wrapper) ← viewport-fit target
      └── div.table
            ├── div.table-header-group → div.table-row → div.table-cell
            └── div.table-row-group
                  ├── div.contents (slot) → div.table-row → div.table-cell
                  └── ...
"""

from fasthtml.common import Div, H2, P, Span, Button, Script, APIRouter

from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_sizes, btn_styles

from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import w
from cjm_fasthtml_tailwind.utilities.typography import (
    font_size, font_weight, truncate,
)
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, flex_direction, items, gap,
)
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow, display_tw
from cjm_fasthtml_tailwind.utilities.tables import (
    table_display, border_collapse,
)
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_viewport_fit.models import ViewportFitConfig
from cjm_fasthtml_viewport_fit.components import render_viewport_fit_script


# =============================================================================
# Sample data
# =============================================================================

ROW_COUNT = 100

# Name for the global auto-fit function (called by viewport-fit resize_callback)
AUTO_FIT_FN = "_tblAutoFit"

# IDs
WRAPPER_ID = "tbl-wrapper"
TABLE_ID = "tbl-table"
HEADER_ID = "tbl-header"
BODY_ID = "tbl-body"
FOOTER_ID = "tbl-footer"


def _generate_rows(count: int) -> list[dict]:
    """Generate sample table row data with occasional long/multi-line content."""
    extensions = ['.txt', '.py', '.md', '.json', '.csv', '.log', '.yaml', '.toml']
    types = ['document', 'code', 'data', 'config']

    long_names = [
        "very_long_filename_that_might_wrap_depending_on_column_width.json",
        "project-report-final-v2-reviewed-approved.docx",
        "screenshots/2026-03-10_meeting_notes_with_annotations.png",
    ]

    multi_line_names = [
        "README.md\n(project documentation)",
        "config.yaml\n(main config)\n(3 profiles)",
        "deploy.sh\n(production)\n(requires sudo)\n(run from root)",
    ]

    rows = []
    for i in range(count):
        ext = extensions[i % len(extensions)]

        if i % 5 == 0:
            name = long_names[i % len(long_names)]
        elif i % 12 == 5:
            name = multi_line_names[i % len(multi_line_names)]
        else:
            name = f"file_{i:04d}{ext}"

        rows.append(dict(
            index=i,
            name=name,
            size=f"{(i * 137 + 42) % 9999} KB",
            file_type=types[i % len(types)],
        ))
    return rows


# =============================================================================
# Table rendering helpers
# =============================================================================

def _render_header_cell(text: str) -> Div:
    """Render a table header cell."""
    return Div(
        Span(text),
        cls=combine_classes(table_display.cell, p.x(3), p.y(2),
                            font_weight.semibold, font_size.sm,
                            border.b(), border_dui.base_300),
    )


def _render_data_cell(text: str, allow_wrap: bool = False) -> Div:
    """Render a table data cell."""
    cls = combine_classes(
        table_display.cell, p.x(3), p.y(2),
        border.b(), border_dui.base_200,
        None if allow_wrap else truncate,
    )
    if allow_wrap and '\n' in text:
        # Render multi-line content with line breaks
        from fasthtml.common import Br
        parts = []
        for j, line in enumerate(text.split('\n')):
            if j > 0: parts.append(Br())
            parts.append(line)
        return Div(*parts, cls=cls)
    return Div(Span(text), cls=cls)


def _render_header_row() -> Div:
    """Render the table header row."""
    return Div(
        _render_header_cell("#"),
        _render_header_cell("Name"),
        _render_header_cell("Size"),
        _render_header_cell("Type"),
        cls=combine_classes(table_display.row, bg_dui.base_200),
    )


def _render_data_row(row: dict) -> Div:
    """Render a single data row."""
    return Div(
        _render_data_cell(str(row['index'])),
        _render_data_cell(row['name'], allow_wrap=True),
        _render_data_cell(row['size']),
        _render_data_cell(row['file_type']),
        cls=combine_classes(table_display.row, bg_dui.base_200.hover),
    )


def _render_slot(slot_index: int, row: dict) -> Div:
    """Render a slot wrapper with display:contents around a data row."""
    return Div(
        _render_data_row(row),
        id=f"tbl-slot-{slot_index}",
        cls=combine_classes(display_tw.contents),
    )


def _render_body(rows: list, state: dict) -> Div:
    """Render the table body (table-row-group) with visible rows."""
    visible = state["visible_rows"]
    start = state["window_start"]
    end = min(start + visible, len(rows))

    return Div(
        *[_render_slot(i, rows[start + i]) for i in range(end - start)],
        id=BODY_ID,
        cls=combine_classes(table_display.row_group),
    )


def _render_footer(rows: list, state: dict) -> Div:
    """Render the footer with row count info."""
    visible = state["visible_rows"]
    start = state["window_start"]
    end = min(start + visible, len(rows))

    return Div(
        Span(f"Showing {start + 1}-{end} of {len(rows)} rows · "
             f"visible_rows={visible}",
             cls=combine_classes(font_size.sm, text_dui.base_content)),
        Span("", id="tbl-height-display",
             cls=combine_classes(font_size.sm, text_dui.base_content)),
        id=FOOTER_ID,
        cls=combine_classes(p(3), bg_dui.base_200, border.t(),
                            border_dui.base_300, flex_display, items.center, gap(4)),
    )


# =============================================================================
# Demo setup
# =============================================================================

def setup():
    """Set up the table layout prototype demo.

    Returns dict with config, router, page_content callable, title, description.
    """
    rows = _generate_rows(ROW_COUNT)

    # Mutable state — start with 1 row, auto-fit grows from there
    state = {"visible_rows": 1, "window_start": 0}

    # -------------------------------------------------------------------------
    # Router for auto-fit endpoint
    # -------------------------------------------------------------------------

    router = APIRouter(prefix="/tbl")

    @router
    def swap_slot(slot_index: int):
        """Test: swap a single slot's innerHTML via OOB on a display:contents element."""
        start = state["window_start"]
        item_index = start + slot_index
        if item_index >= len(rows):
            return ()

        # Modify the row data temporarily to make the swap visible
        original_name = rows[item_index]['name']
        rows[item_index]['name'] = f"SWAPPED slot {slot_index} (was: {original_name[:20]})"

        inner_row = _render_data_row(rows[item_index])
        slot_oob = Div(
            inner_row,
            id=f"tbl-slot-{slot_index}",
            cls=combine_classes(display_tw.contents),
            hx_swap_oob="innerHTML",
        )

        # Restore original
        rows[item_index]['name'] = original_name

        return slot_oob

    @router
    def update_viewport(visible_rows: int):
        """Update visible row count and re-render body + footer."""
        visible_rows = max(1, min(visible_rows, len(rows)))
        state["visible_rows"] = visible_rows
        # Clamp window_start
        max_start = max(0, len(rows) - visible_rows)
        state["window_start"] = min(state["window_start"], max_start)

        body = _render_body(rows, state)
        body.attrs["hx-swap-oob"] = "outerHTML"

        footer = _render_footer(rows, state)
        footer.attrs["hx-swap-oob"] = "outerHTML"

        return (body, footer)

    # -------------------------------------------------------------------------
    # Viewport-fit config — targets the wrapper, uses resize_callback
    # -------------------------------------------------------------------------

    config = ViewportFitConfig(
        namespace="table_body",
        target_id=WRAPPER_ID,
        resize_callback=f"{AUTO_FIT_FN}()",
        enable_htmx_settle=False,  # Auto-fit handles settle events itself
        debug=False,
    )

    # -------------------------------------------------------------------------
    # Page content
    # -------------------------------------------------------------------------

    def page_content():
        update_url = update_viewport.to()

        return Div(
            # Header
            Div(
                H2("Table Layout Prototype",
                   cls=combine_classes(font_size._2xl, font_weight.bold)),
                P(f"{len(rows)} rows · viewport-fit on wrapper · "
                  f"overflow-based auto-fit · no fixed row height",
                  cls=combine_classes(text_dui.base_content, font_size.sm, m.t(1))),
                cls=combine_classes(p(4), bg_dui.base_200, border.b(), border_dui.base_300),
            ),

            # Toggle to test sibling observation
            Div(
                Span("Info bar (sibling of table wrapper)",
                     cls=combine_classes(font_size.sm, text_dui.base_content)),
                Button("Toggle Extra Content",
                       onclick="document.getElementById('tbl-info-extra').classList.toggle('hidden')",
                       cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                Div(
                    P("This extra content tests that viewport-fit recalculates when "
                      "siblings change. The table should shrink to accommodate.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    id="tbl-info-extra",
                    cls=combine_classes(display_tw.hidden, p(3), bg_dui.success.opacity(20),
                                        border.t(), border_dui.success, rounded.lg, m.t(1)),
                ),
                cls=combine_classes(p.x(4), p.y(2), bg_dui.base_100, border.b(),
                                    border_dui.base_300, flex_display,
                                    items.center, gap(3)),
            ),

            # OOB slot swap test
            Div(
                Span("OOB slot test:",
                     cls=combine_classes(font_size.sm, text_dui.base_content)),
                Button("Swap slot 0",
                       hx_post=f"{swap_slot.to()}?slot_index=0",
                       hx_swap="none",
                       cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                Button("Swap slot 2",
                       hx_post=f"{swap_slot.to()}?slot_index=2",
                       hx_swap="none",
                       cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                Button("Swap slot 5",
                       hx_post=f"{swap_slot.to()}?slot_index=5",
                       hx_swap="none",
                       cls=combine_classes(btn, btn_sizes.sm, btn_styles.outline)),
                cls=combine_classes(p.x(4), p.y(2), bg_dui.base_100, border.b(),
                                    border_dui.base_300, flex_display,
                                    items.center, gap(3)),
            ),

            # Wrapper div — viewport-fit target (regular block element)
            Div(
                # CSS Table inside wrapper
                Div(
                    # Header group
                    Div(
                        _render_header_row(),
                        id=HEADER_ID,
                        cls=combine_classes(table_display.header_group),
                    ),

                    # Body group
                    _render_body(rows, state),

                    id=TABLE_ID,
                    cls=combine_classes(table_display, w.full,
                                        border_collapse.collapse, font_size.sm),
                ),
                id=WRAPPER_ID,
                cls=combine_classes(overflow.y.hidden),
            ),

            # Footer (outside wrapper)
            _render_footer(rows, state),

            # Auto-fit: overflow-based with growth validation
            # (adapted from cjm-fasthtml-card-stack auto_adjust pattern)
            Script(f"""
            (function() {{
                const wrapperId = '{WRAPPER_ID}';
                const tableId = '{TABLE_ID}';
                const bodyId = '{BODY_ID}';
                const updateUrl = '{update_url}';
                const totalItems = {len(rows)};
                const GROW_STEP = 1;

                let _visibleRows = {state["visible_rows"]};
                let _adjusting = false;
                let _adjustTimer = null;
                let _lastDisplayText = '';

                // Growth validation state
                let _growing = false;
                let _reverting = false;
                let _preGrowthCount = 0;
                let _preGrowthSlotIds = null;

                function _getWrapperHeight() {{
                    const el = document.getElementById(wrapperId);
                    return el ? parseInt(el.style.height) || 0 : 0;
                }}

                function _getTableHeight() {{
                    const el = document.getElementById(tableId);
                    return el ? el.getBoundingClientRect().height : 0;
                }}

                function _getOverflow() {{
                    return _getTableHeight() - _getWrapperHeight();
                }}

                function _getAvgRowHeight() {{
                    const body = document.getElementById(bodyId);
                    if (!body) return 0;
                    const tblRows = body.querySelectorAll('.table-row');
                    if (tblRows.length === 0) return 0;
                    let total = 0;
                    for (const r of tblRows) total += r.getBoundingClientRect().height;
                    return total / tblRows.length;
                }}

                function _updateDisplay(msg) {{
                    _lastDisplayText = msg;
                    const d = document.getElementById('tbl-height-display');
                    if (d) d.textContent = msg;
                }}

                function _postUpdate(count) {{
                    _adjusting = true;
                    _visibleRows = count;
                    htmx.ajax('POST', updateUrl + '?visible_rows=' + count, {{
                        target: '#' + bodyId,
                        swap: 'none'
                    }});
                }}

                // --- Growth visibility helpers ---
                // Slots use display:contents so opacity on them has no effect.
                // Instead, hide/reveal the table-row inside each new slot.

                function _snapshotSlotIds() {{
                    const body = document.getElementById(bodyId);
                    if (!body) return new Set();
                    const ids = new Set();
                    for (const child of body.children) {{
                        if (child.id) ids.add(child.id);
                    }}
                    return ids;
                }}

                function _hideNewRows() {{
                    if (!_preGrowthSlotIds) return;
                    const body = document.getElementById(bodyId);
                    if (!body) return;
                    for (const child of body.children) {{
                        if (child.id && !_preGrowthSlotIds.has(child.id)) {{
                            // Slot is display:contents — hide its table-row child
                            const row = child.querySelector('.table-row');
                            if (row) row.style.opacity = '0';
                        }}
                    }}
                }}

                function _revealAllRows() {{
                    const body = document.getElementById(bodyId);
                    if (!body) return;
                    const rows = body.querySelectorAll('.table-row');
                    for (const r of rows) {{
                        if (r.style.opacity === '0') r.style.removeProperty('opacity');
                    }}
                }}

                // --- Core adjust logic (card-stack pattern) ---

                function _runAdjust() {{
                    if (_adjusting) return;

                    // After a failed growth revert, stop the loop
                    if (_reverting) {{
                        _reverting = false;
                        return;
                    }}

                    // If in growth validation, validate instead of normal adjust
                    if (_growing) {{
                        _validateGrowth();
                        return;
                    }}

                    const overflow = _getOverflow();
                    const wrapperH = _getWrapperHeight();
                    if (wrapperH === 0) return;

                    if (overflow > 2) {{
                        // Shrink: batch-estimate rows to remove for instant snap
                        const avgRowH = _getAvgRowHeight();
                        const toRemove = avgRowH > 0
                            ? Math.max(1, Math.ceil(overflow / avgRowH))
                            : 1;
                        const newCount = Math.max(1, _visibleRows - toRemove);
                        _updateDisplay(
                            'rows=' + _visibleRows + ' overflow=' + Math.round(overflow)
                            + ' → shrink to ' + newCount
                        );
                        if (newCount !== _visibleRows) {{
                            _postUpdate(newCount);
                        }}
                    }} else if (_visibleRows < totalItems) {{
                        // Grow: snapshot current slots, try adding GROW_STEP
                        _preGrowthCount = _visibleRows;
                        _preGrowthSlotIds = _snapshotSlotIds();
                        _growing = true;
                        const newCount = Math.min(_visibleRows + GROW_STEP, totalItems);
                        _updateDisplay(
                            'rows=' + _visibleRows + ' → grow to ' + newCount
                        );
                        _postUpdate(newCount);
                    }} else {{
                        _updateDisplay('rows=' + _visibleRows + ' (all items fit)');
                    }}
                }}

                function _validateGrowth() {{
                    const overflow = _getOverflow();
                    if (overflow > 2) {{
                        // Growth caused overflow — revert to pre-growth count, stop
                        _growing = false;
                        _reverting = true;
                        _preGrowthSlotIds = null;
                        _updateDisplay(
                            'rows=' + _visibleRows + ' overflow=' + Math.round(overflow)
                            + ' → revert to ' + _preGrowthCount
                        );
                        _postUpdate(_preGrowthCount);
                    }} else {{
                        // Growth fits — reveal new rows, continue trying
                        _revealAllRows();
                        _growing = false;
                        _preGrowthSlotIds = null;
                        _updateDisplay(
                            'rows=' + _visibleRows + ' fits → continue'
                        );
                        requestAnimationFrame(function() {{
                            _runAdjust();
                        }});
                    }}
                }}

                // --- Entry point (debounced) ---

                window.{AUTO_FIT_FN} = function() {{
                    clearTimeout(_adjustTimer);
                    _reverting = false;
                    _adjustTimer = setTimeout(function() {{
                        _runAdjust();
                    }}, 200);
                }};

                // --- Swap handler: hide new rows during growth validation ---

                document.body.addEventListener('htmx:afterSwap', function() {{
                    if (_growing) _hideNewRows();
                }});

                // --- Settle handler: continue adjust loop ---

                document.body.addEventListener('htmx:afterSettle', function() {{
                    // Re-apply display text (footer was OOB-swapped)
                    const d = document.getElementById('tbl-height-display');
                    if (d && _lastDisplayText) d.textContent = _lastDisplayText;

                    if (!_adjusting) return;
                    _adjusting = false;

                    // Continue the adjust loop
                    requestAnimationFrame(function() {{
                        _runAdjust();
                    }});
                }});

                // --- Initial auto-fit ---

                const _initEl = document.getElementById(wrapperId);
                if (_initEl) {{
                    const _initObserver = new ResizeObserver(function() {{
                        _initObserver.disconnect();
                        window.{AUTO_FIT_FN}();
                    }});
                    _initObserver.observe(_initEl);
                }}
            }})();
            """),

            # Viewport fit script (must come after auto-fit function definition)
            render_viewport_fit_script(config),

            cls=combine_classes(flex_display, flex_direction.col),
        )

    return dict(
        config=config,
        router=router,
        page_content=page_content,
        title="Table Layout",
        description="Overflow-based auto-fit with CSS table display, no fixed row height.",
        badges=[("overflow auto-fit", badge_colors.primary),
                ("display:contents", badge_colors.secondary),
                ("no row_height", badge_colors.accent)],
    )
