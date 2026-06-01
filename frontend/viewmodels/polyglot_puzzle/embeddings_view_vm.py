from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Literal, Tuple

from vmx import ComponentVMOf, MessageHub, RxDispatcher


ViewMode = Literal["2d", "3d"]


@dataclass(frozen=True)
class EmbeddingsView:
    mode: ViewMode = "2d"
    labels: Tuple[str, ...] = field(default_factory=tuple)
    points_2d: Tuple[Tuple[float, float], ...] = field(default_factory=tuple)
    points_3d: Tuple[Tuple[float, float, float], ...] = field(default_factory=tuple)
    similarities: Tuple[float, ...] = field(default_factory=tuple)


class EmbeddingsViewVM(ComponentVMOf[EmbeddingsView]):
    def set_mode(self, mode: ViewMode) -> None:
        if mode != self.model.mode:
            self.model = replace(self.model, mode=mode)

    def update(
        self,
        labels: list[str],
        points_2d: list[tuple[float, float]] | list[list[float]],
        points_3d: list[tuple[float, float, float]] | list[list[float]],
        similarities: list[float],
    ) -> None:
        # Backend returns nested lists; coerce to tuples for hashable immutability.
        norm_2d = tuple((float(p[0]), float(p[1])) for p in points_2d)
        norm_3d = tuple((float(p[0]), float(p[1]), float(p[2])) for p in points_3d)
        self.model = replace(
            self.model,
            labels=tuple(labels),
            points_2d=norm_2d,
            points_3d=norm_3d,
            similarities=tuple(float(s) for s in similarities),
        )

    def clear(self) -> None:
        self.model = EmbeddingsView(mode=self.model.mode)


def build_embeddings_view_vm(hub: MessageHub, dispatcher: RxDispatcher) -> EmbeddingsViewVM:
    vm = EmbeddingsViewVM(
        name="embeddings-view",
        hint="",
        initial_model=EmbeddingsView(),
        modeled_hinter=lambda m: m.mode,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
