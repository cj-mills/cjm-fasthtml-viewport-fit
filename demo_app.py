"""Demo application for cjm-fasthtml-viewport-fit library.

Demonstrates viewport-fit height measurement on a target div with content
above and below. The target div fills the remaining viewport space.

Run with: python demo_app.py
"""

from fasthtml.common import fast_app, Div, H1, H2, P, Span, serve

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
    """Demo page with header, fitted target, and footer."""
    # Generate scrollable content for the target
    content_items = [
        P(f"Item {i + 1}: Sample content that fills the viewport-fitted area",
          style="padding: 8px; margin: 4px 0; background: #f0f0ff; border-radius: 4px;")
        for i in range(50)
    ]

    return Div(
        # Header (above target)
        Div(
            H1("Viewport Fit Demo", style="margin: 0;"),
            P("The blue area below fills the remaining viewport height. "
              "Resize the browser window to see it adjust. Check the console for debug output."),
            style="padding: 16px; background: #e8e8e8; border-bottom: 2px solid #ccc;",
        ),

        # Target element (will be fitted to viewport)
        Div(
            *content_items,
            id="demo-target",
            style="overflow-y: auto; background: #e0e0ff; border: 2px solid #88f; padding: 8px;",
        ),

        # Footer (below target — should remain visible)
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
    print(f"  Open browser console to see debug output\n")
    serve(port=DEMO_PORT)
