# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                       |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------- | -------: | -------: | ------: | --------: |
| src/mcp\_audit/\_\_init\_\_.py             |       38 |       20 |     47% |12-14, 37-47, 50-56, 59-65, 68-70, 73-75, 78-80, 83-85, 95-103, 107-114 |
| src/mcp\_audit/base\_tracker.py            |      519 |       32 |     94% |173, 183-186, 554-574, 842, 916, 1178-1188, 1200-1205, 1302, 1316-1318, 1327-1332 |
| src/mcp\_audit/claude\_code\_adapter.py    |      377 |      187 |     50% |81, 136-138, 208, 215, 220-266, 277, 292-362, 428-429, 439-440, 448, 461, 481, 484-485, 494-576, 630, 705-708, 823-859, 896-930 |
| src/mcp\_audit/cli.py                      |      956 |      614 |     36% |76-95, 119-537, 608-619, 641, 675-677, 712-732, 760-781, 888, 985-1050, 1055-1257, 1262-1270, 1275-1279, 1284-1299, 1304-1358, 1363-1414, 1424-1435, 1440-1477, 1516, 1520, 1568-1572, 1585-1593, 1623-1627, 1639, 1641, 1643, 1697-1701, 1736-1752, 1762-1829, 1834-1970, 1975-2025, 2036-2044, 2058-2083 |
| src/mcp\_audit/codex\_cli\_adapter.py      |      488 |      260 |     47% |175, 202, 209, 213, 217, 230-232, 247-248, 282-283, 309-310, 322-325, 334-391, 395-477, 541-580, 584-621, 756, 831, 901-930, 954-989, 1069-1070, 1110-1236 |
| src/mcp\_audit/display/\_\_init\_\_.py     |       31 |        8 |     74% |75-81, 104-108 |
| src/mcp\_audit/display/ascii\_mode.py      |       53 |       26 |     51% |100-106, 121-125, 141-165 |
| src/mcp\_audit/display/base.py             |        8 |        0 |    100% |           |
| src/mcp\_audit/display/keyboard.py         |       70 |       52 |     26% |25-38, 45-58, 71-74, 79-99, 104-119, 133 |
| src/mcp\_audit/display/null\_display.py    |       13 |        0 |    100% |           |
| src/mcp\_audit/display/plain\_display.py   |       47 |        8 |     83% |69, 79-87, 93 |
| src/mcp\_audit/display/rich\_display.py    |      490 |      298 |     39% |75-84, 95-119, 123, 128-135, 151-156, 162, 184-185, 199-217, 219, 221, 226-227, 229, 231, 233-234, 237-239, 242, 247, 251-252, 257, 300, 313-318, 320-323, 381-382, 422-423, 449-450, 466, 470-478, 488, 497-499, 513, 524-538, 542-584, 593-625, 637-646, 657-774, 803-808, 811, 817-1000 |
| src/mcp\_audit/display/session\_browser.py |      577 |      577 |      0% |   10-1259 |
| src/mcp\_audit/display/snapshot.py         |       53 |        0 |    100% |           |
| src/mcp\_audit/display/theme\_detect.py    |       58 |        7 |     88% |50-51, 55-57, 130, 132 |
| src/mcp\_audit/display/themes.py           |      293 |       51 |     83% |117, 145, 153, 157, 202, 206, 210, 214, 218, 222, 226, 230, 234, 238, 242, 246, 250, 254, 258, 262, 266, 270, 291, 295, 299, 303, 308, 316, 329, 333, 337, 342, 346, 350, 354, 358, 379, 383, 387, 391, 396, 404, 408, 417, 421, 425, 430, 434, 438, 442, 446 |
| src/mcp\_audit/gemini\_cli\_adapter.py     |      542 |      204 |     62% |98-100, 144-145, 194-195, 199-200, 338, 356-359, 361-363, 367-372, 411, 429, 435, 454, 465, 490, 511, 524-528, 551-554, 566-628, 637-717, 742-747, 783-786, 871, 1012, 1061-1089, 1148, 1283-1293, 1303-1384 |
| src/mcp\_audit/normalization.py            |       33 |        0 |    100% |           |
| src/mcp\_audit/preferences.py              |       83 |        4 |     95% |21, 93, 121, 127 |
| src/mcp\_audit/pricing\_api.py             |      175 |       21 |     88% |95, 117, 120, 160-170, 252-254, 308, 372, 388, 396, 414-416 |
| src/mcp\_audit/pricing\_config.py          |      171 |       43 |     75% |24-31, 186, 198, 211-212, 228-231, 236, 242, 286-291, 295-299, 304-305, 382, 406-408, 411, 421-423, 427, 430, 437-441, 459, 464-466 |
| src/mcp\_audit/privacy.py                  |      112 |        8 |     93% |255, 269, 355-362 |
| src/mcp\_audit/schema\_analyzer.py         |      135 |       14 |     90% |184-189, 242, 303, 347, 377, 388, 394, 429-431 |
| src/mcp\_audit/session\_manager.py         |      289 |       75 |     74% |29, 169, 175, 180-182, 206-209, 243, 249, 254-256, 284-290, 319-320, 329, 349-378, 395, 399-432, 465, 487-488, 563-618, 637, 644, 656-658, 665-666, 671, 684, 688-689, 712, 719, 724, 750-756, 786-788 |
| src/mcp\_audit/smells.py                   |       92 |       11 |     88% |    98-111 |
| src/mcp\_audit/storage.py                  |      318 |       40 |     87% |381-383, 424-426, 480-481, 550, 558-559, 715-717, 758-759, 785, 795, 804, 806, 813-816, 931, 936-957 |
| src/mcp\_audit/token\_estimator.py         |      268 |       72 |     73% |35-37, 43-45, 121-122, 126-127, 132-133, 136, 139-140, 146-147, 163-167, 206, 225-230, 255-256, 262-263, 432-477, 565, 590, 602, 615, 629, 648, 657-658, 691-711 |
| src/mcp\_audit/zombie\_detector.py         |       46 |        5 |     89% |22-23, 81-83, 154 |
|                                  **TOTAL** | **6335** | **2637** | **58%** |           |


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