import pytest

from .utils import make_cobertura


def remove_style_tag(html):
    style_pattern_start = '\n    <style>'
    style_pattern_stop = '\n    </style>'
    style_starts = html.find(style_pattern_start)
    style_stops = html.find(style_pattern_stop) + len(style_pattern_stop)
    html_nostyle = html[:style_starts] + html[style_stops:]
    return html_nostyle


def test_text_report():
    from pycobertura.reporters import TextReporter

    cobertura = make_cobertura()
    report = TextReporter(cobertura)

    assert report.generate() == """\
Filename                          Stmts    Miss  Cover    Missing
------------------------------  -------  ------  -------  ---------
Main.java                            15       0  100.00%
search/BinarySearch.java             12       1  91.67%   24
search/ISortedArraySearch.java        0       0  100.00%
search/LinearSearch.java              7       2  71.43%   19-24
TOTAL                                34       3  90.00%"""


def test_text_report__with_missing_range():
    from pycobertura.reporters import TextReporter

    cobertura = make_cobertura('tests/dummy.with-dummy2-no-cov.xml')
    report = TextReporter(cobertura)

    assert report.generate() == """\
Filename             Stmts    Miss  Cover    Missing
-----------------  -------  ------  -------  ---------
dummy/__init__.py        0       0  0.00%
dummy/dummy.py           4       0  100.00%
dummy/dummy2.py          2       2  0.00%    1-2
TOTAL                    6       2  66.67%"""


def test_text_report_delta__no_diff():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source1/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Filename      Stmts    Miss  Cover     Missing
----------  -------  ------  --------  ---------
TOTAL             0       0  +100.00%"""


def test_text_report_delta__colorize_True():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
TOTAL                 +4      \x1b[31m+1\x1b[39m  +31.06%"""


def test_text_report_delta__colorize_True__with_missing_range():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
TOTAL                 +4      \x1b[31m+1\x1b[39m  +31.06%"""


def test_text_report_delta__colorize_False():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=False)

    assert report_delta.generate() == """\
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      -2  +40.00%
dummy/dummy2.py       +2      +1  -25.00%   5
dummy/dummy3.py       +2      +2  +100.00%  1, 2
TOTAL                 +4      +1  +31.06%"""


def test_html_report():
    from pycobertura.reporters import HtmlReporter

    cobertura = make_cobertura()
    report = HtmlReporter(cobertura)
    html_output = report.generate()

    assert "normalize.css" in html_output
    assert "Skeleton V2.0" in html_output

    assert remove_style_tag(html_output) == """\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <div class="container">
      <h1>pycobertura report</h1>
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#Main.java">Main.java</a></td>
            <td>15</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td><a href="#search/BinarySearch.java">search/BinarySearch.java</a></td>
            <td>12</td>
            <td>1</td>
            <td>91.67%</td>
            <td>24</td>
          </tr>
          <tr>
            <td><a href="#search/ISortedArraySearch.java">search/ISortedArraySearch.java</a></td>
            <td>0</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td><a href="#search/LinearSearch.java">search/LinearSearch.java</a></td>
            <td>7</td>
            <td>2</td>
            <td>71.43%</td>
            <td>19-24</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>34</td>
            <td>3</td>
            <td>90.00%</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
<h4 id="Main.java">Main.java</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>0 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">tests/Main.java not found</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="search/BinarySearch.java">search/BinarySearch.java</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>0 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">tests/search/BinarySearch.java not found</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="search/ISortedArraySearch.java">search/ISortedArraySearch.java</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>0 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">tests/search/ISortedArraySearch.java not found</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="search/LinearSearch.java">search/LinearSearch.java</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>0 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">tests/search/LinearSearch.java not found</span></pre>
      </td>
    </tr>
  </tbody>
</table>

    </div>
  </body>
</html>"""


def test_html_report__no_source_files_message():
    from pycobertura.reporters import HtmlReporter

    cobertura = make_cobertura()
    report = HtmlReporter(cobertura, title="test report", render_file_sources=False)
    html_output = report.generate()

    assert "normalize.css" in html_output
    assert "Skeleton V2.0" in html_output

    assert remove_style_tag(html_output) == """\
<html>
  <head>
    <title>test report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <div class="container">
      <h1>test report</h1>
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Main.java</td>
            <td>15</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td>search/BinarySearch.java</td>
            <td>12</td>
            <td>1</td>
            <td>91.67%</td>
            <td>24</td>
          </tr>
          <tr>
            <td>search/ISortedArraySearch.java</td>
            <td>0</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td>search/LinearSearch.java</td>
            <td>7</td>
            <td>2</td>
            <td>71.43%</td>
            <td>19-24</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>34</td>
            <td>3</td>
            <td>90.00%</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
<p>Rendering of source files was disabled.</p>
    </div>
  </body>
</html>"""


def test_text_report_delta__no_source():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, show_source=False)
    output = report_delta.generate()
    assert output == """\
Filename           Stmts    Miss  Cover
---------------  -------  ------  --------
dummy/dummy.py         0      -2  +40.00%
dummy/dummy2.py       +2      +1  -25.00%
dummy/dummy3.py       +2      +2  +100.00%
TOTAL                 +4      +1  +31.06%"""


def test_html_report_delta__no_source():
    from pycobertura.reporters import HtmlReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = HtmlReporterDelta(cobertura1, cobertura2, show_source=False)
    html_output = report_delta.generate()
    assert 'Missing' not in html_output
    assert '<h4 id=' not in html_output

    assert remove_style_tag(html_output) == """\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <div class="container">
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#dummy/dummy.py">dummy/dummy.py</a></td>
            <td>0</td>
            <td><span class="green">-2</span></td>
            <td>+40.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy2.py">dummy/dummy2.py</a></td>
            <td>+2</td>
            <td><span class="red">+1</span></td>
            <td>-25.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy3.py">dummy/dummy3.py</a></td>
            <td>+2</td>
            <td><span class="red">+2</span></td>
            <td>+100.00%</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>+4</td>
            <td><span class="red">+1</span></td>
            <td>+31.06%</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </body>
</html>"""


def test_html_report_delta():
    from pycobertura.reporters import HtmlReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = HtmlReporterDelta(cobertura1, cobertura2)
    html_output = report_delta.generate()
    assert '.red {color: red}' in html_output
    assert '.green {color: green}' in html_output
    assert "normalize.css" in html_output
    assert "Skeleton V2.0" in html_output

    assert remove_style_tag(html_output) == u"""\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <div class="container">
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#dummy/dummy.py">dummy/dummy.py</a></td>
            <td>0</td>
            <td><span class="green">-2</span></td>
            <td>+40.00%</td>
            <td>
            </td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy2.py">dummy/dummy2.py</a></td>
            <td>+2</td>
            <td><span class="red">+1</span></td>
            <td>-25.00%</td>
            <td><span class="red">5</span>
            </td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy3.py">dummy/dummy3.py</a></td>
            <td>+2</td>
            <td><span class="red">+2</span></td>
            <td>+100.00%</td>
            <td><span class="red">1</span>, <span class="red">2</span>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>+4</td>
            <td><span class="red">+1</span></td>
            <td>+31.06%</td>
            <td></td>
          </tr>
        </tfoot>
      </table><div class="legend">
  <dl>
    <dt><code>code</code></dt><dd>coverage unchanged</dd>
    <dt class="hit"><code>code</code></dt><dd>coverage increased</dd>
    <dt class="miss"><code>code</code></dt><dd>coverage decreased</dd>
    <dt><code>+</code></dt><dd>line added or modified</dd>
  </dl>
</div>
<h4 id="dummy/dummy.py">dummy/dummy.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>2 &nbsp;
3 &nbsp;
4 &nbsp;
5 &nbsp;
6 +
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">    pass
</span><span class="noop">
</span><span class="noop">def bar():
</span><span class="hit">    a = &#39;a&#39;
</span><span class="hit">    d = &#39;d&#39;
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="dummy/dummy2.py">dummy/dummy2.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>1 &nbsp;
2 +
3 &nbsp;
4 +
5 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">def baz():
</span><span class="hit">    c = &#39;c&#39;
</span><span class="noop">
</span><span class="hit">def bat():
</span><span class="miss">    pass
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="dummy/dummy3.py">dummy/dummy3.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>1 +
2 +
</pre>
      </td>
      <td class="source">
        <pre><span class="miss">def foobar():
</span><span class="miss">    pass  # This is a very long comment that was purposefully written so we could test how HTML rendering looks like when the boundaries of the page are reached. And here is a non-ascii char: \u015e
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
    </div>
  </body>
</html>"""


def test_html_report_delta__show_missing_False():
    from pycobertura.reporters import HtmlReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = HtmlReporterDelta(cobertura1, cobertura2, show_missing=False)
    html_output = report_delta.generate()

    assert remove_style_tag(html_output) == u"""\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <div class="container">
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#dummy/dummy.py">dummy/dummy.py</a></td>
            <td>0</td>
            <td><span class="green">-2</span></td>
            <td>+40.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy2.py">dummy/dummy2.py</a></td>
            <td>+2</td>
            <td><span class="red">+1</span></td>
            <td>-25.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy3.py">dummy/dummy3.py</a></td>
            <td>+2</td>
            <td><span class="red">+2</span></td>
            <td>+100.00%</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>+4</td>
            <td><span class="red">+1</span></td>
            <td>+31.06%</td>
          </tr>
        </tfoot>
      </table><div class="legend">
  <dl>
    <dt><code>code</code></dt><dd>coverage unchanged</dd>
    <dt class="hit"><code>code</code></dt><dd>coverage increased</dd>
    <dt class="miss"><code>code</code></dt><dd>coverage decreased</dd>
    <dt><code>+</code></dt><dd>line added or modified</dd>
  </dl>
</div>
<h4 id="dummy/dummy.py">dummy/dummy.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>2 &nbsp;
3 &nbsp;
4 &nbsp;
5 &nbsp;
6 +
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">    pass
</span><span class="noop">
</span><span class="noop">def bar():
</span><span class="hit">    a = &#39;a&#39;
</span><span class="hit">    d = &#39;d&#39;
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="dummy/dummy2.py">dummy/dummy2.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>1 &nbsp;
2 +
3 &nbsp;
4 +
5 &nbsp;
</pre>
      </td>
      <td class="source">
        <pre><span class="noop">def baz():
</span><span class="hit">    c = &#39;c&#39;
</span><span class="noop">
</span><span class="hit">def bat():
</span><span class="miss">    pass
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
<h4 id="dummy/dummy3.py">dummy/dummy3.py</h4>
<table class="code u-max-full-width">
  <tbody>
    <tr>
      <td class="lineno">
        <pre>1 +
2 +
</pre>
      </td>
      <td class="source">
        <pre><span class="miss">def foobar():
</span><span class="miss">    pass  # This is a very long comment that was purposefully written so we could test how HTML rendering looks like when the boundaries of the page are reached. And here is a non-ascii char: \u015e
</span></pre>
      </td>
    </tr>
  </tbody>
</table>
    </div>
  </body>
</html>"""

@pytest.mark.parametrize(
    "report, expected_default_output, expected_custom_output",
    [
        (
            "tests/cobertura.xml",
            """\
::notice file=search/BinarySearch.java,line=24,endLine=24,title=pycobertura::not covered
::notice file=search/LinearSearch.java,line=19,endLine=24,title=pycobertura::not covered""",
            """\
::error file=search/BinarySearch.java,line=24,endLine=24,title=JCov::missing coverage
::error file=search/LinearSearch.java,line=19,endLine=24,title=JCov::missing coverage""",
        ),
        (
            "tests/cobertura-generated-by-istanbul-from-coffeescript.xml",
            "::notice file=app.coffee,line=10,endLine=10,title=pycobertura::not covered",
            "::error file=app.coffee,line=10,endLine=10,title=JCov::missing coverage",
        ),
    ],
)
def test_github_annotation_report(
    report, expected_default_output, expected_custom_output
):
    from pycobertura.reporters import GitHubAnnotationReporter

    cobertura = make_cobertura(report)
    report = GitHubAnnotationReporter(cobertura)
    default_config = {
        "annotation_level": "notice",
        "annotation_title": "pycobertura",
        "annotation_message": "not covered",
    }

    assert report.generate(**default_config) == expected_default_output
    assert (
        report.generate(
            annotation_level="error",
            annotation_title="JCov",
            annotation_message="missing coverage",
        )
        == expected_custom_output
    )


@pytest.mark.parametrize(
    "report1, report2, config, expected_default_output, expected_custom_output",
    [
        (
            "tests/dummy.source1/coverage.xml",
            "tests/dummy.source2/coverage.xml",
            {
                "annotation_level":"error",
                "annotation_title":"JCov",
                "annotation_message":"missing coverage"
            },
            """\
::notice file=dummy/dummy2.py,line=5,endLine=5,title=pycobertura::not covered
::notice file=dummy/dummy3.py,line=1,endLine=2,title=pycobertura::not covered""",
            """\
::error file=dummy/dummy2.py,line=5,endLine=5,title=JCov::missing coverage
::error file=dummy/dummy3.py,line=1,endLine=2,title=JCov::missing coverage""",
        ),
    ],
)
def test_github_annotation_report_delta(
    report1, report2, config, expected_default_output, expected_custom_output
):
    from pycobertura.reporters import GitHubAnnotationReporterDelta

    cobertura1 = make_cobertura(report1)
    cobertura2 = make_cobertura(report2)

    default_config = {
        "annotation_level": "notice",
        "annotation_title": "pycobertura",
        "annotation_message": "not covered",
    }
    report_delta = GitHubAnnotationReporterDelta(
        cobertura1, cobertura2, show_missing=False
    )
    assert report_delta.generate(**default_config) == expected_default_output
    assert report_delta.generate(**config) == expected_custom_output

