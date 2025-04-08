from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel

from .base_formatter import BaseFormatter


class YAMLFormatter(BaseFormatter):
    @staticmethod
    def generate(
        schemas: List[BaseModel],
        header: Optional[List[str]] = None,
        exclusive_groups: Optional[List[List[BaseModel]]] = None,
        config_values: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> str:
        formatter: YAMLFormatter = YAMLFormatter()
        sections: List[List[str]] = []

        if header:
            header_lines: List[str] = [formatter._format_comment(h) for h in header]
            sections.append(header_lines)

        exclusivity_map: Dict[int, int] = {}
        if not config_values:
            exclusivity_map = formatter._build_exclusivity_index_map(
                schemas, exclusive_groups
            )

        seen_groups: Set[int] = set()

        for i, schema in enumerate(schemas):
            if i in exclusivity_map:
                group_id: int = exclusivity_map[i]
                if group_id in seen_groups:
                    continue
                seen_groups.add(group_id)
                group: List[BaseModel] = exclusive_groups[group_id]
                section_lines: List[str] = formatter._render_exclusive_group(
                    group,
                    lambda s: formatter._render_single_schema(s, config_values),
                )
            else:
                section_lines = formatter._render_single_schema(schema, config_values)

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
        config_values: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[str]:
        structured: Any = self._get_structured_schema(
            schema.model_json_schema(mode="validation")
        )
        title: str = schema.model_json_schema(mode="validation").get("title", "")
        overrides: Optional[Dict[str, Any]] = (
            config_values.get(title, {}) if config_values else {}
        )

        lines: List[str] = []
        self._format_schema_recursive(
            structured,
            level=0,
            lines=lines,
            config_values_for_section=overrides,
        )
        return lines

    def _format_key_value(
        self, key: str, value: Any, comment: Optional[str], level: int
    ) -> str:
        indent: str = self.DEFAULT_INDENT * level
        line: str = f"{indent}{key}: {value}"
        if comment:
            line += f"  # {comment}"
        return line

    def _format_section(self, name: str, level: int) -> str:
        indent: str = self.DEFAULT_INDENT * level
        return f"{indent}{name}:"

    def _format_comment(self, text: str, level: int = 0) -> str:
        indent: str = self.DEFAULT_INDENT * level
        return f"{indent}# {text}"
