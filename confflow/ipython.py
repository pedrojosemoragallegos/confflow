from typing import Any


class IPythonKeyCompletionMixin:
    def _ipython_key_completions_(self) -> list[str]:
        if hasattr(self, "keys"):
            return list(self.keys())
        return []


class ReprPrettyMixin:
    def _repr_pretty_(self, p, cycle: bool):
        if cycle:
            p.text(f"{self.__class__.__name__}(...)")
        else:
            p.text(repr(self))


class ReprHTMLMixin:
    def _repr_html_(self) -> str:
        name = getattr(self, "_name", self.__class__.__name__)
        desc = getattr(self, "_description", "")
        if hasattr(self, "items"):
            try:
                items_html = "".join(
                    f"<li><strong>{k}</strong>: {v}</li>" for k, v in self.items()
                )
            except Exception:
                items_html = "<li><em>Unable to render fields</em></li>"
        else:
            items_html = ""
        return f"<div><h3>{name}</h3><p>{desc}</p><ul>{items_html}</ul></div>"


class ReprMarkdownMixin:
    def _repr_markdown_(self) -> str:
        name = getattr(self, "_name", self.__class__.__name__)
        desc = getattr(self, "_description", "")
        output = f"### {name}\n\n{desc}\n\n"
        if hasattr(self, "items"):
            try:
                for k, v in self.items():
                    output += f"- **{k}**: {v}\n"
            except Exception:
                output += "- *(Unable to list fields)*\n"
        return output


class ReprMimeBundleMixin:
    def _repr_mimebundle_(self, include=None, exclude=None) -> dict[str, Any]:
        bundle = {}
        if hasattr(self, "_repr_markdown_"):
            bundle["text/markdown"] = self._repr_markdown_()
        if hasattr(self, "_repr_html_"):
            bundle["text/html"] = self._repr_html_()
        return bundle


class IPythonDisplayMixin:
    def _ipython_display_(self):
        from IPython.display import Markdown, display

        if hasattr(self, "_repr_markdown_"):
            display(Markdown(self._repr_markdown_()))
        else:
            display(repr(self))


class DirKeysMixin:
    def __dir__(self):
        base = list(super().__dir__())
        if hasattr(self, "keys"):
            try:
                return base + list(self.keys())
            except Exception:
                pass
        return base


# Optional: Combine all into a single convenience mixin
class JupyterDisplayMixin(
    IPythonKeyCompletionMixin,
    ReprPrettyMixin,
    ReprHTMLMixin,
    ReprMarkdownMixin,
    ReprMimeBundleMixin,
    IPythonDisplayMixin,
    DirKeysMixin,
):
    """Convenience mixin that adds full IPython/Jupyter support."""

    pass
