from nicegui import ui


def install_fonts() -> None:
    """Inject Google-hosted Inter + JetBrains Mono into the document head. Idempotent."""
    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700&'
        'family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
        '<style>'
        'html,body{font-family:"Inter",-apple-system,sans-serif;'
        '-webkit-font-smoothing:antialiased;font-feature-settings:"cv11","ss01"}'
        'code,pre,.mono{font-family:"JetBrains Mono",ui-monospace,monospace}'
        '</style>'
    )
