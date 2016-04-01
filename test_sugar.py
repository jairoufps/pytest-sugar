# -*- coding: utf-8 -*-
import pytest

pytest_plugins = "pytester"


class TestTerminalReporter(object):
    def test_deselecting_tests(self, testdir):
        testdir.makepyfile(
            """
            import pytest
            @pytest.mark.example
            def test_func():
                assert True

            def test_should_be():
                assert False
            """
        )
        result = testdir.runpytest('-m', 'example')
        result.stdout.fnmatch_lines(['*1 passed*', '*1 deselected*'])

    def test_fail(self, testdir):
        testdir.makepyfile(
            """
            import pytest
            def test_func():
                assert 0
            """
        )
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "* test_func *",
            "    def test_func():",
            ">       assert 0",
            "E       assert 0",
        ])

    def test_fail_unicode_crashline(self, testdir):
        testdir.makepyfile(
            """
            # -*- coding: utf-8 -*-
            import pytest
            def test_func():
                assert b'hello' == b'Bj\\xc3\\xb6rk Gu\\xc3\\xb0mundsd\\xc3\\xb3ttir'
            """
        )
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "* test_func *",
            "    def test_func():",
            ">       assert * == *",
            "E       assert * == *",
        ])

    def test_fail_fail(self, testdir):
        testdir.makepyfile(
            """
            import pytest
            def test_func():
                assert 0
            def test_func2():
                assert 0
            """
        )
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "* test_func *",
            "    def test_func():",
            ">       assert 0",
            "E       assert 0",
            "* test_func2 *",
            "    def test_func2():",
            ">       assert 0",
            "E       assert 0",
        ])

    def test_error_in_setup_then_pass(self, testdir):
        testdir.makepyfile(
            """
            def setup_function(function):
                print ("setup func")
                if function is test_nada:
                    assert 0
            def test_nada():
                pass
            def test_zip():
                pass
            """
        )
        result = testdir.runpytest()

        result.stdout.fnmatch_lines([
            "*ERROR at setup of test_nada*",
            "",
            "function = <function test_nada at *",
            "",
            "*setup_function(function):*",
            "*setup func*",
            "*if function is test_nada:*",
            "*assert 0*",
            "test_error_in_setup_then_pass.py:4: AssertionError",
            "*Captured stdout setup*",
            "*setup func*",
            "*1 passed*",
        ])
        assert result.ret != 0

    def test_error_in_teardown_then_pass(self, testdir):
        testdir.makepyfile(
            """
            def teardown_function(function):
                print ("teardown func")
                if function is test_nada:
                    assert 0
            def test_nada():
                pass
            def test_zip():
                pass
            """
        )
        result = testdir.runpytest()

        result.stdout.fnmatch_lines([
            "*ERROR at teardown of test_nada*",
            "",
            "function = <function test_nada at*",
            "",
            "*def teardown_function(function):*",
            "*teardown func*",
            "*if function is test_nada*",
            ">*assert 0*",
            "E*assert 0*",
            "test_error_in_teardown_then_pass.py:4: AssertionError",
            "*Captured stdout teardown*",
            "teardown func",
            "*2 passed*",
        ])
        assert result.ret != 0

    def test_collect_error(self, testdir):
        testdir.makepyfile("""raise ValueError(0)""")
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*ERROR collecting test_collect_error.py*",
            "test_collect_error.py:1: in <module>",
            "    raise ValueError(0)",
            "E   ValueError: 0",
        ])

    def test_xdist(self, testdir):
        pytest.importorskip("xdist")
        testdir.makepyfile(
            """
            def test_nada():
                pass
            def test_zip():
                pass
            """
        )
        result = testdir.runpytest('-n2')

        assert result.ret == 0, result.stderr.str()
