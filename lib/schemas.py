from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Generic, Literal, TypeVar, get_args, get_origin, overload

import ujson
from marshmallow import EXCLUDE, Schema, post_load

T = TypeVar("T")


class BaseSchema(Schema, Generic[T]):
    _domain_cls: type[T]
    _to_domain: Callable[[dict[str, Any]], T]

    class Meta:
        render_module = ujson
        unknown = EXCLUDE

    def __init_subclass__(cls) -> None:
        """Get the domain object from the generic alias"""

        base, *_ = cls.__orig_bases__  # type: ignore[attr-defined]
        domain, *_ = get_args(base)
        origin = get_origin(domain)

        if origin is dict:
            cls._domain_cls = origin
            cls._to_domain = lambda _, data: data  # type: ignore[misc, assignment]
        else:
            cls._domain_cls = domain
            cls._to_domain = lambda _, data: cls._domain_cls(**data)  # type: ignore[misc, assignment]

    @post_load
    def to_domain(self, incoming_data: dict[str, Any], **_kwargs: Any) -> T:
        return self._to_domain(incoming_data)

    @overload  # type: ignore[override]
    def load(
        self,
        data: Mapping[str, Any] | Iterable[Mapping[str, Any]],
        *,
        many: Literal[True],
        partial: Sequence[str] | set[str] | bool | None = None,
        unknown: str | None = None,
    ) -> list[T]: ...

    @overload
    def load(
        self,
        data: Mapping[str, Any] | Iterable[Mapping[str, Any]],
        *,
        many: Literal[False] = False,
        partial: Sequence[str] | set[str] | bool | None = None,
        unknown: str | None = None,
    ) -> T: ...

    def load(
        self,
        data: Mapping[str, Any] | Iterable[Mapping[str, Any]],
        *,
        many: bool | None = None,
        partial: Sequence[str] | set[str] | bool | None = None,
        unknown: str | None = None,
    ) -> T | list[T]:
        return super().load(data, many=many, partial=partial, unknown=unknown)  # type: ignore[no-any-return]

    @overload  # type: ignore[override]
    def dump(
        self,
        data: Any,
        *,
        many: Literal[True],
    ) -> list[dict[str, Any]]: ...

    @overload
    def dump(
        self,
        data: Any,
        *,
        many: Literal[False] = False,
    ) -> dict[str, Any]: ...

    def dump(
        self,
        data: Any,
        *,
        many: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return super().dump(data, many=many)  # type: ignore[no-any-return]
