# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                     |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------- | -------: | -------: | ------: | --------: |
| src/mcp\_audit/\_\_init\_\_.py           |       38 |       20 |     47% |12-14, 37-47, 50-56, 59-65, 68-70, 73-75, 78-80, 83-85, 95-103, 107-114 |
| src/mcp\_audit/base\_tracker.py          |      395 |       18 |     95% |167, 177-180, 359-379, 709, 973, 987-989, 998-1003 |
| src/mcp\_audit/claude\_code\_adapter.py  |      370 |      183 |     51% |81, 136-138, 199, 204-250, 261, 276-346, 412-413, 423-424, 432, 445, 465, 468-469, 478-556, 610, 685-688, 779-815, 850-884 |
| src/mcp\_audit/cli.py                    |      691 |      488 |     29% |76-95, 119-426, 497-508, 530, 564-566, 601-621, 649-670, 777, 862-927, 932-1083, 1088-1096, 1101-1105, 1110-1125, 1130-1184, 1189-1240, 1250-1317, 1322-1458, 1463-1513, 1524-1532, 1546-1565 |
| src/mcp\_audit/codex\_cli\_adapter.py    |      481 |      256 |     47% |185, 192, 196, 200, 213-215, 230-231, 265-266, 292-293, 305-308, 317-370, 374-456, 496-535, 539-576, 711, 786, 856-885, 909-944, 1022-1023, 1063-1189 |
| src/mcp\_audit/display/\_\_init\_\_.py   |       26 |        4 |     85% |     75-81 |
| src/mcp\_audit/display/ascii\_mode.py    |       22 |        0 |    100% |           |
| src/mcp\_audit/display/base.py           |        8 |        0 |    100% |           |
| src/mcp\_audit/display/null\_display.py  |       12 |        0 |    100% |           |
| src/mcp\_audit/display/plain\_display.py |       45 |        8 |     82% |67, 77-85, 91 |
| src/mcp\_audit/display/rich\_display.py  |      309 |      150 |     51% |70-77, 81-94, 98, 102-106, 131-132, 145, 147, 152-153, 155, 157, 159-160, 163, 202, 215-220, 222-225, 288-289, 315-316, 332, 336-344, 354, 363-365, 379, 390-404, 411-420, 455-460, 463, 469-604 |
| src/mcp\_audit/display/snapshot.py       |       41 |        0 |    100% |           |
| src/mcp\_audit/display/theme\_detect.py  |       58 |        7 |     88% |50-51, 55-57, 130, 132 |
| src/mcp\_audit/display/themes.py         |      293 |       51 |     83% |117, 145, 153, 157, 202, 206, 210, 214, 218, 222, 226, 230, 234, 238, 242, 246, 250, 254, 258, 262, 266, 270, 291, 295, 299, 303, 308, 316, 329, 333, 337, 342, 346, 350, 354, 358, 379, 383, 387, 391, 396, 404, 408, 417, 421, 425, 430, 434, 438, 442, 446 |
| src/mcp\_audit/gemini\_cli\_adapter.py   |      535 |      200 |     63% |98-100, 144-145, 194-195, 199-200, 334-337, 339-341, 345-350, 389, 407, 413, 432, 443, 468, 489, 502-506, 529-532, 544-606, 615-691, 716-721, 757-760, 819, 960, 1009-1037, 1096, 1227-1237, 1247-1328 |
| src/mcp\_audit/normalization.py          |       33 |        0 |    100% |           |
| src/mcp\_audit/pricing\_config.py        |      119 |       26 |     78% |18-25, 163, 175, 181, 207-212, 220, 303, 327-329, 332, 338-340, 344, 347, 354-358 |
| src/mcp\_audit/privacy.py                |      112 |        8 |     93% |255, 269, 355-362 |
| src/mcp\_audit/session\_manager.py       |      289 |       75 |     74% |29, 169, 175, 180-182, 206-209, 243, 249, 254-256, 284-290, 319-320, 329, 349-378, 395, 399-432, 465, 487-488, 563-618, 637, 644, 656-658, 665-666, 671, 684, 688-689, 712, 719, 724, 750-756, 786-788 |
| src/mcp\_audit/storage.py                |      291 |       24 |     92% |381-383, 424-426, 480-481, 550, 558-559, 715-717, 758-759, 785, 795, 804, 806, 813-816 |
| src/mcp\_audit/token\_estimator.py       |      268 |       72 |     73% |35-37, 43-45, 121-122, 126-127, 132-133, 136, 139-140, 146-147, 163-167, 206, 225-230, 255-256, 262-263, 432-477, 565, 590, 602, 615, 629, 648, 657-658, 691-711 |
|                                **TOTAL** | **4436** | **1590** | **64%** |           |


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