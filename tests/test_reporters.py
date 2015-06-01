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
Name                         Stmts    Miss  Cover    Missing
-------------------------  -------  ------  -------  ---------
Main                            11       0  100.00%
search.BinarySearch             12       1  91.67%   24
search.ISortedArraySearch        0       0  100.00%
search.LinearSearch              7       2  71.43%   19-24
TOTAL                           30       3  90.00%"""


def test_text_report__with_missing_range():
    from pycobertura.reporters import TextReporter

    cobertura = make_cobertura('tests/dummy.with-dummy2-no-cov.xml')
    report = TextReporter(cobertura)

    assert report.generate() == """\
Name              Stmts    Miss  Cover    Missing
--------------  -------  ------  -------  ---------
dummy/__init__        0       0  0.00%
dummy/dummy           4       0  100.00%
dummy/dummy2          2       2  0.00%    1-2
TOTAL                 6       2  66.67%"""


def test_text_report_delta__no_diff():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source1/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name    Stmts    Miss    Cover    Missing
------  -------  ------  -------  ---------
TOTAL   -        -       -"""


def test_text_report_delta__colorize_True():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL         +4           \x1b[31m+1\x1b[39m  +15.00%"""


def test_text_report_delta__colorize_True__with_missing_range():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL         +4           \x1b[31m+1\x1b[39m  +15.00%"""


def test_text_report_delta__colorize_False():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=False)

    assert report_delta.generate() == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            -2  +40.00%  -5, -6
dummy/dummy2  +2           +1  -25.00%  -2, -4, +5
dummy/dummy3  +2           +2  -        +1, +2
TOTAL         +4           +1  +15.00%"""


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
      <table class="u-full-width">
        <thead>
          <tr>
            <th>Name</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#Main">Main</a></td>
            <td>11</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td><a href="#search.BinarySearch">search.BinarySearch</a></td>
            <td>12</td>
            <td>1</td>
            <td>91.67%</td>
            <td>24</td>
          </tr>
          <tr>
            <td><a href="#search.ISortedArraySearch">search.ISortedArraySearch</a></td>
            <td>0</td>
            <td>0</td>
            <td>100.00%</td>
            <td></td>
          </tr>
          <tr>
            <td><a href="#search.LinearSearch">search.LinearSearch</a></td>
            <td>7</td>
            <td>2</td>
            <td>71.43%</td>
            <td>19-24</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>30</td>
            <td>3</td>
            <td>90.00%</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
<h4 id="Main">Main</h4>
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
<h4 id="search.BinarySearch">search.BinarySearch</h4>
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
<h4 id="search.ISortedArraySearch">search.ISortedArraySearch</h4>
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
<h4 id="search.LinearSearch">search.LinearSearch</h4>
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


def test_text_report_delta__no_source():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, show_source=False)
    output = report_delta.generate()
    assert output == """\
Name          Stmts      Miss  Cover
------------  -------  ------  -------
dummy/dummy   -            -2  +40.00%
dummy/dummy2  +2           +1  -25.00%
dummy/dummy3  +2           +2  -
TOTAL         +4           +1  +15.00%"""


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
            <th>Name</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#dummy/dummy">dummy/dummy</a></td>
            <td>-</td>
            <td><span class="green">-2</span></td>
            <td>+40.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy2">dummy/dummy2</a></td>
            <td>+2</td>
            <td><span class="red">+1</span></td>
            <td>-25.00%</td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy3">dummy/dummy3</a></td>
            <td>+2</td>
            <td><span class="red">+2</span></td>
            <td>-</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>+4</td>
            <td><span class="red">+1</span></td>
            <td>+15.00%</td>
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
            <th>Name</th>
            <th>Stmts</th>
            <th>Miss</th>
            <th>Cover</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#dummy/dummy">dummy/dummy</a></td>
            <td>-</td>
            <td><span class="green">-2</span></td>
            <td>+40.00%</td>
            <td><span class="green">-5</span>, <span class="green">-6</span>
            </td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy2">dummy/dummy2</a></td>
            <td>+2</td>
            <td><span class="red">+1</span></td>
            <td>-25.00%</td>
            <td><span class="green">-2</span>, <span class="green">-4</span>, <span class="red">+5</span>
            </td>
          </tr>
          <tr>
            <td><a href="#dummy/dummy3">dummy/dummy3</a></td>
            <td>+2</td>
            <td><span class="red">+2</span></td>
            <td>-</td>
            <td><span class="red">+1</span>, <span class="red">+2</span>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>TOTAL</td>
            <td>+4</td>
            <td><span class="red">+1</span></td>
            <td>+15.00%</td>
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
<h4 id="dummy/dummy">dummy/dummy</h4>
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
<h4 id="dummy/dummy2">dummy/dummy2</h4>
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
<h4 id="dummy/dummy3">dummy/dummy3</h4>
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
