from typing import Any, Dict, List

PROPERTIES_KEY: str = "properties"
REQUIRED_KEY: str = "required"
DEFINITIONS_KEY: str = "$defs"
REFERENCE_KEY: str = "$ref"
DESCRIPTION_KEY: str = "description"
TYPE_KEY: str = "type"


def _resolve_required(schema: Dict[str, Any]) -> Dict[str, Any]:
    property_names: List[str] = list(schema.get(PROPERTIES_KEY, {}).keys())
    required_names: List[str] = schema.get(REQUIRED_KEY, [])

    property_dict: Dict[str, Any] = schema.get(PROPERTIES_KEY, {})

    for property_name in property_names:
        if property_name in property_dict:
            property_dict[property_name][REQUIRED_KEY] = property_name in required_names

    schema.pop(REQUIRED_KEY, None)

    return schema


def _resolve_reference(
    property_content: Dict[str, Any], definitions: Dict[str, Any]
) -> Dict[str, Any]:
    ref_path: str = property_content[REFERENCE_KEY]
    ref_name: str = ref_path.split("/")[-1]
    ref_schema: Dict[str, Any] = definitions.get(ref_name, {})
    ref_properties: Dict[str, Any] = ref_schema.get(PROPERTIES_KEY, {})

    new_content: Dict[str, Any] = {**property_content, **ref_properties}

    new_content.pop(REFERENCE_KEY, None)

    return new_content


def _resolve_definitions(schema: Dict[str, Any]) -> Dict[str, Any]:
    definitions: Dict[str, Any] = schema.get(DEFINITIONS_KEY, {})

    for schema_content in definitions.values():
        property_dict: Dict[str, Any] = schema_content.get(PROPERTIES_KEY, {})

        for property_name, property_content in property_dict.items():
            if REFERENCE_KEY in property_content:
                property_dict[property_name] = _resolve_reference(
                    property_content, definitions
                )

    root_properties: Dict[str, Any] = schema.get(PROPERTIES_KEY, {})

    for property_name, property_content in root_properties.items():
        if REFERENCE_KEY in property_content:
            root_properties[property_name] = _resolve_reference(
                property_content, definitions
            )

    schema.pop(DEFINITIONS_KEY, None)

    return schema


def parse_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    schema: Dict[str, Any] = _resolve_required(schema)

    definitions: Dict[str, Any] = schema.get(DEFINITIONS_KEY, {})
    name: str
    content: Dict[str, Any]
    for name, content in definitions.items():
        definitions[name] = _resolve_required(content)

    schema[DEFINITIONS_KEY] = definitions
    schema = _resolve_definitions(schema)

    schema.pop(TYPE_KEY, None)

    return schema
