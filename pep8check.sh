#!/bin/bash
find . -name "*.py" -exec pycodestyle --max-line-length=180 {} \;
