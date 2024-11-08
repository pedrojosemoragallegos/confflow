from typing import Any, Dict, List, Optional

from pydantic import BaseModel


def create_yaml(
    schema_map: Dict[str, Any],
    configs: Optional[Dict[str, BaseModel]] = None,
    header: Optional[List[str]] = None,
    mutually_exclusive_groups: Optional[List[List[str]]] = None,
) -> str:
    template: Dict[str, Dict[str, Any]] = _generate(
        schema_map=schema_map,
        configs=configs,
    )
    formatted_yaml_content: str = _format_yaml(template, mutually_exclusive_groups)

    if header:
        header_content = "\n".join(header) + "\n"
        return header_content + formatted_yaml_content

    return formatted_yaml_content


def _generate(
    schema_map: Dict[str, Any],
    configs: Optional[Dict[str, BaseModel]] = None,
) -> Dict[str, Dict[str, Any]]:
    template: Dict[str, Dict[str, Any]] = {}

    for key, conf_class in schema_map.items():
        if configs and key not in configs:
            continue

        properties = conf_class.model_json_schema().get("properties", {}).items()
        schema_template: Dict[str, Dict[str, Any]] = {}

        for identifier, schema in properties:
            config_default = (
                configs.get(key).model_dump().get(identifier)
                if configs and configs.get(key)
                else None
            )

            schema_template[identifier] = {
                "default": config_default
                if config_default is not None
                else schema.get("default"),
                "type": schema.get("type"),
                "description": schema.get("description", ""),
                **{
                    name: v
                    for name, v in schema.items()
                    if name not in ["default", "type", "description", "title"]
                },
            }

        template[key] = schema_template

    return template


def _format_yaml(
    template: Dict[str, Dict[str, Any]],
    mutually_exclusive_groups: Optional[List[List[str]]] = None,
) -> str:
    yaml_lines: List[str] = []
    yaml_lines.append("")

    handled_groups = set()

    for key, schemas in template.items():
        current_group = next(
            (group for group in (mutually_exclusive_groups or []) if key in group), None
        )

        if current_group and not handled_groups.intersection(current_group):
            yaml_lines.append("# -------------------------------------")
            yaml_lines.append("# Mutual exclusive group: Pick only one")
            yaml_lines.append("# -------------------------------------")

            for group_key in current_group:
                yaml_lines.append(f"{group_key}:")
                _append_schemas_to_yaml(group_key, template, yaml_lines)
                yaml_lines.append("")

            yaml_lines.append("# -------------------------------------")
            yaml_lines.append("")
            handled_groups.update(current_group)

        elif not current_group:
            yaml_lines.append(f"{key}:")
            _append_schemas_to_yaml(key, template, yaml_lines)
            yaml_lines.append("")

    return "\n".join(yaml_lines)


def _append_schemas_to_yaml(
    key: str, template: Dict[str, Dict[str, Any]], yaml_lines: List[str]
):
    schemas = template[key]

    max_identifier_length: int = max(len(identifier) for identifier in schemas.keys())
    max_value_length: int = max(
        len(str(schema.get("default", ""))) if schema.get("default") is not None else 0
        for schema in schemas.values()
    )

    type_column_start: int = max_identifier_length + max_value_length + 7
    description_column_start: int = type_column_start + 17

    for identifier, schema in schemas.items():
        yaml_lines.append(
            _format_schema_line(
                identifier, schema, type_column_start, description_column_start
            )
        )


def _format_schema_line(
    identifier: str,
    schema: Dict[str, Any],
    type_column_start: int,
    description_column_start: int,
) -> str:
    default_value: Any = schema.get("default")

    if isinstance(default_value, str):
        default_value = f'"{default_value}"'

    type_comment: str = f"Type: {schema.get('type')}"

    constraints: List[str] = [
        f"{k}={v!r}"
        for k, v in schema.items()
        if k not in ["default", "type", "description", "title"]
    ]

    if constraints:
        type_comment += f" ({', '.join(constraints)})"

    description_comment: str = (
        f"    Description: {schema['description']}" if schema.get("description") else ""
    )

    yaml_line: str = (
        f"  {identifier}: {default_value}"
        if default_value is not None
        else f"  {identifier}:"
    )

    type_padding: int = type_column_start - len(yaml_line)
    yaml_line += f"{' ' * type_padding}# {type_comment}"

    description_padding: int = description_column_start - len(yaml_line)
    yaml_line += f"{' ' * description_padding}{description_comment}"

    return yaml_line
