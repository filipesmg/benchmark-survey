import sys
import argparse

import json
import textwrap
import yaml
from jinja2 import Environment, BaseLoader
tags_cats_to_tex_commands = {
    'programming-model': 'btProgMod',
    'programming-language': 'btProgLang',
    'benchmark-scale': 'btScale'
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

    # Artifact association

    bench_rel_tpl = r"""
    % this file is auto-generated, do not change it manually!
    $A_{((( number )))}$ is the benchmark setup for $C_{1,((( number )))}$ ( (((- name -))) )."""

    bench_exp_tpl = r"""
    % this file is auto-generated, do not change it manually!
    We expect a seamless setup using the provided repository, following the instructions in \texttt{DESCRIPTION.md}. ((* if base -*)) Given a similar execution environment, scaling results similar to the ones provided in Figure 2 ((* if weak -*)) and Figure 3 ((* endif -*)) of the manuscript. ((* endif -*))"""

    bench_artsw_tpl = r"""
    % this file is auto-generated, do not change it manually!
    $A_{((( number )))}$ ( (((- name -))) ) uses EasyBuild modules of the following software components (including version numbers): ((( modules|join(', ') )))"""

    bench_artdata_tpl = r"""
    % this file is auto-generated, do not change it manually!
    The benchmark utilizes no input dataset; all data is generated on-the-fly as part of the benchmark."""

    bench_artdeploy_tpl = r"""
    % this file is auto-generated, do not change it manually!
    ((* if name in compile_strings *))Compilation is integrated into the JUBE script and described in detail in \texttt{DESCRIPTION.md} in the benchmark's repository. Relevant for the compilation of ((( name ))) is the following snippet: 
    \begin{minted}{bash}
    ((( compile_strings[name] -)))
    \end{minted}
    ((* else *))
    The benchmark does not need to be compiled.
    ((* endif -*))
    """

    bench_artcomp_tpl = r"""
    % this file is auto-generated, do not change it manually!
    $A_{((( number )))}$ ( (((- name -))) ) includes the file ((*- if jubefiles | length > 1 -*))s((*- endif *)) ((*- for jubefile in jubefiles *)) \Verb|((( jubefile )))| ((*- if (loop.length > 2) and (loop.index != loop.length) -*)), ((*- endif -*)) ((*- if loop.index == loop.length - 1 *)) and ((*- endif -*)) ((* endfor *)), which contain ((*- if jubefiles | length == 1 -*))s((*- endif *)) the execution instructions for JUBE. Find details in \texttt{DESCRIPTION.md}."""

    bench_artout_tpl = r"""
    % this file is auto-generated, do not change it manually!
    See details in \texttt{DESCRIPTION.md} in the benchmark's repository."""

    tpl_suite_header = r"""
    ((* if suite -*))\multicolumn{2}{l}{((( name )))} & 
    ((*- else -*))
    & ((( name ))) &
    ((*- endif *))
    ((*- for tag in tags *)) \((( tag[0] ))){((( tag[1] )))} ((*- endfor *)) &
    ((* if license -*)) ((( license ))) ((* endif *)) & 
    ((* if url['long'] -*)) \href{((( url['long'] )))}{((( url['short'] )))}} ((* endif *)) ((* if citekey -*)) \cite{((( citekey )))} ((* endif *)) & 
    ((* if notes -*)) ((( notes ))) ((* endif *))\\
    """

    # for i, benchmark in enumerate(benchmarks):
    #     print(f"Rendering template for {item}:{benchmark}")
    #     base = 'Base' in appinfos[benchmark]['featured_figures']
    #     weak = 'Weak' in appinfos[benchmark]['featured_figures']
    #     number = i+1
    #     modules = all_modules[benchmark]
    #     jubefiles = appinfos[benchmark]['jube_files']
    #     jube_run_paths = appinfos[benchmark]['jube_run_paths']
    #     # jubefiles_other = appinfos[benchmark]['jube_files_other']
    #     rendered_template = environment.from_string(
    #             textwrap.dedent(template).strip()).render(
    #                     number=number, name=benchmark,
    #                     base=base, weak=weak, modules=modules,
    #                     jubefiles=jubefiles,
    #                     jube_run_paths=jube_run_paths,
    #                     compile_strings=apps_compile_strings,
    #                     run_strings=apps_run_strings,
    #                     eval_strings=apps_eval_strings)
    #     if args.print:
    #         print(rendered_template)
    #     if args.write:
    #         outfile = f"{folder}/{benchmark.replace(' ', '-')}.tex"
    #         with open(outfile, mode="w", encoding="utf-8") as output:
    #             print(f'Writing to {outfile}', file=sys.stderr)
    #             output.write(rendered_template)

    benchmark_tex = ""
    sorted_benchmarks = sorted(benchmarks.items(), key=lambda b: b[0].startswith('benchmark'))  # sort "benchmarks key to the end (https://stackoverflow.com/a/57301615)
    for benchkey, benchdata in dict(sorted_benchmarks).items():
        if benchkey == "benchmarks":  # go to next loop
            continue
        # print(benchdata)
        name = benchdata['name']
        license = benchdata['license'] if 'license' in benchdata else ''
        notes = benchdata['notes'] if 'notes' in benchdata else ''
        ref = f'link_{benchkey}' if 'ref' in benchdata else ''
        tags = parseTags(benchdata['tags']) if 'tags' in benchdata else ''
        url = {
            'long': benchdata['url'] if 'url' in benchdata else '',
            'short': benchdata['url'].replace('https://', '').replace('http://', '') if 'url' in benchdata else ''
        }
        suite=True
        print(environment.from_string(tpl_suite_header).render(name=name, license=license, notes=notes, citekey=ref, tags=tags, url=url, suite=suite))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='HPC Benchmarks Survey Table Generator', description='Generate a LaTeX table from YAML')
    parser.add_argument('-p', '--print', action='store_true', default=True, help='Print generated template(s)')
    parser.add_argument('-w', '--write', action='store_true', help='Write generated template file(s)')
    args = parser.parse_args()
    main(args)
