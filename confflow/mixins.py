class IPythonMixin:
    def _ipython_key_completions_(self) -> list[str]:
        try:
            return list(self.keys())
        except AttributeError:
            return []
