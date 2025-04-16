PROPERTIES_KEY: str = "properties"
REQUIRED_KEY: str = "required"
DEFINITIONS_KEY: str = "$defs"
REFERENCE_KEY: str = "$ref"
DESCRIPTION_KEY: str = "description"
TYPE_KEY: str = "type"


def _resolve_required(schema: dict) -> dict:
    property_names = schema.get(PROPERTIES_KEY, {}).keys()
    required_names = schema.get(REQUIRED_KEY, [])

    for property_name in property_names:
        schema[PROPERTIES_KEY][property_name][REQUIRED_KEY] = (
            property_name in required_names
        )

    schema.pop(REQUIRED_KEY, None)
    return schema


def _resolve_reference(property_content: dict, definitions: dict) -> dict:
    ref_name = property_content[REFERENCE_KEY].split("/")[-1]
    ref_properties = definitions.get(ref_name, {}).get(PROPERTIES_KEY, {})
    new_content = {**property_content, **ref_properties}
    new_content.pop(REFERENCE_KEY, None)
    return new_content


def _resolve_definitions(schema: dict) -> dict:
    definitions = schema.get(DEFINITIONS_KEY, {})

    for schema_content in definitions.values():
        for property_name, property_content in schema_content.get(
            PROPERTIES_KEY, {}
        ).items():
            if REFERENCE_KEY in property_content:
                schema_content[PROPERTIES_KEY][property_name] = _resolve_reference(
                    property_content, definitions
                )

    for property_name, property_content in schema.get(PROPERTIES_KEY, {}).items():
        if REFERENCE_KEY in property_content:
            schema[PROPERTIES_KEY][property_name] = _resolve_reference(
                property_content, definitions
            )

    schema.pop(DEFINITIONS_KEY, None)
    return schema


def parse_schema(schema: dict) -> dict:
    schema = _resolve_required(schema)

    definitions = schema.get(DEFINITIONS_KEY, {})
    for name, content in definitions.items():
        definitions[name] = _resolve_required(content)
    schema[DEFINITIONS_KEY] = definitions

    schema = _resolve_definitions(schema)
    schema.pop(TYPE_KEY, None)

    return schema
