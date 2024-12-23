SCHEMA ?= schema.json

validate: benchmarks.yaml
	pajv validate -s ${SCHEMA} -d $<
.PHONY: validate