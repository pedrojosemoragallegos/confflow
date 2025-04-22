import copy
from typing import Any, Optional

from ..common.utils import get_by_key_path


def _resolve_property_references(
    property_content: dict[str, Any], *, references_map: dict[str, Any]
) -> dict[str, Any]:
    property_content: dict[str, Any] = copy.deepcopy(property_content)

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


def _resolve_model_properties_references(
    properties: dict[str, Any], reference_map: dict[str, Any]
) -> dict[str, Any]:
    properties: dict[str, Any] = copy.deepcopy(properties)

    for property_name in properties.keys():  # NOTE could use .items()
        properties[property_name] = _resolve_property_references(
            properties[property_name], references_map=reference_map
        )

    return properties


def _resolve_model_properties_requirement(
    properties: dict[str, Any], *, required: list[str]
) -> dict[str, Any]:
    properties: dict[str, Any] = copy.deepcopy(properties)

    for property_name in properties.keys():
        properties[property_name]["required"] = property_name in required

        if "properties" in properties[property_name]:
            # nested_required = properties[property_name].get("requiredFields", []) # NOTE never understood why lol
            nested_required: list[str] = []

            if "required" in properties[property_name] and isinstance(
                properties[property_name]["required"], list
            ):
                nested_required = properties[property_name]["required"]

            properties[property_name]["properties"] = (
                _resolve_model_properties_requirement(
                    properties[property_name]["properties"], required=nested_required
                )
            )

    return properties


def resolve_schema(model_json_schema: dict[str, Any]) -> dict[str, Any]:
    model_json_schema: dict[str, Any] = copy.deepcopy(model_json_schema)

    if "$defs" in model_json_schema:
        model_json_schema["properties"] = _resolve_model_properties_references(
            model_json_schema["properties"], reference_map=model_json_schema["$defs"]
        )

        model_json_schema.pop("$defs")

    model_json_schema["properties"] = _resolve_model_properties_requirement(
        model_json_schema["properties"], required=model_json_schema["required"]
    )

    model_json_schema.pop("required")

    return model_json_schema


def inject_set_value(
    schema: dict[str, Any], values_to_inject: dict[str, Any]
) -> dict[str, Any]:
    def inject_recursively(
        schema_section: dict[str, Any], values_section: dict[str, Any]
    ) -> None:
        if not isinstance(schema_section, dict) or not isinstance(values_section, dict):
            return

        for field_name, injected_value in values_section.items():
            if field_name in schema_section:
                schema_field = schema_section[field_name]
                if (
                    isinstance(injected_value, dict)
                    and isinstance(schema_field, dict)
                    and "properties" in schema_field
                ):
                    inject_recursively(schema_field["properties"], injected_value)
                else:
                    schema_field["value"] = injected_value

    updated_schema: dict[str, Any] = copy.deepcopy(schema)
    inject_recursively(updated_schema, values_to_inject)

    return updated_schema
