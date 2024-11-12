from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel as BaseConfig

from confflow.types import NestedDict


class Formatter(ABC):
    @staticmethod
    @abstractmethod
    def generate(
        schemas: List[BaseConfig],
        header: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Dict[str, Any]]] = None,
        mutually_exclusive_groups: Optional[List[List[str]]] = [],
    ) -> str:
        pass

    @staticmethod
    def _get_structured_schema(schema: NestedDict) -> NestedDict:
        def resolve_ref(ref: str, schema: NestedDict) -> NestedDict:
            ref_key: str = ref.split("/")[-1]
            return schema.get("$defs").get(ref_key, {})

        def resolve_schema(schema: NestedDict, node: NestedDict) -> NestedDict:
            if node.get("$ref"):
                resolved: NestedDict = resolve_ref(node["$ref"], schema)
                return filtered_dict(resolve_schema(schema, resolved).get("properties"))
            elif node.get("properties"):
                resolved_properties: NestedDict = {}
                for key, value in node.get("properties").items():
                    resolved_properties[key] = resolve_schema(schema, value)
                node["properties"] = resolved_properties
            return filtered_dict(node, "title")

        def filtered_dict(data: NestedDict, *keys: str) -> NestedDict:
            return {key: data[key] for key in data if key not in keys}

        properties: NestedDict = schema.get("properties")
        result: NestedDict = {}

        for title, content in properties.items():
            if content.get("$ref"):
                resolved: NestedDict = resolve_schema(schema, content)
                result[title] = resolved
            else:
                result[title] = filtered_dict(properties.get(title, {}), "title")

        return {schema.get("title"): result}

    @staticmethod
    def _schema_formatter(
        structured_schema: NestedDict,
        callback: Callable[[str], Any],
        default_values: Optional[Dict[str, Any]] = {},
        level: int = 0,
    ):
        DEFAULT_INTENT: str = "  "
        intent: str = DEFAULT_INTENT * level
        for title, content in structured_schema.items():
            if any(isinstance(value, dict) for value in content.values()):
                callback(f"{intent}{title}:")
                Formatter._schema_formatter(
                    structured_schema=content,
                    callback=callback,
                    level=level + 1,
                    default_values=default_values,
                )
            else:
                base_line: str = f"{intent}{title}: "
                default_value: Any = default_values.get(
                    title, content.get("default", "")
                )

                comment: str = " # "
                if (value_type := content.get("type")) and (
                    enum_values := content.get("enum")
                ):
                    comment += f"Type: {value_type} {enum_values}  "
                else:
                    if value_type := content.get("type"):
                        comment += f"Type: {value_type}  "
                    if enum_values := content.get("enum"):
                        comment += f"Enum: {enum_values}  "
                if literal := content.get("anyOf"):
                    comment += f"Types: {[item['type'] for item in literal]}  "
                if description := content.get("description"):
                    comment += f"Description: {description}  "

                callback(
                    base_line + (str(default_value) if default_value else "") + comment
                )
