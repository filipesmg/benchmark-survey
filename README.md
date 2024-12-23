# HPC Benchmark Survey

A survey of existing HPC benchmarks and benchmark suites. See also [benchmark taxonomy](https://github.com/LLNL/benchmark-taxonomy).

The list of benchmarks collected here in a machine-readable manner is transformed into tables, like a TeX table for a paper.

## Benchmark YAML Scheme

Rules: 

1. Top-level keys can be either a name of a suite or `benchmarks`
2. A benchmark is identify with a unique key, and sibling keys `name`, `tags`, `license`, `url`, `ref`; with the according values
3. If the top-level key is a suite, the sibling keys are the same as _benchmark keys_ (`name`, `tags`, `license`, `url`, `ref`) plus a key `benchmark`, which contains keys for each benchmark like in 2.

Notes:

* Mandatory: `name` and (`url` or `ref `)
* `license`: use SPDX identifiers; be conscious of the distinction between a suite license and license for the individual benchmarks, they can be different
* `ref`: DOI


```yaml
rajaperf:
  name: RAJAPerf
  tags: [raja]
  license: BSD-3-Clause
  url: https://github.com/LLNL/RAJAPerf/
  # ref: none
  benchmarks:
    stream:
      name: STREAM
      tags: [benchmark-scale:single-node, memory-access-characteristics:regular-memory-access, programming-language:c]  # inline lists are a little more space-efficient
      license: free
      url: https://www.cs.virginia.edu/stream/
      ref: doi/1.2jladf
    polybench:
      name: PolyBench
      #...
benchmarks:
  hpl:
    name: HPL
```

A schema file exists to validate entries against this scheme. Validate with

```bash
pajv validate -s schema.json -d benchmark.yaml
```

## Conversion

Currently, only a script for conversion to TeX is available; see `./tex-gen/`.
