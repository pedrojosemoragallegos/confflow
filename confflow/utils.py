from typing import Any, Union, get_args, get_origin


def recursive_is_instance(value: Any, expected_type: Any) -> bool:
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # Case 1: Primitive or non-generic types
    if origin is None:
        return isinstance(value, expected_type)

    # Case 2: List[...] check
    if origin is list:
        if not isinstance(value, list):
            return False
        if not args:
            return True
        return all(recursive_is_instance(item, args[0]) for item in value)

    # Case 3: Union[...] check
    if origin is Union:
        return any(recursive_is_instance(value, arg) for arg in args)

    # Case 4: Dict[...] check
    if origin is dict:
        if not isinstance(value, dict):
            return False
        key_type, val_type = args
        return all(
            recursive_is_instance(k, key_type) and recursive_is_instance(v, val_type)
            for k, v in value.items()
        )

    # Case 5: Set[...] check
    if origin is set:
        if not isinstance(value, set):
            return False
        (elem_type,) = args
        return all(recursive_is_instance(item, elem_type) for item in value)

    # Case 6: Handle generic classes like BaseField[...]
    try:
        base_origin = get_origin(expected_type) or expected_type
        if args:
            # Try validating against the inner type (e.g., BaseField[T] → T)
            return recursive_is_instance(value, args[0])
        else:
            return isinstance(value, base_origin)
    except TypeError:
        return False
