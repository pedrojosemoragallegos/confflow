from typing import Callable, List, Optional

from pydantic import BaseModel

from confflow.typings import NestedDict


def create_yaml(
    schemas: List[BaseModel],
    header: Optional[List[str]] = None,
) -> str:
    yaml_lines: List[str] = []
    for schema in schemas:
        schema_structure: NestedDict = schema.model_json_schema()
        structured_schema: NestedDict = _get_structured_schema(schema_structure)
        _schema_formatter(structured_schema, lambda x: yaml_lines.append(x))

    if header:
        header_content: str = "\n".join(header) + "\n"
        return header_content + "\n".join(yaml_lines)

    return "\n".join(yaml_lines)


# TODO separation of concerns
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

    return result


def _schema_formatter(
    structured_schema: NestedDict, callback: Callable, level: int = 0
):
    DEFAULT_INTENT: str = "  "

    intent: str = DEFAULT_INTENT * level

    for title, content in structured_schema.items():
        if any(isinstance(value, dict) for value in content.values()):
            callback(f"{intent}{title}:")
            _schema_formatter(content, callback, level + 1)
        else:
            base_line = f"{intent}{title}: "
            default_value = content.get("default", "")
            value_type = content.get("type", "")
            description = content.get("description", "")

            callback(
                base_line
                + (str(default_value) if default_value else "")
                + (
                    f"  # {value_type} - {description}"
                    if description
                    else f"  # {value_type}"
                )
            )
