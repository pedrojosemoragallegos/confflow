from typing import Any, Dict, Iterator, List, Optional

from pydantic import BaseModel as BaseConfig

from .formatter import Formatter


class YAMLFormatter(Formatter):
    def generate(
        schemas: List[BaseConfig],
        header: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Dict[str, Any]]] = None,
        mutually_exclusive_groups: Optional[List[List[str]]] = [],
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

        if default_values:
            schemas: List[BaseConfig] = [
                schema for schema in schemas if schema.__name__ in default_values
            ]
        else:
            default_values = {}

        skipped_indices: List[int] = []
        yaml_lines: List[str] = []
        for current_index, schema in enumerate(schemas):
            if current_index in skipped_indices:
                continue

            group_index: Optional[int] = index_to_group_map.get(current_index)
            if group_index is not None:
                BLOCK_START: List[str] = [
                    "# -------------------------------------",
                    "# Mutual exclusive group: Pick only one",
                    "# -------------------------------------",
                ]
                yaml_lines.extend(BLOCK_START)

                iterator: Iterator = iter(
                    mutually_exlusive_grouped_indices[group_index]
                )
                while True:
                    try:
                        index: int = next(iterator)
                        YAMLFormatter._schema_formatter(
                            YAMLFormatter._get_structured_schema(
                                schema=schemas[index].model_json_schema(
                                    mode="validation"
                                )
                            ),
                            callback=lambda x: yaml_lines.append(x),
                        )
                        skipped_indices.append(index)
                        yaml_lines.append("\n")
                    except StopIteration:
                        BLOCK_END: List[str] = (
                            "# -------------------------------------\n"
                        )
                        yaml_lines[-1] = BLOCK_END
                        break
            else:
                YAMLFormatter._schema_formatter(
                    YAMLFormatter._get_structured_schema(
                        schema=schema.model_json_schema(mode="validation")
                    ),
                    callback=lambda x: yaml_lines.append(x),
                    default_values=default_values.get(schema.__name__, {}),
                )
                yaml_lines.append("\n")
        if header:
            header_content: str = "\n".join(header) + "\n"
            return header_content + "\n".join(yaml_lines)

        return "\n".join(yaml_lines)
