"""Demo application for cjm-fasthtml-viewport-fit library.

Demonstrates viewport-fit height measurement with two observation scenarios:
- L0: Direct sibling toggle (info bar beside the target)
- L1: Ancestor-level sibling toggle (header above the target's wrapper)

The target is nested inside a wrapper div to test that the ancestor-walking
sibling observer correctly detects changes at all DOM levels.

Run with: python demo_app.py
"""

from fasthtml.common import fast_app, Div, H1, H2, P, Span, Button, Script, serve

from cjm_fasthtml_viewport_fit.models import ViewportFitConfig
from cjm_fasthtml_viewport_fit.components import render_viewport_fit_script


DEMO_PORT = 5040

config = ViewportFitConfig(
    namespace="demo",
    target_id="demo-target",
    debug=True,
)

app, rt = fast_app(
    pico=False,
    title="Viewport Fit Demo",
)


@rt("/")
def get():
    """Demo page with nested target to test ancestor-level sibling observation."""
    content_items = [
        P(f"Item {i + 1}: Sample content that fills the viewport-fitted area",
          style="padding: 8px; margin: 4px 0; background: #f0f0ff; border-radius: 4px;")
        for i in range(50)
    ]

    return Div(
        # Header with toggle (L1 sibling — sibling of the content wrapper, not the target)
        Div(
            Div(
                H1("Viewport Fit Demo", style="margin: 0; display: inline;"),
                Button("Toggle Header Info (L1)",
                       onclick="document.getElementById('header-extra').style.display = "
                               "document.getElementById('header-extra').style.display === 'none' ? 'block' : 'none';",
                       style="margin-left: 16px; padding: 4px 12px; cursor: pointer;"),
                style="display: flex; align-items: center;",
            ),
            P("The blue area fills the remaining viewport height. "
              "Toggle buttons add/remove content to test sibling observation at different DOM levels. "
              "Check the console for debug output.",
              style="margin: 8px 0 0 0;"),
            Div(
                P("This extra header content is a L1 ancestor-level sibling of the target. "
                  "The target is nested inside a wrapper div, so this element is NOT a direct sibling. "
                  "The ancestor-walking observer detects this change.",
                  style="margin: 4px 0; color: #555;"),
                P("With the old direct-sibling-only observer, toggling this would NOT trigger "
                  "a recalculation. With the ancestor-walking observer, it does.",
                  style="margin: 4px 0; color: #555;"),
                id="header-extra",
                style="display: none; padding: 8px; background: #fff3cd; border: 1px solid #ffc107; "
                      "border-radius: 4px; margin-top: 8px;",
            ),
            id="demo-header",
            style="padding: 16px; background: #e8e8e8; border-bottom: 2px solid #ccc;",
        ),

        # Content wrapper (adds one level of nesting)
        Div(
            # Info bar with toggle (L0 sibling — direct sibling of the target)
            Div(
                Span("Info bar (direct sibling of target)", style="font-size: 14px;"),
                Button("Toggle Details (L0)",
                       onclick="document.getElementById('info-extra').style.display = "
                               "document.getElementById('info-extra').style.display === 'none' ? 'block' : 'none';",
                       style="margin-left: 12px; padding: 4px 12px; cursor: pointer;"),
                Div(
                    P("This extra detail is a L0 direct sibling expansion. "
                      "Both old and new observer implementations detect this change.",
                      style="margin: 4px 0; color: #555;"),
                    id="info-extra",
                    style="display: none; padding: 8px; background: #d4edda; border: 1px solid #28a745; "
                          "border-radius: 4px; margin-top: 4px;",
                ),
                id="demo-info-bar",
                style="padding: 8px 16px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; "
                      "display: flex; align-items: center; flex-wrap: wrap; gap: 4px;",
            ),

            # Target element (nested inside wrapper — will be fitted to viewport)
            Div(
                *content_items,
                id="demo-target",
                style="overflow-y: auto; background: #e0e0ff; border: 2px solid #88f; padding: 8px;",
            ),

            id="demo-content-wrapper",
            style="display: flex; flex-direction: column; flex: 1;",
        ),

        # Footer (L1 sibling — below the content wrapper)
        Div(
            Span("Footer: This should always be visible at the bottom of the viewport.",
                 style="font-size: 14px; color: #666;"),
            style="padding: 12px; background: #e8e8e8; border-top: 2px solid #ccc; text-align: center;",
        ),

        # Viewport fit script
        render_viewport_fit_script(config),

        style="display: flex; flex-direction: column;",
    )


if __name__ == "__main__":
    print(f"\nViewport Fit Demo: http://localhost:{DEMO_PORT}")
    print(f"  Open browser console to see debug output")
    print(f"  Toggle buttons test L0 (direct) and L1 (ancestor) sibling observation\n")
    serve(port=DEMO_PORT)
