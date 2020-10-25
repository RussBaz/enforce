import typing
from numbers import Integral

import pytest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class TestGenericTypes:
    """
    Tests for the generic types
    """

    def test_custom_generic_initialisation(self):
        """
        Verifies that user defined generics can be initialised
        """
        T = typing.TypeVar("T")

        class Sample(typing.Generic[T]):
            pass

        SD = runtime_validation(Sample)

        ST = Sample[int]
        SDT = SD[int]

        s = Sample()
        sd = SD()
        st = ST()
        sdt = SDT()

        assert not hasattr(s, "__enforcer__")
        assert not hasattr(st, "__enforcer__")
        assert hasattr(sd, "__enforcer__")
        assert hasattr(sdt, "__enforcer__")

        assert sd.__enforcer__.signature == Sample
        assert sdt.__enforcer__.signature == Sample

        assert sd.__enforcer__.generic == SD.__enforcer__.generic
        assert sdt.__enforcer__.generic == SDT.__enforcer__.generic

        assert sd.__enforcer__.bound == SD.__enforcer__.bound
        assert sdt.__enforcer__.bound == SDT.__enforcer__.bound

        for hint_name, hint_value in sdt.__enforcer__.hints.items():
            assert hint_value == SDT.__enforcer__.hints[hint_name]

        assert len(sdt.__enforcer__.hints) == len(SDT.__enforcer__.hints)

    def test_custom_generic_validation(self):
        """
        Verifies that user defined generic can be used as a type hint
        """
        T = typing.TypeVar("T")

        @runtime_validation
        class Sample(typing.Generic[T]):
            def get(self, data: T) -> T:
                return data

        @runtime_validation
        def return_int(data: Sample[int], arg: int) -> int:
            return data.get(arg)

        @runtime_validation
        def return_any(data: Sample) -> typing.Any:
            return data

        good = Sample[int]()
        bad = Sample[str]()
        other = Sample()
        strange = Sample[T]()

        en_1 = return_int.__enforcer__
        en_2 = good.__enforcer__
        en_3 = other.__enforcer__
        en_4 = strange.__enforcer__

        assert return_int(good, 1) == 1
        assert return_any(other) is other

        # TODO: Find out exactly what should be be happening in this case
        # self.assertIs(return_any(strange), strange)

        with pytest.raises(RuntimeTypeError):
            return_int(bad, 1)

        with pytest.raises(RuntimeTypeError):
            return_int(other, 1)

        with pytest.raises(RuntimeTypeError):
            return_int(strange, 1)

        with pytest.raises(RuntimeTypeError):
            return_any(good)

        with pytest.raises(RuntimeTypeError):
            return_any(bad)

    def test_numbers_with_aliases_and_named_tuple(self):
        """
        Verifies if 'numbers' can be used in type aliases and in NamedTuples
        """
        Interval = typing.Tuple[Integral, Integral]
        Annotation = typing.NamedTuple(
            "Annotation",
            [
                ("source", typing.Text),
                ("start", Integral),
                ("end", Integral),
                ("text", typing.Text),
                ("cls", typing.Text),
            ],
        )
        TypedAnnotation = runtime_validation(Annotation)
