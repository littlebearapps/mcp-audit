# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/littlebearapps/mcp-audit/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                       |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------- | -------: | -------: | ------: | --------: |
| src/mcp\_audit/\_\_init\_\_.py             |       50 |        2 |     96% |     14-16 |
| src/mcp\_audit/base\_tracker.py            |      568 |       33 |     94% |173, 183-186, 575-595, 847, 970, 1044, 1306-1316, 1328-1333, 1430, 1444-1446, 1455-1460 |
| src/mcp\_audit/claude\_code\_adapter.py    |      377 |      187 |     50% |81, 136-138, 208, 215, 220-266, 277, 292-362, 428-429, 439-440, 448, 461, 481, 484-485, 494-576, 630, 705-708, 823-859, 896-930 |
| src/mcp\_audit/cli.py                      |     1383 |      817 |     41% |77-96, 120-673, 744-755, 777, 811-813, 848-868, 899-920, 1027, 1124-1189, 1194-1219, 1224-1279, 1284-1294, 1299-1356, 1361-1366, 1371-1573, 1578-1586, 1591-1595, 1600-1615, 1620-1674, 1679-1730, 1740-1751, 1756-1814, 1876, 1880, 1928, 1990-1994, 2006, 2008, 2010, 2082, 2084-2086, 2104-2106, 2169-2170, 2173, 2178, 2256-2264, 2271-2273, 2356, 2410, 2451-2452, 2484, 2494, 2499-2500, 2511-2512, 2514, 2516-2517, 2521-2523, 2559-2575, 2585-2652, 2657-2793, 2798-2848, 2859-2867, 2881-2906, 2924-3010 |
| src/mcp\_audit/codex\_cli\_adapter.py      |      488 |      260 |     47% |175, 202, 209, 213, 217, 230-232, 247-248, 282-283, 309-310, 322-325, 334-391, 395-477, 541-580, 584-621, 756, 831, 901-930, 954-989, 1069-1070, 1110-1236 |
| src/mcp\_audit/display/\_\_init\_\_.py     |       31 |        8 |     74% |75-81, 104-108 |
| src/mcp\_audit/display/ascii\_mode.py      |       53 |       26 |     51% |104-110, 125-129, 145-169 |
| src/mcp\_audit/display/base.py             |        8 |        0 |    100% |           |
| src/mcp\_audit/display/keyboard.py         |       70 |       52 |     26% |25-38, 45-58, 71-74, 79-99, 104-119, 133 |
| src/mcp\_audit/display/null\_display.py    |       13 |        0 |    100% |           |
| src/mcp\_audit/display/plain\_display.py   |       47 |        8 |     83% |69, 79-87, 93 |
| src/mcp\_audit/display/rich\_display.py    |      558 |      259 |     54% |109-118, 129-157, 161, 180-187, 212, 227, 237, 241, 251, 259, 303-304, 338, 367-368, 400, 402, 404, 414, 416-417, 420-422, 430, 434-435, 440, 483, 496-501, 503-506, 564-565, 605-606, 660-661, 680-682, 696, 707-721, 725-767, 779, 820-829, 840-959, 1018, 1020, 1025, 1031-1214 |
| src/mcp\_audit/display/session\_browser.py |     1045 |      702 |     33% |273-276, 294-299, 304-342, 346-395, 399-452, 464-493, 511-526, 530-572, 576-588, 592-599, 607-609, 614-622, 652-654, 709, 716, 721, 729, 741-743, 747, 754, 776-777, 823, 834, 860, 870, 902, 925-948, 952-1001, 1005-1038, 1042-1147, 1151-1158, 1162-1172, 1176-1192, 1196-1200, 1204-1216, 1220-1227, 1232-1241, 1245-1251, 1255-1263, 1267-1321, 1325-1338, 1342-1428, 1432-1463, 1467-1492, 1496-1505, 1514, 1522-1537, 1547, 1555-1654, 1664, 1672-1733, 1742, 1750-1813, 1844-1845, 1902, 1910-1977, 1981-2065, 2074, 2082-2195, 2199-2208 |
| src/mcp\_audit/display/snapshot.py         |       53 |        0 |    100% |           |
| src/mcp\_audit/display/theme\_detect.py    |       58 |        7 |     88% |50-51, 55-57, 130, 132 |
| src/mcp\_audit/display/themes.py           |      293 |       51 |     83% |117, 145, 153, 157, 202, 206, 210, 214, 218, 222, 226, 230, 234, 238, 242, 246, 250, 254, 258, 262, 266, 270, 291, 295, 299, 303, 308, 316, 329, 333, 337, 342, 346, 350, 354, 358, 379, 383, 387, 391, 396, 404, 408, 417, 421, 425, 430, 434, 438, 442, 446 |
| src/mcp\_audit/gemini\_cli\_adapter.py     |      542 |      204 |     62% |98-100, 144-145, 194-195, 199-200, 338, 356-359, 361-363, 367-372, 411, 429, 435, 454, 465, 490, 511, 524-528, 551-554, 566-628, 637-717, 742-747, 783-786, 871, 1012, 1061-1089, 1148, 1283-1293, 1303-1384 |
| src/mcp\_audit/normalization.py            |       33 |        0 |    100% |           |
| src/mcp\_audit/preferences.py              |       83 |        3 |     96% |93, 121, 127 |
| src/mcp\_audit/pricing\_api.py             |      175 |       21 |     88% |95, 117, 120, 160-170, 252-254, 308, 372, 388, 396, 414-416 |
| src/mcp\_audit/pricing\_config.py          |      171 |       43 |     75% |24-31, 186, 198, 211-212, 228-231, 236, 242, 286-291, 295-299, 304-305, 382, 406-408, 411, 421-423, 427, 430, 437-441, 459, 464-466 |
| src/mcp\_audit/privacy.py                  |      112 |        8 |     93% |255, 269, 355-362 |
| src/mcp\_audit/recommendations.py          |      152 |        4 |     97% |158, 215, 406, 410 |
| src/mcp\_audit/schema\_analyzer.py         |      135 |       14 |     90% |184-189, 242, 303, 347, 377, 388, 394, 429-431 |
| src/mcp\_audit/session\_manager.py         |      294 |       73 |     75% |29, 169, 175, 180-182, 206-209, 243, 249, 254-256, 284-290, 319-320, 329, 349-378, 395, 399-432, 466, 578-633, 652, 659, 671-673, 680-681, 686, 699, 703-704, 727, 734, 739, 765-771, 801-803 |
| src/mcp\_audit/smell\_aggregator.py        |      156 |       58 |     63% |159-177, 213-275, 289-307, 409, 414, 432, 456-457 |
| src/mcp\_audit/smells.py                   |      248 |       14 |     94% |160-173, 471, 633, 690 |
| src/mcp\_audit/storage.py                  |      356 |       63 |     82% |388-390, 431-433, 487-488, 557, 565-566, 598-600, 619-650, 658-659, 813-815, 856-857, 883, 893, 902, 904, 911-914, 1029, 1034-1055 |
| src/mcp\_audit/token\_estimator.py         |      268 |       72 |     73% |35-37, 43-45, 121-122, 126-127, 132-133, 136, 139-140, 146-147, 163-167, 206, 225-230, 255-256, 262-263, 432-477, 565, 590, 602, 615, 629, 648, 657-658, 691-711 |
| src/mcp\_audit/zombie\_detector.py         |       46 |        5 |     89% |22-23, 81-83, 154 |
| **TOTAL**                                  | **7866** | **2994** | **62%** |           |


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