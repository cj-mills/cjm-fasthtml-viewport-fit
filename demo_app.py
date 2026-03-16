"""Demo application for cjm-fasthtml-viewport-fit library.

Showcases viewport-fit height measurement with multiple demo configurations.
Each demo is a self-contained module in the demos/ package.

Run with: python demo_app.py
"""


DEMO_PORT = 5040


def main():
    """Initialize viewport-fit demos and start the server."""
    from fasthtml.common import fast_app, Div, H1, H2, P, Span, A, APIRouter

    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.data_display.card import card, card_body
    from cjm_fasthtml_daisyui.components.data_display.badge import badge
    from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
    from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import grid_display, grid_cols, gap
    from cjm_fasthtml_tailwind.core.base import combine_classes

    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    import demos.sibling_observer as sibling_demo
    import demos.table_layout as table_demo
    import demos.constrained as constrained_demo
    import demos.dual_columns as dual_columns_demo

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-viewport-fit Demo")
    print("=" * 70)

    app, rt = fast_app(
        pico=False,
        hdrs=[*get_daisyui_headers(), create_theme_persistence_script()],
        title="Viewport Fit Demo",
        htmlkw={'data-theme': 'light'},
        secret_key="demo-secret-key"
    )

    router = APIRouter(prefix="")

    # -------------------------------------------------------------------------
    # Set up demos
    # -------------------------------------------------------------------------

    sibling = sibling_demo.setup()
    table = table_demo.setup()
    constrained = constrained_demo.setup()
    dual_columns = dual_columns_demo.setup()
    print(f"  Sibling observer demo: {sibling['title']}")
    print(f"  Table layout demo: {table['title']}")
    print(f"  Constrained demo: {constrained['title']}")
    print(f"  Dual columns demo: {dual_columns['title']}")

    # -------------------------------------------------------------------------
    # Page routes
    # -------------------------------------------------------------------------

    @router
    def index(request):
        """Homepage with demo overview."""

        def home_content():
            return Div(
                H1("Viewport Fit Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

                P("Reusable viewport height measurement for FastHTML applications. "
                  "Dynamically fits element height to remaining viewport space "
                  "with resize and HTMX integration.",
                  cls=combine_classes(font_size.lg, text_dui.base_content, m.b(8))),

                # Demo cards
                Div(
                    _demo_card(
                        sibling['title'],
                        sibling['description'],
                        badges=sibling['badges'],
                        href=demo_sibling.to(),
                    ),
                    _demo_card(
                        table['title'],
                        table['description'],
                        badges=table['badges'],
                        href=demo_table.to(),
                    ),
                    _demo_card(
                        constrained['title'],
                        constrained['description'],
                        badges=constrained['badges'],
                        href=demo_constrained.to(),
                    ),
                    _demo_card(
                        dual_columns['title'],
                        dual_columns['description'],
                        badges=dual_columns['badges'],
                        href=demo_dual_columns.to(),
                    ),
                    cls=combine_classes(
                        grid_display, grid_cols(1), grid_cols(2).md, gap(6), m.b(8)
                    )
                ),

                # Features section
                Div(
                    H2("Features",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Div(
                        P("Collapse-measure-apply height calculation", cls=m.b(1)),
                        P("Ancestor-walking sibling observer (ResizeObserver)", cls=m.b(1)),
                        P("Window resize handler with re-entrance guard", cls=m.b(1)),
                        P("HTMX afterSettle integration for SPA navigation", cls=m.b(1)),
                        P("Namespace isolation for multiple instances", cls=m.b(1)),
                        P("Optional resize callback for consumer integration", cls=m.b(1)),
                        P("Debug logging via window flag", cls=m.b(1)),
                        cls=combine_classes(text_align.left, max_w.md, m.x.auto, font_size.sm)
                    ),
                    cls=m.b(8)
                ),

                cls=combine_classes(
                    container, max_w._5xl, m.x.auto, p(8), text_align.center
                )
            )

        return handle_htmx_request(
            request, home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    def _demo_card(title, description, badges, href):
        """Render a demo card for the homepage."""
        return Div(
            Div(
                H2(title, cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                P(description, cls=combine_classes(text_dui.base_content, m.b(4))),
                Div(
                    *[Span(label, cls=combine_classes(badge, color, m.r(2)))
                      for label, color in badges],
                    cls=m.b(4)
                ),
                A("Open Demo", href=href, cls=combine_classes(btn, btn_colors.primary)),
                cls=card_body
            ),
            cls=combine_classes(card, bg_dui.base_200)
        )

    @router
    def demo_sibling(request):
        """Sibling observer demo page."""
        return handle_htmx_request(
            request, sibling['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_table(request):
        """Table layout prototype demo page."""
        return handle_htmx_request(
            request, table['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_constrained(request):
        """Constrained container demo page."""
        return handle_htmx_request(
            request, constrained['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_dual_columns(request):
        """Dual columns demo page."""
        return handle_htmx_request(
            request, dual_columns['page_content'],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    # -------------------------------------------------------------------------
    # Navbar & route registration
    # -------------------------------------------------------------------------

    navbar = create_navbar(
        title="Viewport Fit Demo",
        nav_items=[
            ("Home", index),
            ("Sibling Observer", demo_sibling),
            ("Table Layout", demo_table),
            ("Constrained", demo_constrained),
            ("Dual Columns", demo_dual_columns),
        ],
        home_route=index,
        theme_selector=True
    )

    register_routes(app, router, table['router'])

    # Debug output
    print("\n" + "=" * 70)
    print("Registered Routes:")
    print("=" * 70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    print("=" * 70)
    print("Demo App Ready!")
    print("=" * 70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    app = main()

    port = DEMO_PORT
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print(f"\n  http://{display_host}:{port}/              — Homepage")
    print(f"  http://{display_host}:{port}/demo_sibling  — Sibling observer demo")
    print(f"  http://{display_host}:{port}/demo_table   — Table layout prototype")
    print()

    timer = threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host=host, port=port)
