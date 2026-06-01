from __future__ import annotations
from datetime import datetime

from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.home.home_vm import HomeVM
from views.theme.components import card, pill_button, section_header


def _greeting() -> str:
    h = datetime.now().hour
    if 5 <= h < 12:
        period = "morning"
    elif 12 <= h < 18:
        period = "afternoon"
    elif 18 <= h < 22:
        period = "evening"
    else:
        period = "night"
    weekday = datetime.now().strftime("%A")
    return f"{weekday} {period}"


def render(shell: AppShellVM) -> None:
    home = next((p for p in shell if getattr(p, "route", None) == "home"), None)
    assert isinstance(home, HomeVM), "HomeVM not found in shell children"
    session = shell.session

    # --- Tour dialog (#16) ---
    tour_dialog = ui.dialog()
    with tour_dialog:
        with card().classes("w-[640px]"):
            section_header("A quick orientation", subtitle="four things you can do here")
            with ui.column().classes("gap-3 mt-2"):
                for icon, name, desc in [
                    (
                        "chat_bubble", "Chat",
                        "Practice a target language with an AI tutor. Pick a persona "
                        "and a model; turn on TTS to hear responses.",
                    ),
                    (
                        "extension", "Polyglot puzzle",
                        "Translate prompts and see how semantically close your answers "
                        "are via embedding similarity.",
                    ),
                    (
                        "auto_stories", "Content",
                        "Generate reading passages at your level on any topic; rewrite "
                        "passages in a target style; get feedback on your own writing.",
                    ),
                    (
                        "insights", "Assessment & Profile",
                        "Take periodic skill assessments. Your profile tracks streaks "
                        "and your skill progression per language.",
                    ),
                ]:
                    with ui.row().classes("gap-3 items-start"):
                        ui.icon(icon).classes("text-[var(--brand)] text-2xl pt-1")
                        with ui.column().classes("gap-0 flex-1"):
                            ui.label(name).classes("text-sm font-semibold")
                            ui.label(desc).classes("text-xs text-[var(--text-2)]")
            with ui.row().classes("justify-end mt-4"):
                pill_button("Got it", variant="primary", on_click=tour_dialog.close)

    # Greeting band
    with ui.row().classes("items-end justify-between mb-6 w-full"):
        with ui.column().classes("gap-1"):
            ui.label(_greeting()).classes("text-xs text-[var(--text-3)]")
            ui.label().bind_text_from(
                session, "model",
                backward=lambda s: f"Welcome back, {s.preferred_name or s.username or 'friend'}.",
            ).classes("text-2xl font-semibold tracking-tight")
            ui.label().bind_text_from(
                home, "model",
                backward=lambda m: (
                    f"{m.languages_in_progress} language(s) in progress"
                    f" · {m.last_session_label}"
                ),
            ).classes("text-sm text-[var(--text-2)]")

            # Daily-streak badge (#17) — shown only when streak >= 2
            streak_chip = (
                ui.label()
                .bind_text_from(
                    session, "model",
                    backward=lambda s: (
                        f"\U0001f525 {s.streak_days}-day streak" if s.streak_days >= 2 else ""
                    ),
                )
                .classes(
                    "text-xs px-2 py-0.5 rounded-full "
                    "bg-[var(--brand)]/10 text-[var(--brand)] mt-1 inline-block"
                )
            )
            streak_chip.bind_visibility_from(
                session, "model", backward=lambda s: s.streak_days >= 2
            )

        # CTA row: Take a tour + Start practice
        with ui.row().classes("gap-2 items-center"):
            pill_button("Take a tour", on_click=tour_dialog.open)
            pill_button(
                "Start practice", variant="primary",
                on_click=lambda: shell.navigation.go("chat"),
            )

    # Your languages section — reactive CTA card when no assessments, hidden once data exists.
    section_header("Your languages")
    starter_container = ui.column().classes("w-full")

    def _render_starter() -> None:
        starter_container.clear()
        if home.model.has_assessments:
            # Assessment data exists — show skill cards when HomeVM populates them.
            if home.model.skill_cards:
                with starter_container:
                    with ui.row().classes("gap-3 w-full flex-wrap"):
                        for sc in home.model.skill_cards:
                            with card().classes("flex-1 min-w-[160px]"):
                                ui.label(str(sc)).classes("text-sm")
            # else: assessments exist but skill_cards not yet wired — show nothing
            return
        # No assessments yet — starter CTA (#24)
        with starter_container:
            with card():
                section_header("Get started")
                ui.label(
                    "Take your first assessment to track your skill progression."
                ).classes("text-sm text-[var(--text-2)]")
                with ui.row().classes("mt-3"):
                    pill_button(
                        "Take an assessment", variant="primary",
                        on_click=lambda: shell.navigation.go("assessment"),
                    )

    _render_starter()
    home.property_changed.subscribe(lambda n: _render_starter() if n == "model" else None)

    # Quick actions
    section_header("Quick actions")
    with ui.row().classes("gap-3 w-full"):
        for route, icon, title, desc in [
            ("chat", "chat_bubble", "Resume conversation", "AI tutor practice"),
            ("polyglot_puzzle", "extension", "Polyglot puzzle", "Translate & compare"),
            ("content_gen", "auto_stories", "Read an article", "Generate at your level"),
            ("rewrite_content", "edit", "Rewrite a passage", "Adjust the register"),
        ]:
            with card().classes("flex-1 cursor-pointer").on("click", _goto(shell, route)):
                ui.icon(icon).classes("text-[var(--brand)] text-2xl")
                ui.label(title).classes("font-semibold mt-1")
                ui.label(desc).classes("text-xs text-[var(--text-3)] mt-0.5")

    # Recent activity section is intentionally omitted until backend wires real data.
    # (Previously showed a "(wired up in phase 4)" placeholder — removed per audit #27.)


def _goto(shell: AppShellVM, route: str):  # type: ignore[no-untyped-def]
    def _cb() -> None:
        shell.navigation.go(route)  # type: ignore[arg-type]
    return _cb
