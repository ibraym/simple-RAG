# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

with open('dataset1.txt', 'w') as f2:
    with open('geo-reviews-dataset-2023.tskv', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 500:
                break
            parts = line.split('	')
            line = '	'.join([part for part in parts if part.startswith(('name_ru', 'rubrics', 'text'))])
            f2.write(f'{line}')