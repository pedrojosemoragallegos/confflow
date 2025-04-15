SCHEMA_PROPERTIES_KEY: str = "properties"
SCHEMA_REQUIERED_KEY: str = "required"
SCHEMA_DEFINITIONS_KEY: str = "$defs"
SCHEMA_REFERENCE_KEY: str = "$ref"
SCHEMA_DESCRIBSION_KEY: str = "description"


# 1. resolve requiered || used for all schemas
def _resolve_requiered(schema: dict) -> dict:
    property_names: list[str] = schema[SCHEMA_PROPERTIES_KEY].keys()
    required_names: list[str] = schema[SCHEMA_REQUIERED_KEY]

    for property_name in property_names:
        schema[SCHEMA_PROPERTIES_KEY][property_name][SCHEMA_REQUIERED_KEY] = (
            True if property_name in required_names else False
        )

    schema.pop(SCHEMA_REQUIERED_KEY)

    return schema


# 2. resolve definitions
def _resolve_definitions(schema: dict) -> dict:
    definitions: dict = schema[SCHEMA_DEFINITIONS_KEY]

    for schema_name, schema_content in definitions.items():
        for property_name, property_content in schema_content[
            SCHEMA_PROPERTIES_KEY
        ].items():
            property_content.pop(SCHEMA_DESCRIBSION_KEY)

            if SCHEMA_REFERENCE_KEY in property_content:
                referenced_schema_name: str = property_content[
                    SCHEMA_REFERENCE_KEY
                ].split("/")[-1]
                property_content |= definitions[referenced_schema_name][
                    SCHEMA_PROPERTIES_KEY
                ]
                property_content.pop(SCHEMA_REFERENCE_KEY)

    for property_name, property_content in schema[SCHEMA_PROPERTIES_KEY].items():
        if SCHEMA_REFERENCE_KEY in property_content:
            referenced_schema_name: str = property_content[SCHEMA_REFERENCE_KEY].split(
                "/"
            )[-1]
            property_content |= definitions[referenced_schema_name][
                SCHEMA_PROPERTIES_KEY
            ]
            property_content.pop(SCHEMA_REFERENCE_KEY)

            schema[SCHEMA_PROPERTIES_KEY][property_name] = property_content

    schema.pop(SCHEMA_DEFINITIONS_KEY)
    return schema


# FINAL
def parse_schema(schema: dict) -> dict:
    # resolve required - schema
    schema = _resolve_requiered(schema)
    # resolve required - schema definitions
    schema_definitions = schema.get(SCHEMA_DEFINITIONS_KEY, {})

    for schema_name in schema_definitions.keys():
        schema_definitions[schema_name] = _resolve_requiered(
            schema_definitions[schema_name]
        )

    schema[SCHEMA_DEFINITIONS_KEY] = schema_definitions

    schema = _resolve_definitions(schema)
    schema.pop("type")

    return schema
