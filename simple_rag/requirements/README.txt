To regenerate the `*.txt` files in this directory, run:

    pip-compile-multi -d simple_rag/requirements \
        --backtracking --allow-unsafe --autoresolve --skip-constraints

Make sure to use the same Python version as is used in the main Dockerfile.