#!/bin/bash

set -eux -o pipefail

i3-msg "[workspace=5] move workspace to output DP-2"
i3-msg "[workspace=6] move workspace to output DP-1-1"
i3-msg "[workspace=8] move workspace to output DP-2"
i3-msg "[workspace=9] move workspace to output DP-1-1"
