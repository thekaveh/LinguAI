from __future__ import annotations
import asyncio
from dataclasses import replace as dc_replace
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import PolyglotPuzzleVM
from views.theme.components import card, pill_button, section_header, bind_button_enabled
from views.polyglot_puzzle._colors import similarity_color as _similarity_color
from views.polyglot_puzzle.attempt_row import render as render_attempt
from views.polyglot_puzzle.embeddings_plot import render as render_plot


# ---------------------------------------------------------------------------
# Advanced-section callbacks (module-level closures)
# ---------------------------------------------------------------------------

def _make_set_structured(vm: PolyglotPuzzleVM):  # type: ignore[no-untyped-def]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        sel = next(
            (lid for lid, label in vm.state.model.structured_llms if label == e.value),
            None,
        )
        if sel is not None:
            vm.set_structured_llm(sel)
    return _cb


def _make_set_embeddings(vm: PolyglotPuzzleVM):  # type: ignore[no-untyped-def]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        sel = next(
            (lid for lid, label in vm.state.model.embeddings_llms if label == e.value),
            None,
        )
        if sel is not None:
            vm.set_embeddings_llm(sel)
    return _cb


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render(shell: AppShellVM) -> None:
    vm: PolyglotPuzzleVM = shell._polyglot_vm  # type: ignore[attr-defined]
    assert vm is not None, "PolyglotPuzzleVM not found on shell"

    # Lazy-load options on first render (fire and forget — view stays sync)
    if vm.state.model.request is None:
        asyncio.create_task(_load_then_finish(vm))

    with card():
        section_header("Polyglot Puzzle", subtitle="Translate, then compare semantic similarity")

        # Three selects in a row
        with ui.row().classes("gap-3 w-full"):
            src = ui.select(list(vm.state.model.src_langs) or [],
                             label="Source", value=vm.state.model.request.src_lang if vm.state.model.request else None) \
                .props("outlined dense").classes("flex-1")
            dst = ui.select(list(vm.state.model.dst_langs) or [],
                             label="Target", value=vm.state.model.request.dst_lang if vm.state.model.request else None) \
                .props("outlined dense").classes("flex-1")
            dif = ui.select(list(vm.state.model.difficulties),
                             label="Difficulty",
                             value=vm.state.model.request.difficulty if vm.state.model.request else "Easy") \
                .props("outlined dense").classes("flex-1")

        def _refresh_selects(name: str) -> None:
            if name != "model":
                return
            src.options = list(vm.state.model.src_langs)
            dst.options = list(vm.state.model.dst_langs)
            src.update(); dst.update()
            if vm.state.model.request:
                src.value = vm.state.model.request.src_lang
                dst.value = vm.state.model.request.dst_lang
                dif.value = vm.state.model.request.difficulty
        vm.state.property_changed.subscribe(_refresh_selects)

        def _set_request_field(field: str):  # type: ignore[no-untyped-def]
            def _cb(e) -> None:  # type: ignore[no-untyped-def]
                if vm.state.model.request is None:
                    return
                new_req = vm.state.model.request.model_copy(update={field: e.value or ""})
                vm.state.set_model(dc_replace(vm.state.model, request=new_req))
            return _cb
        src.on_value_change(_set_request_field("src_lang"))
        dst.on_value_change(_set_request_field("dst_lang"))
        dif.on_value_change(_set_request_field("difficulty"))

        # ---- Advanced expansion: LLM + temperature selectors ----
        with ui.expansion("Advanced", icon="tune").classes("w-full mt-3"):
            with ui.row().classes("gap-3 w-full"):
                struct_sel = ui.select([], label="Generation model") \
                    .props("outlined dense").classes("flex-1")
                emb_sel = ui.select([], label="Embeddings model") \
                    .props("outlined dense").classes("flex-1")
                with ui.column().classes("flex-1"):
                    ui.label("Temperature").classes("text-xs text-[var(--text-3)]")
                    temp_slider = ui.slider(min=0.0, max=1.0, step=0.05) \
                        .props("color=primary dense")

            def _refresh_advanced(name: str) -> None:
                if name != "model":
                    return
                struct_sel.options = [label for _id, label in vm.state.model.structured_llms]
                struct_sel.update()
                if vm.state.model.request:
                    struct_sel.value = next(
                        (label for lid, label in vm.state.model.structured_llms
                         if lid == vm.state.model.request.llm_id),
                        None,
                    )
                emb_sel.options = [label for _id, label in vm.state.model.embeddings_llms]
                emb_sel.update()
                emb_sel.value = next(
                    (label for lid, label in vm.state.model.embeddings_llms
                     if lid == vm.state.model.embeddings_llm_id),
                    None,
                )
                if vm.state.model.request:
                    temp_slider.value = vm.state.model.request.llm_temperature

            _refresh_advanced("model")
            vm.state.property_changed.subscribe(_refresh_advanced)

            struct_sel.on_value_change(_make_set_structured(vm))
            emb_sel.on_value_change(_make_set_embeddings(vm))
            temp_slider.on_value_change(lambda e: vm.set_temperature(float(e.value)))

        with ui.row().classes("gap-2 mt-3"):
            gen = pill_button("Generate puzzle", variant="primary", on_click=vm.generate_command.execute)
            bind_button_enabled(gen, vm.generate_command)
            clr = pill_button("Clear", on_click=vm.clear_command.execute)
            bind_button_enabled(clr, vm.clear_command)

    # Response card: only visible after a response exists
    resp_card = card()
    resp_card.bind_visibility_from(vm.state, "model", backward=lambda m: m.has_response).classes("mt-4")
    with resp_card:
        ui.label().bind_text_from(
            vm.state, "model",
            backward=lambda m: m.response.src_lang_question if m.response else "",
        ).classes("text-base font-medium")
        ui.label().bind_text_from(
            vm.state, "model",
            backward=lambda m: m.response.dst_lang_question if m.response else "",
        ).classes("text-xs text-[var(--text-3)] mt-1")

        attempts_col = ui.column().classes("gap-2 mt-3 w-full")

        def _render_attempts(name: str) -> None:
            if name != "model":
                return
            attempts_col.clear()
            with attempts_col:
                for a in vm.attempts:
                    render_attempt(a)

        # initial render
        with attempts_col:
            for a in vm.attempts:
                render_attempt(a)
        # re-render attempts whenever state.model changes (covers add/clear/generate)
        vm.state.property_changed.subscribe(_render_attempts)

        with ui.row().classes("gap-2 mt-3"):
            add = pill_button("Add attempt", on_click=vm.add_attempt_command.execute)
            bind_button_enabled(add, vm.add_attempt_command)
            sub = pill_button("Submit", variant="primary", on_click=vm.submit_command.execute)
            bind_button_enabled(sub, vm.submit_command)

    # ---- Results card: color-coded similarity table ----
    results_card = card()
    results_card.classes("mt-4").bind_visibility_from(
        vm.state, "model",
        backward=lambda m: m.has_response,
    )
    with results_card:
        section_header("Results", subtitle="how close each attempt is to the ideal translation")

        results_container = ui.column().classes("w-full gap-1 mt-2")

        def _render_results(name: str) -> None:
            if name != "model":
                return
            results_container.clear()
            scored = [a for a in vm.attempts if a.model.similarity is not None]
            if not scored:
                with results_container:
                    ui.label("Submit your attempts to see how they score.") \
                        .classes("text-sm text-[var(--text-3)]")
                return
            with results_container:
                # Header row
                with ui.row().classes(
                    "w-full gap-2 text-xs uppercase tracking-wider "
                    "text-[var(--text-3)] py-1 border-b border-white/5"
                ):
                    ui.label("ATTEMPT").classes("flex-1")
                    ui.label("SIMILARITY").classes("w-32 text-right")
                # Data rows — sorted highest similarity first
                sorted_attempts = sorted(scored, key=lambda a: a.model.similarity or 0, reverse=True)
                for a in sorted_attempts:
                    sim = a.model.similarity or 0.0
                    color = _similarity_color(sim)
                    with ui.row().classes(
                        "w-full gap-2 items-center py-2 border-b border-white/5 text-sm"
                    ):
                        ui.label(a.model.text or "(empty)").classes("flex-1 text-[var(--text-1)]")
                        with ui.column().classes("w-32 gap-0 items-end"):
                            ui.label(f"{sim * 100:.1f}%").style(
                                f"color: {color}; font-weight: 600;"
                            ).classes("text-sm")
                            bar = ui.element("div").classes(
                                "w-full h-1.5 rounded-full bg-white/5 mt-1 overflow-hidden"
                            )
                            with bar:
                                ui.element("div").style(
                                    f"width: {max(0, min(100, sim * 100))}%; height: 100%; "
                                    f"background: {color}; border-radius: inherit;"
                                )

        _render_results("model")
        vm.state.property_changed.subscribe(_render_results)

        ui.label(
            "Semantic similarity is computed via cosine distance over LLM embeddings. "
            "It’s a useful heuristic, not a definitive correctness score — a translation "
            "with different wording can still convey the same meaning and still score "
            "below a literal one."
        ).classes("text-xs text-[var(--text-3)] mt-3 italic")

    render_plot(vm.embeddings)


async def _load_then_finish(vm: PolyglotPuzzleVM) -> None:
    # Re-fires the load command's async body. Done as a regular await to ensure errors surface.
    vm.load_options_command.execute()
