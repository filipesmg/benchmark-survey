import sys
import argparse

import json
import re
import textwrap
import yaml
from jinja2 import Environment, BaseLoader
tags_cats_to_tex_commands = {
    'programming-model': 'btProgMod',
    'programming-language': 'btProgLang',
    'benchmark-scale': 'btScale',
    'memory-access-characteristics': 'btMemAcc',
    'method-type': 'btMethod',
    'communication': 'btComm',
    'application-domain': 'btAppDomain',
    'compute-performance-characteristics': 'btCompPerf',
    'communication-performance-characteristics': 'btCommPerf',
    'mesh-representation': 'btMesh',
    'math-libraries': 'btMath'
}
license_to_tex_commands = {
    'bsd': r'\licBsd',
    'bsd-4-clause': r'\licBsdFour',
    'bsd-3-clause': r'\licBsdThree',
    'bsd-2-clause': r'\licBsdTwo',
    'mit': r'\licMit',
    'none': r'\licNone',
    'free': r'\licFree',
    'gpl': r'\licGpl',
    'gpl-3.0': r'\licGplThree',
    'gpl-2.0': r'\licGplTwo',
    'lgpl-2.1': r'\licLgplTwoone',
    'proprietary': r'\licProp',
    'apache-2.0': r'\licApacheTwo',
    'mpl-2.0': r'\licMplTwo',
}
sort_order_tags = {cat: (i, cat) for i, cat in enumerate(["programming-language", "programming-model"])}
def customSortTags(tags):
    return sorted(tags, key=lambda cat: sort_order_tags.get(cat[0], (len(sort_order_tags), cat[0]))) #https://stackoverflow.com/a/64593268
def parseTags(rawTags):
    _tags = []
    for tag in rawTags:
        rawcat, name = tag.split(':')
        cat = tags_cats_to_tex_commands[rawcat] if rawcat in tags_cats_to_tex_commands else 'NA'
        _tags.append((cat, name))
    return _tags
def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
        credit: https://stackoverflow.com/a/25875504
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)
tpl_suite_tableheader = r"""% do not change this file manually! it's auto-generated
\begin{longtblr}[
    caption={Benchmark Overview. Benchmark suites are indicated by leftmost entries with individual subordinated benchmark entries, connected by a dotted line. Per benchmark, tags, license (\emph{Lic.}), URL, reference (\emph{Ref.}), and notes are given; if each component is common to all benchmarks in a suite, the components are listed for the suite itself.},
    entry = {Benchmark Overview Table},
    label = {table:benchmarks}
]{
    width   = \textwidth,
    colspec = {X[0.01]|[dotted]X[0.8,l]X[1.4]ccX[3]},
    cells   = {font=\footnotesize},
    row{1}  = {font=\footnotesize\bfseries}, rowhead = 1,
    rowsep = 0.3pt
}
\SetCell[c=2]{l} \emph{(Suite-)}Name & & Tags & Lic. & URL, Ref. & Notes \\
\midrule"""
tpl_suite_tablefooter = r"""
\end{longtblr}
"""
tpl_suite_table = r"""
    ((* if multicol -*))\SetCell[c=2]{l} ((( name ))) & &
    ((*- else -*))
    & ((( name ))) &
    ((*- endif *))
    ((* for tag in tags *)) \((( tag[0] ))){((( tag[1] )))} ((*- endfor *)) &
    ((* if license -*)) ((( license ))) ((* endif -*)) &
    ((* if url['key'] -*))\href{((( url['long'] )))}{\scalebox{0.8}{\faIcon{link}}}~\cite{((( url['key'] )))}((* endif -*)) ((* if url and citekey -*)), ((* endif -*)) ((* if citekey -*)) \cite{((( citekey )))} ((* endif -*)) &
    ((* if notes -*)) ((( notes ))) ((* endif -*))\\
"""
tpl_bib_link = r"""
@electronic{((( key ))),
 title     = {{((( name )))}},
 url       = {((( url )))}
}
"""
def main(args):

    with open('benchmarks.yaml', 'r') as f:
        benchmarks = yaml.safe_load(f)

    environment = Environment(
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        comment_start_string='((=',
        comment_end_string='=))',
        # line_statement_prefix='%%',
        # line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=BaseLoader
    )

    benchmark_tex = tpl_suite_tableheader
    bib_urls_tex = ""
    sorted_benchmarks = dict(sorted(benchmarks.items()))
    sorted_benchmarks = sorted(sorted_benchmarks.items(), key=lambda b: b[0].startswith('benchmark'))  # sort "benchmarks key to the end (https://stackoverflow.com/a/57301615)
    for suitekey, suitedata in dict(sorted_benchmarks).items():
        multicol=True
        last_suite_bench=False
        insuite=True
        if suitekey != "benchmarks":  # go to next loop
            benchmark_tex += genTableRow(suitekey, suitedata, suitekey=suitekey, last_suite_bench=last_suite_bench, multicol=multicol, jinjaenv=environment)
            bib_urls_tex += genBibUrl(suitekey, suitedata, jinjaenv=environment)
            benchmarks = suitedata['benchmarks']
            multicol=False
        else:
            benchmarks = suitedata
            insuite=False
            suitekey=""
        for benchkey, benchdata in benchmarks.items():
            if insuite and (benchkey == list(benchmarks.keys())[-1]):
                last_suite_bench=True
            benchmark_tex += genTableRow(benchkey, benchdata, suitekey=suitekey, last_suite_bench=last_suite_bench, multicol=multicol, jinjaenv=environment)
            bib_urls_tex += genBibUrl(benchkey, benchdata, jinjaenv=environment)
    benchmark_tex += tpl_suite_tablefooter
    if args.print:
        print(benchmark_tex)
        print(bib_urls_tex)
    if args.write:
        outfile = f"benchmark_table.tex"
        with open(outfile, mode="w", encoding="utf-8") as output:
            print(f'Writing to {outfile}', file=sys.stderr)
            output.write(benchmark_tex) 
        outfile = f"benchmarklinks.bib"
        with open(outfile, mode="w", encoding="utf-8") as output:
            print(f'Writing to {outfile}', file=sys.stderr)
            output.write(bib_urls_tex)
def genTableRow(benchkey, benchdata, suitekey, last_suite_bench, multicol, jinjaenv):
    name = tex_escape(benchdata['name'])
    license = license_to_tex_commands.get(benchdata['license'].lower(), benchdata['license']) if 'license' in benchdata else ''
    notes = tex_escape(benchdata['notes']) if 'notes' in benchdata else ''
    ref = f'{benchkey}_ref' if 'ref' in benchdata else ''
    tags = parseTags(benchdata['tags']) if 'tags' in benchdata else ''
    url = {
        'long': benchdata['url'] if 'url' in benchdata else '',
        'short': benchdata['url'].replace('https://', '').replace('http://', '') if 'url' in benchdata else '',
        'key': f'{benchkey}_link' if 'url' in benchdata else ''
    }
    return jinjaenv.from_string(textwrap.dedent(tpl_suite_table)).render(key=benchkey, name=name, license=license, notes=notes, citekey=ref, tags=tags, url=url, multicol=multicol, suitekey=suitekey, last_suite_bench=last_suite_bench)
def genBibUrl(benchkey, benchdata, jinjaenv):
    if 'url' in benchdata:
        name = tex_escape(benchdata['name'])
        url = benchdata['url'] 
        key = f'{benchkey}_link'
        return jinjaenv.from_string(textwrap.dedent(tpl_bib_link)).render(key=key, name=name, url=url)
    else:
        return ""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='HPC Benchmarks Survey Table Generator', description='Generate a LaTeX table from YAML')
    parser.add_argument('-p', '--print', action='store_true', default=True, help='Print generated template(s)')
    parser.add_argument('-w', '--write', action='store_true', help='Write generated template file(s)')
    args = parser.parse_args()
    main(args)
