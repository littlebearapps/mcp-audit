# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                     |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------- | -------: | -------: | ------: | --------: |
| src/mcp\_audit/\_\_init\_\_.py           |       38 |       20 |     47% |12-14, 37-47, 50-56, 59-65, 68-70, 73-75, 78-80, 83-85, 95-103, 107-114 |
| src/mcp\_audit/base\_tracker.py          |      431 |       18 |     96% |167, 177-180, 449-469, 799, 1073, 1087-1089, 1098-1103 |
| src/mcp\_audit/claude\_code\_adapter.py  |      371 |      183 |     51% |81, 136-138, 209, 214-260, 271, 286-356, 422-423, 433-434, 442, 455, 475, 478-479, 488-566, 620, 695-698, 793-829, 864-898 |
| src/mcp\_audit/cli.py                    |      866 |      553 |     36% |76-95, 119-503, 574-585, 607, 641-643, 678-698, 726-747, 854, 939-1004, 1009-1160, 1165-1173, 1178-1182, 1187-1202, 1207-1261, 1266-1317, 1327-1338, 1343-1380, 1438-1442, 1455-1463, 1493-1497, 1508, 1562-1566, 1601-1668, 1673-1809, 1814-1864, 1875-1883, 1897-1916 |
| src/mcp\_audit/codex\_cli\_adapter.py    |      482 |      256 |     47% |196, 203, 207, 211, 224-226, 241-242, 276-277, 303-304, 316-319, 328-381, 385-467, 511-550, 554-591, 726, 801, 871-900, 924-959, 1037-1038, 1078-1204 |
| src/mcp\_audit/display/\_\_init\_\_.py   |       26 |        4 |     85% |     75-81 |
| src/mcp\_audit/display/ascii\_mode.py    |       22 |        0 |    100% |           |
| src/mcp\_audit/display/base.py           |        8 |        0 |    100% |           |
| src/mcp\_audit/display/null\_display.py  |       12 |        0 |    100% |           |
| src/mcp\_audit/display/plain\_display.py |       45 |        8 |     82% |67, 77-85, 91 |
| src/mcp\_audit/display/rich\_display.py  |      318 |      155 |     51% |70-77, 81-94, 98, 102-106, 131-132, 145, 147, 152-153, 155, 157, 159-160, 163, 206, 219-224, 226-229, 262-263, 303-304, 330-331, 347, 351-359, 369, 378-380, 394, 405-419, 426-435, 470-475, 478, 484-627 |
| src/mcp\_audit/display/snapshot.py       |       44 |        0 |    100% |           |
| src/mcp\_audit/display/theme\_detect.py  |       58 |        7 |     88% |50-51, 55-57, 130, 132 |
| src/mcp\_audit/display/themes.py         |      293 |       51 |     83% |117, 145, 153, 157, 202, 206, 210, 214, 218, 222, 226, 230, 234, 238, 242, 246, 250, 254, 258, 262, 266, 270, 291, 295, 299, 303, 308, 316, 329, 333, 337, 342, 346, 350, 354, 358, 379, 383, 387, 391, 396, 404, 408, 417, 421, 425, 430, 434, 438, 442, 446 |
| src/mcp\_audit/gemini\_cli\_adapter.py   |      536 |      200 |     63% |98-100, 144-145, 194-195, 199-200, 350-353, 355-357, 361-366, 405, 423, 429, 448, 459, 484, 505, 518-522, 545-548, 560-622, 631-707, 732-737, 773-776, 841, 982, 1031-1059, 1118, 1249-1259, 1269-1350 |
| src/mcp\_audit/normalization.py          |       33 |        0 |    100% |           |
| src/mcp\_audit/pricing\_config.py        |      119 |       26 |     78% |18-25, 163, 175, 181, 207-212, 220, 303, 327-329, 332, 338-340, 344, 347, 354-358 |
| src/mcp\_audit/privacy.py                |      112 |        8 |     93% |255, 269, 355-362 |
| src/mcp\_audit/session\_manager.py       |      289 |       75 |     74% |29, 169, 175, 180-182, 206-209, 243, 249, 254-256, 284-290, 319-320, 329, 349-378, 395, 399-432, 465, 487-488, 563-618, 637, 644, 656-658, 665-666, 671, 684, 688-689, 712, 719, 724, 750-756, 786-788 |
| src/mcp\_audit/smells.py                 |       92 |       11 |     88% |    98-111 |
| src/mcp\_audit/storage.py                |      318 |       40 |     87% |381-383, 424-426, 480-481, 550, 558-559, 715-717, 758-759, 785, 795, 804, 806, 813-816, 931, 936-957 |
| src/mcp\_audit/token\_estimator.py       |      268 |       72 |     73% |35-37, 43-45, 121-122, 126-127, 132-133, 136, 139-140, 146-147, 163-167, 206, 225-230, 255-256, 262-263, 432-477, 565, 590, 602, 615, 629, 648, 657-658, 691-711 |
| src/mcp\_audit/zombie\_detector.py       |       46 |        5 |     89% |22-23, 81-83, 154 |
|                                **TOTAL** | **4827** | **1692** | **65%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/littlebearapps/mcp-audit/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/littlebearapps/mcp-audit/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Flittlebearapps%2Fmcp-audit%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.