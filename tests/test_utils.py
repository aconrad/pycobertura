import pytest

from pycobertura.utils import memoize


class TestMemoize:
    def test_memoize_caches_method_results(self):
        """Tests that the memoize decorator caches method results."""

        class MyClass:
            def __init__(self):
                self.call_count = 0

            @memoize
            def my_method(self, arg1, arg2):
                self.call_count += 1
                return arg1 + arg2

        instance = MyClass()

        # First call - should execute the method
        result1 = instance.my_method(1, 2)
        assert result1 == 3
        assert instance.call_count == 1

        # Second call with same args - should return cached result
        result2 = instance.my_method(1, 2)
        assert result2 == 3
        assert instance.call_count == 1 # Count should not increase

        # Call with different args - should execute the method again
        result3 = instance.my_method(3, 4)
        assert result3 == 7
        assert instance.call_count == 2 # Count should increase

        # Call again with the first set of args - should return cached result
        result4 = instance.my_method(1, 2)
        assert result4 == 3
        assert instance.call_count == 2 # Count should not increase

        # Call again with the second set of args - should return cached result
        result5 = instance.my_method(3, 4)
        assert result5 == 7
        assert instance.call_count == 2 # Count should not increase

    def test_memoize_different_instances(self):
        """Tests that memoization is instance-specific."""

        class MyClass:
            def __init__(self):
                self.call_count = 0

            @memoize
            def my_method(self, arg):
                self.call_count += 1
                return arg * 2

        instance1 = MyClass()
        instance2 = MyClass()

        # Call on instance1
        result1_1 = instance1.my_method(5)
        assert result1_1 == 10
        assert instance1.call_count == 1
        assert instance2.call_count == 0

        # Call on instance2 with the same arg
        result2_1 = instance2.my_method(5)
        assert result2_1 == 10
        assert instance1.call_count == 1
        assert instance2.call_count == 1 # instance2 count increases

        # Call on instance1 again
        result1_2 = instance1.my_method(5)
        assert result1_2 == 10
        assert instance1.call_count == 1 # instance1 count stays the same
        assert instance2.call_count == 1

    def test_memoize_with_kwargs(self):
        """Tests that memoization works with keyword arguments."""

        class MyClass:
            def __init__(self):
                self.call_count = 0

            @memoize
            def my_method(self, a, b=0):
                self.call_count += 1
                return a + b

        instance = MyClass()

        # Call with positional args
        res1 = instance.my_method(1, b=2)
        assert res1 == 3
        assert instance.call_count == 1

        # Call with same args using kwargs
        res2 = instance.my_method(a=1, b=2)
        assert res2 == 3
        assert instance.call_count == 1 # Should be cached

        # Call with different kwargs order
        res3 = instance.my_method(b=2, a=1)
        assert res3 == 3
        assert instance.call_count == 1 # Should be cached

        # Call with different value for kwarg
        res4 = instance.my_method(a=1, b=3)
        assert res4 == 4
        assert instance.call_count == 2 # New call

        # Call using default value
        res5 = instance.my_method(5)
        assert res5 == 5
        assert instance.call_count == 3 # New call

        # Call again using default value
        res6 = instance.my_method(5, b=0)
        assert res6 == 5
        assert instance.call_count == 3 # Should be cached
