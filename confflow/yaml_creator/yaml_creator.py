from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

from confflow.types import NestedDict


def create_yaml(
    schemas: List[BaseModel],
    header: Optional[List[str]] = None,
    mutually_exclusive_groups: Optional[List[List[str]]] = None,
) -> str:
    mutually_exlusive_grouped_indices: List[List[str]] = sorted(
        [
            sorted([schemas.index(item) for item in mutually_exclusive_group])
            for mutually_exclusive_group in mutually_exclusive_groups
        ],
        key=lambda x: x[0],
    )

    index_to_group_map: Dict[int, str] = {
        index: group_id
        for group_id, indices in enumerate(mutually_exlusive_grouped_indices)
        for index in indices
    }

    skipped_indices: List[int] = []
    yaml_lines: List[str] = []
    for current_index, schema in enumerate(schemas):
        if current_index in skipped_indices:
            continue

        group_index: Optional[int] = index_to_group_map.get(current_index)
        if group_index is not None:  # schema is part of a mutual excluisve group
            BLOCK_START: List[str] = [
                "# -------------------------------------",
                "# Mutual exclusive group: Pick only one",
                "# -------------------------------------",
            ]
            yaml_lines.extend(BLOCK_START)

            for index in mutually_exlusive_grouped_indices[
                group_index
            ]:  # index of schema in schemas
                schema_formatter(
                    get_structured_schema(schemas[index].model_json_schema()),
                    lambda x: yaml_lines.append(x),
                )
                skipped_indices.append(index)

            BLOCK_END: List[str] = "# -------------------------------------"
            yaml_lines.append(BLOCK_END)
        else:
            schema_formatter(
                get_structured_schema(schema.model_json_schema()),
                lambda x: yaml_lines.append(x),
            )

    if header:
        header_content: str = "\n".join(header) + "\n"
        return header_content + "\n".join(yaml_lines)

    return "\n".join(yaml_lines)


# TODO extract into a standalone service/module responsible for schema resolution
def get_structured_schema(schema: NestedDict) -> NestedDict:
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


# TODO extract into own module for handling schema formatting
def schema_formatter(
    structured_schema: NestedDict, callback: Callable[[str], Any], level: int = 0
):
    DEFAULT_INTENT: str = "  "
    intent: str = DEFAULT_INTENT * level

    for title, content in structured_schema.items():
        if any(isinstance(value, dict) for value in content.values()):
            callback(f"{intent}{title}:")
            schema_formatter(content, callback, level + 1)
        else:
            base_line: str = f"{intent}{title}: "
            default_value: str = content.get("default", "")
            value_type: str = content.get("type", "")
            description: str = content.get("description", "")

            callback(
                base_line
                + (str(default_value) if default_value else "")
                + (
                    f"  # Type: {value_type} - Description: {description}"
                    if value_type and description
                    else f"  # Type: {value_type}"
                    if value_type
                    else f" # Description: {description}"
                    if description
                    else ""
                )
            )
