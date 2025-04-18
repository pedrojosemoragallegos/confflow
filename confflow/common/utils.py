import copy
from typing import Any, Dict, List, Optional


def get_by_key_path(dictionary: Dict[str, Any], *, key_path: List[str]) -> Any:
    if not key_path:
        raise ValueError("'key_path' list is empty.")

    if key_path[0] not in dictionary:
        raise KeyError(f"Reference '{key_path[0]}' not found in dictionary.")

    data: Any = dictionary[key_path[0]]

    if len(key_path) == 1:
        return data
    else:
        return get_by_key_path(dictionary=data, key_path=key_path[1:])


def resolve_reference(
    property_content: dict[str, Any], *, references_map: dict[str, Any]
) -> dict[str, Any]:
    property_content = copy.deepcopy(property_content)

    def get_referenced_model(ref_content: dict[str, Any]) -> dict[str, Any]:
        reference_path: str = ref_content["$ref"]

        reference_key_path: list[str] = reference_path.split("/")[2:]

        return get_by_key_path(references_map, key_path=reference_key_path)

    def resolve(property_content: dict[str, Any]) -> dict[str, Any]:
        if "$ref" in property_content:
            description: Optional[str] = property_content.get("description", "")

            referenced_model: dict[str, Any] = copy.deepcopy(
                get_referenced_model(property_content)
            )

            if description:
                referenced_model["description"] = description

            property_content: dict[str, Any] = referenced_model

        if "properties" in property_content:
            for property_name in property_content["properties"].keys():
                property_content["properties"][property_name] = resolve(
                    property_content["properties"][property_name]
                )

        return property_content

    return resolve(property_content)


def resolve_references(
    properties: dict[str, Any], reference_map: dict[str, Any]
) -> dict[str, Any]:
    properties = copy.deepcopy(properties)

    for property_name in properties.keys():
        properties[property_name] = resolve_reference(
            properties[property_name], references_map=reference_map
        )

    return properties


def resolve_required(
    properties: dict[str, Any], *, required: list[str]
) -> dict[str, Any]:
    properties = copy.deepcopy(properties)

    for property_name in properties.keys():
        properties[property_name]["required"] = property_name in required

        if "properties" in properties[property_name]:
            nested_required = properties[property_name].get("requiredFields", [])
            if "required" in properties[property_name] and isinstance(
                properties[property_name]["required"], list
            ):
                nested_required = properties[property_name]["required"]

            properties[property_name]["properties"] = resolve_required(
                properties[property_name]["properties"], required=nested_required
            )

    return properties


def resolve_properties(
    properties: dict[str, Any], *, reference_map: dict[str, Any], required: list[str]
) -> dict[str, Any]:
    properties = copy.deepcopy(properties)
    properties = resolve_references(properties, reference_map=reference_map)
    properties = resolve_required(properties, required=required)

    return properties


def resolve_schemas(
    schemas: dict[str, Any], *, reference_map: dict[str, Any]
) -> dict[str, Any]:
    schemas = copy.deepcopy(schemas)

    for schema_name in schemas.keys():
        schemas[schema_name]["properties"] = resolve_properties(
            schemas[schema_name]["properties"],
            reference_map=reference_map,
            required=schemas[schema_name]["required"],
        )

    return schemas


def build_tree_string(dictionary: dict, prefix: str = "") -> str:
    lines: list[str] = []
    items: list[tuple[str, any]] = list(dictionary.items())
    for i, (key, value) in enumerate(items):
        connector: str = "└── " if i == len(items) - 1 else "├── "
        lines.append(prefix + connector + str(key))
        if isinstance(value, dict):
            extension: str = "    " if i == len(items) - 1 else "│   "
            subtree: str = build_tree_string(value, prefix + extension)
            lines.append(subtree)
        else:
            leaf_connector: str = "└── "
            extension: str = "    " if i == len(items) - 1 else "│   "
            lines.append(prefix + extension + leaf_connector + str(value))
    return "\n".join(lines)
