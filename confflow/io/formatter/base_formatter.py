from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from ...utils.types import NestedDict, SchemaGroup


class BaseFormatter(ABC):
    MUTEX_HEADER: str = "# ---------------------------------------"
    MUTEX_MSG: str = "# Mutually exclusive group: Pick only one"
    MUTEX_FOOTER: str = "# ---------------------------------------"
    DEFAULT_INDENT: str = "  "

    @staticmethod
    @abstractmethod
    def generate(
        schemas: List[BaseModel],
        header: Optional[List[str]] = None,
        exclusive_groups: List[SchemaGroup] = [],
    ) -> str: ...

    @abstractmethod
    def _format_key_value(
        self, key: str, value: Any, comment: Optional[str], level: int
    ) -> str: ...

    @abstractmethod
    def _format_section(self, name: str, level: int) -> str: ...

    @abstractmethod
    def _format_comment(self, text: str, level: int = 0) -> str: ...

    def _build_exclusivity_index_map(
        self,
        schemas: List[BaseModel],
        exclusive_groups: List[SchemaGroup],
    ) -> Dict[int, int]:
        index_map: Dict[int, int] = {}
        for group_id, group in enumerate(exclusive_groups):
            for schema in group:
                index: int = schemas.index(schema)
                index_map[index] = group_id
        return index_map

    def _render_exclusive_group(
        self,
        group: SchemaGroup,
        render_func: Callable[[BaseModel], List[str]],
    ) -> List[str]:
        lines: List[str] = [
            self._format_comment(self.MUTEX_HEADER),
            self._format_comment(self.MUTEX_MSG),
            self._format_comment(self.MUTEX_HEADER),
        ]
        for schema in group:
            block: List[str] = render_func(schema)
            lines.extend(block)
        lines.append(self._format_comment(self.MUTEX_FOOTER))
        return lines

    def _get_structured_schema(self, schema: NestedDict) -> NestedDict:
        def resolve_ref(ref: str, root: NestedDict) -> NestedDict:
            ref_key: str = ref.split("/")[-1]
            return root.get("$defs", {}).get(ref_key, {})

        def resolve_node(
            node: NestedDict, root: NestedDict
        ) -> Union[NestedDict, Dict[str, Any]]:
            if "$ref" in node:
                resolved: NestedDict = resolve_ref(node["$ref"], root)
                return resolve_node(resolved, root)

            if "properties" in node:
                resolved_properties: NestedDict = {}
                for key, prop in node["properties"].items():
                    resolved_properties[key] = resolve_node(prop, root)
                return resolved_properties

            return {k: v for k, v in node.items() if k != "title"}

        title: str = schema.get("title", "Config")
        properties: NestedDict = schema.get("properties", {})
        result: NestedDict = {}

        for key, value in properties.items():
            result[key] = resolve_node(value, schema)

        return {title: result}

    def _format_schema_recursive(
        self,
        structured_schema: NestedDict,
        level: int,
        lines: List[str],
    ) -> None:
        for key, content in structured_schema.items():
            if isinstance(content, dict) and any(
                isinstance(v, dict) for v in content.values()
            ):
                lines.append(self._format_section(key, level))
                self._format_schema_recursive(content, level + 1, lines)
            else:
                comment: Optional[str] = self._extract_comment(content)
                default: Any = content.get("default", "")
                lines.append(self._format_key_value(key, default, comment, level))

    def _extract_comment(self, content: Dict[str, Any]) -> Optional[str]:
        comment_parts: List[str] = []
        if (type_ := content.get("type")) is not None:
            comment_parts.append(f"Type: {type_}")
        if (enum := content.get("enum")) is not None:
            comment_parts.append(f"Enum: {enum}")
        if (any_of := content.get("anyOf")) is not None:
            types: List[str] = [item.get("type", "?") for item in any_of]
            comment_parts.append(f"Types: {types}")
        if (description := content.get("description")) is not None:
            comment_parts.append(f"Description: {description}")
        return " | ".join(comment_parts) if comment_parts else None
