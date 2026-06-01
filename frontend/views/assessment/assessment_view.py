from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.assessment.assessment_vm import AssessmentVM
from views.theme.components import card, pill_button, section_header, bind_button_enabled


def render(shell: AppShellVM) -> None:
    vm: AssessmentVM = shell._assessment_vm  # type: ignore[attr-defined]

    if not vm.state.model.language:
        asyncio.create_task(_load_then_finish(vm))

    with card():
        section_header("Skill assessment")
        ui.label().bind_text_from(
            vm.state,
            "model",
            backward=lambda m: f"Language: {m.language or '(loading…)'}",
        ).classes("text-sm text-[var(--text-2)] mb-2")

        questions_col = ui.column().classes("gap-3 w-full")

        def _render_questions() -> None:
            questions_col.clear()
            with questions_col:
                for i, qvm in enumerate(vm.questions):
                    with ui.column().classes("gap-1"):
                        ui.label(f"{i+1}. {qvm.model.prompt}").classes("text-sm")
                        radio = ui.radio(list(qvm.model.options))
                        if qvm.model.selected_index is not None:
                            radio.value = qvm.model.options[qvm.model.selected_index]
                        radio.on_value_change(_make_select(qvm))

        def _refresh(name: str) -> None:
            if name != "model":
                return
            _render_questions()

        _render_questions()
        vm.state.property_changed.subscribe(_refresh)

        with ui.row().classes("justify-between items-center mt-4"):
            ui.label().bind_text_from(
                vm.state,
                "model",
                backward=lambda m: f"Score: {m.completed_score}%"
                if m.completed_score is not None
                else "",
            ).classes("text-sm text-[var(--brand)]")
            submit = pill_button(
                "Submit", variant="primary", on_click=vm.submit_command.execute
            )
            bind_button_enabled(submit, vm.submit_command)


def _make_select(qvm: object) -> object:
    from viewmodels.assessment.question_vm import QuestionVM

    def _cb(e: object) -> None:
        assert isinstance(qvm, QuestionVM)
        try:
            idx = list(qvm.model.options).index(e.value)  # type: ignore[union-attr]
        except ValueError:
            return
        qvm.choose(idx)

    return _cb


async def _load_then_finish(vm: AssessmentVM) -> None:
    vm.load_command.execute()
