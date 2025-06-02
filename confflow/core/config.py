# from collections import OrderedDict
# from collections.abc import ItemsView, Iterable, Iterator, KeysView, ValuesView
# from typing import Optional, final

# from confflow.protocols import Constraint

# from .field import FieldType, FieldValue, create_field


# @final
# class Config:
#     def __init__(self, name: str, description: str = ""):
#         self._name: str = name
#         self._description: str = description
#         self._fields: OrderedDict[str, FieldType] = OrderedDict()

#     def addField(
#         self,
#         value: FieldValue,
#         name: str,
#         description: str = "",
#         default_value: Optional[FieldValue] = None,
#         required: bool = False,
#         constraints: Optional[Iterable[Constraint[FieldValue]]] = None,
#     ) -> "Config":
#         if name in self._fields:
#             raise ValueError(f"Field with name '{name}' already exists.")

#         self._fields[name] = create_field(
#             value=value,
#             name=name,
#             description=description,
#             default_value=default_value,
#             required=required,
#             constraints=constraints,
#         )

#         return self

#     def keys(self) -> KeysView[str]:
#         return self._fields.keys()

#     def values(self) -> ValuesView[FieldType]:
#         return self._fields.values()

#     def items(self) -> ItemsView[str, FieldType]:
#         return self._fields.items()

#     def __getitem__(self, key: str) -> FieldType:
#         return self._fields[key]

#     def __contains__(self, key: str) -> bool:
#         return key in self._fields

#     def __iter__(self) -> Iterator[str]:
#         return iter(self._fields)

#     def __len__(self) -> int:
#         return len(self._fields)

#     def __repr__(self) -> str:
#         return (
#             f"{self.__class__.__name__}("
#             f"name={self._name!r}, "
#             f"description={self._description!r}, "
#             f"fields={[field for field in self._fields.values()]!r})"
#         )

#     # Only for iPython # TODO maybe remove here add as mixin or so
#     def _ipython_key_completions_(self) -> list[str]:
#         return list(self._fields.keys())
