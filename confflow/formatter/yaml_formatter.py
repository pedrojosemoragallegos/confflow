from typing import Any, Dict, List, Optional, Set, Type

from pydantic import BaseModel

from ..common.types import SchemaGroup
from .base_formatter import BaseFormatter
from .formatter_registry import FormatterRegistry


@FormatterRegistry.register(key="yaml")
class YAMLFormatter(BaseFormatter):
    @staticmethod
    def generate(
        schemas: List[BaseModel],
        header: Optional[List[str]] = None,
        exclusive_groups: Optional[List[SchemaGroup]] = None,
        defaults: Optional[Dict[Type[BaseModel], Dict[str, Any]]] = None,
    ) -> str:
        formatter = YAMLFormatter()
        sections: List[List[str]] = []
        defaults = defaults or {}

        if header:
            header_lines = [formatter._format_comment(line) for line in header]
            sections.append(header_lines)

        exclusivity_map = formatter._build_exclusivity_index_map(
            schemas, exclusive_groups
        )
        seen_groups: Set[int] = set()

        for i, schema in enumerate(schemas):
            schema_cls = type(schema)
            schema_defaults = defaults.get(schema_cls, {})

            if i in exclusivity_map:
                group_id = exclusivity_map[i]
                if group_id in seen_groups:
                    continue
                seen_groups.add(group_id)
                group = exclusive_groups[group_id] if exclusive_groups else []

                def render_func(s: BaseModel) -> List[str]:
                    s_cls = type(s)
                    s_defaults = defaults.get(s_cls, {})
                    return formatter._render_single_schema(s, s_defaults)

                section_lines = formatter._render_exclusive_group(group, render_func)
            else:
                section_lines = formatter._render_single_schema(schema, schema_defaults)

            sections.append(section_lines)

        lines: List[str] = []
        for idx, section in enumerate(sections):
            lines.extend(section)
            if idx < len(sections) - 1:
                lines.append("")

        return "\n".join(lines)

    def _render_single_schema(
        self,
        schema: BaseModel,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        structured_schema = schema.model_json_schema(mode="validation")
        structured = self._get_structured_schema(structured_schema)
        lines: List[str] = []
        self._format_schema_recursive(
            structured, level=0, lines=lines, defaults=defaults
        )
        return lines

    def _format_key_value(
        self,
        key: str,
        value: Any,
        comment: Optional[str],
        level: int,
    ) -> str:
        line: str = ""
        line += self.DEFAULT_INDENT * level
        line += f"{key}:" + (f" {value}" if value != "" else "")
        if comment:
            line += f" # {comment}"
        return line

    def _format_section(self, name: str, level: int) -> str:
        indent = self.DEFAULT_INDENT * level
        return f"{indent}{name}:"

    def _format_comment(self, text: str, level: int = 0) -> str:
        indent = self.DEFAULT_INDENT * level
        return f"{indent}# {text}"
