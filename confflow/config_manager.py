from typing import Any, Dict, List, TypeAlias

from pydantic import BaseModel

from .common.types import Schema, SchemaName
from .core.registry.schema_registry import SchemaRegistry
from .core.rule_engine.base_rule import BaseRule
from .core.rule_engine.rule_engine import RuleEngine

ConfigurationMap: TypeAlias = Dict[SchemaName, BaseModel]
DefaultsMap: TypeAlias = Dict[Schema, Dict[str, Any]]

TEMPLATE_HEADER: List[str] = [  # TODO move it to a module level
    "================================================================================",
    "                                  Configuration Template                        ",
    "================================================================================",
    "",
    "Purpose:",
    "  - Use this template to set up configuration values for your environment.",
    "",
    "Instructions:",
    "  - Fill in each field with appropriate values.",
    "  - Refer to the documentation for detailed descriptions of each field.",
    "",
    "Notes:",
    "  - Only one configuration per mutually exclusive group can be active at a time.",
    "  - Ensure data types match the specified type for each field.",
    "",
    "================================================================================",
]


class ConfigManager:
    def __init__(self) -> None:
        self._registry = SchemaRegistry()
        self._ruler = RuleEngine(registry=self._registry)
        self._data: ConfigurationMap = {}

    def register_schemas(
        self,
        *schemas: Schema,
    ) -> None:
        for schema in schemas:
            self._registry.register(schema)

    def register_rules(self, *rules: BaseRule) -> None:
        for rule in rules:
            missing_schemas: set[Schema] = rule.referenced_schemas - set(
                self._registry.schema_types
            )

            if missing_schemas:
                raise ValueError(
                    f"The following schemas are not registered: {missing_schemas}"
                )

            self._ruler.register(rule)

    def set_configs(self, *configs: BaseModel) -> None:
        for config in configs:
            schema_name: SchemaName = config.__class__.__name__

            if schema_name not in self._registry:
                raise ValueError(f"Schema '{schema_name}' is not registered.")

            active_configs: list[BaseModel] = list(self._data.values())
            active_configs.append(config)

            self._ruler.validate(active_configs)

            self._data[schema_name] = config

    def __getitem__(self, key: str) -> BaseModel:
        return self._data[key].model_dump()

    # def save(self, output_path: PathLike) -> None:
    #     output_path: Path = Path(output_path)
    #     if not self._data:
    #         raise ValueError("No configurations to save.")
    #     defaults: DefaultsMap = {
    #         type(config): config.model_dump() for config in self._data.values()
    #     }
    #     to_file(
    #         schemas=list(self._data.values()),
    #         format="yaml",
    #         path=output_path,
    #         header=["Generated configuration file"],
    #         defaults=defaults,
    #     )

    # def create_template(self, output_path: PathLike) -> None:
    #     to_file(  # TODO correct it
    #         header=TEMPLATE_HEADER,
    #         schemas=self._registry.schema_types,
    #         exclusive_groups=self.exclusive_groups,
    #         format="yaml",
    #         path=output_path,
    #     )

    # def load(self, input_path: PathLike) -> None:
    #     input_path = Path(input_path)
    #     if not input_path.exists():
    #         raise FileNotFoundError(f"Configuration file not found: {input_path}")

    #     with open(input_path, "r", encoding="utf-8") as f:
    #         parsed_data: Dict[str, Any] = yaml.safe_load(f) or {}

    #     loaded_configurations: ConfigurationMap = {}
    #     loaded_names = set(parsed_data.keys())

    #     exclusive_names = {
    #         schema.__name__ for group in self.exclusive_groups for schema in group
    #     }

    #     required_names = {
    #         schema.__name__
    #         for schema in self._schema_registry.schemas
    #         if schema.__name__ not in exclusive_names
    #     }

    #     missing_required = required_names - loaded_names
    #     if missing_required:
    #         raise ValueError(
    #             f"Missing configuration(s) for required schema(s): {sorted(missing_required)}"
    #         )

    #     for group in self.exclusive_groups:
    #         group_names = {schema.__name__ for schema in group}
    #         present = group_names & loaded_names
    #         if len(present) == 0:
    #             raise ValueError(
    #                 f"No configuration provided for mutually exclusive group: {sorted(group_names)}"
    #             )
    #         if len(present) > 1:
    #             raise ValueError(
    #                 f"Multiple configurations provided for mutually exclusive group {sorted(group_names)}: {sorted(present)}"
    #             )

    #     for schema_name, config_data in parsed_data.items():
    #         schema_class = self._schema_registry[schema_name]
    #         if not schema_class:
    #             raise ValueError(f"Unknown schema type: '{schema_name}'")
    #         loaded_configurations[schema_name] = schema_class(**config_data)

    #     self._data = loaded_configurations
