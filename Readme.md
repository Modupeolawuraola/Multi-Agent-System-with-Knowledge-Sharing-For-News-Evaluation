## Project: Group 6: Improved Multi-Agent Knowledge Sharing Systems
## Title: Improved  Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs for News Bias Detection and Summarization

Proposed by Group Initiative and Idea 

## Project Objectives:
The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased summaries of the topic. This project will explore the effects of shared memory on a multi-agent system and look at utilizing dynamic knowledge graphs to improve the overall efficiency of the system and accuracy of predictions and quality of  summarizations. Specifically, this project will focus on:

Developing several agents based on customizing open-source LLMs for specific tasks, such as bias detection, summarization, knowledge graph maintenance, data collection, and chat functionality.
Evaluating the effect of shared memory on a multi agent system, specifically focusing on the effect of deploying dynamic knowledge graphs compared to other methods. Evaluation metrics will focus on comparing compute resources, reducing redundancy of collected information, accuracy of bias classification, and quality of news summarization.


## System Architecture
 
![multiagent-diagram_v3](https://github.com/user-attachments/assets/bb406a4a-0e7c-464a-8c91-30fd90d342ea)

![multiagent-diagram_updated](https://github.com/user-attachments/assets/249d9339-371d-4dbf-b40c-fb89292c0d3c){
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "type": "text",
      "version": 1162,
      "versionNonce": 2087119036,
      "isDeleted": false,
      "id": "x2sbMHVFmpBTxerdxhbcM",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -3781.4892866258865,
      "y": 110.59914868773501,
      "strokeColor": "#000000",
      "backgroundColor": "white",
      "width": 139.62066398755283,
      "height": 61.23713332787406,
      "seed": 606626748,
      "groupIds": [
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "fontSize": 48.989706662299234,
      "fontFamily": 1,
      "text": "Users",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Users",
      "index": "b3E",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "ellipse",
      "version": 2091,
      "versionNonce": 495087932,
      "isDeleted": false,
      "id": "8m5VL5zR0N5EQoubnry7M",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3682.425199703415,
      "y": -54.15285106733336,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 48.37817705244955,
      "height": 42.33090492089351,
      "seed": 1700564028,
      "groupIds": [
        "0ywMkQyF7wVTgfkpWLS7p",
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "index": "b3F",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "ellipse",
      "version": 2135,
      "versionNonce": 320399804,
      "isDeleted": false,
      "id": "KfUaMlh13ROsjGguKdxOU",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3788.2029761009585,
      "y": -52.72463508310983,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 48.37817705244955,
      "height": 42.33090492089351,
      "seed": 787981500,
      "groupIds": [
        "0ywMkQyF7wVTgfkpWLS7p",
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "index": "b3G",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "line",
      "version": 2318,
      "versionNonce": 1884049980,
      "isDeleted": false,
      "id": "tVA0NngXR2icd6b_z8cou",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3762.6013962888073,
      "y": 91.62607262153654,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 102.40318905981651,
      "height": 91.18709900210453,
      "seed": 916172092,
      "groupIds": [
        "0ywMkQyF7wVTgfkpWLS7p",
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          11.469157174699431,
          -60.42518608573196
        ],
        [
          49.153530748711994,
          -91.18709900210453
        ],
        [
          86.83790432272441,
          -67.01702456781157
        ],
        [
          102.40318905981651,
          -6.274389865293504
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3H",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 2029,
      "versionNonce": 335456956,
      "isDeleted": false,
      "id": "oz6u6FgzuO5fJOXfGSN3D",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3736.9157938791463,
      "y": -46.952363084550655,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 52.43043279862601,
      "height": 45.876628698797994,
      "seed": 766158268,
      "groupIds": [
        "0ywMkQyF7wVTgfkpWLS7p",
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "index": "b3I",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "line",
      "version": 1431,
      "versionNonce": 819065660,
      "isDeleted": false,
      "id": "OzrUmJvKKQJt6dl46Nb27",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3691.1956276524143,
      "y": 9.15419249580043,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 81.90421806756979,
      "height": 91.65472021847101,
      "seed": 1229360700,
      "groupIds": [
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.675652796171395,
          -13.650703011261744
        ],
        [
          23.401205162162757,
          -20.476054516892713
        ],
        [
          41.927159248875014,
          -21.45110473198273
        ],
        [
          54.60281204504653,
          -18.525954086712257
        ],
        [
          63.37826398085756,
          -8.775451935811223
        ],
        [
          69.22856527139825,
          3.900200860360276
        ],
        [
          75.078866561939,
          19.501004301802265
        ],
        [
          79.95411763738957,
          35.10180774324425
        ],
        [
          81.90421806756979,
          47.77746053941573
        ],
        [
          79.95411763738957,
          60.45311333558727
        ],
        [
          72.15371591666863,
          66.30341462612779
        ],
        [
          61.4281635506773,
          69.22856527139827
        ],
        [
          45.82736010923543,
          70.20361548648829
        ],
        [
          36.076857958334266,
          68.2535150563082
        ],
        [
          35.10180774324414,
          54.60281204504674
        ],
        [
          31.201606882883656,
          45.827360109235265
        ],
        [
          24.3762553772529,
          32.17665709797377
        ],
        [
          14.625753226351645,
          13.650703011261516
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3J",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "line",
      "version": 1726,
      "versionNonce": 1428695996,
      "isDeleted": false,
      "id": "Vhs0F5wAL_U9DkqKPMB-7",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3735.0874322570753,
      "y": 9.125102644593824,
      "strokeColor": "#000000",
      "backgroundColor": "#ced4da",
      "width": 78.97906742229952,
      "height": 95.55492107883168,
      "seed": 1246848700,
      "groupIds": [
        "Wh5KAaU7a-3Jarw9HRWpL",
        "_6GqbOQoc3Ah1uppIh-Uu"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123594191,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          -9.75050215090118,
          -10.725552365991254
        ],
        [
          -20.47605451689251,
          -17.550903871622246
        ],
        [
          -39.00200860360485,
          -18.525954086712222
        ],
        [
          -51.67766139977634,
          -15.600803441441757
        ],
        [
          -60.4531133355873,
          -5.850301290540744
        ],
        [
          -66.30341462612813,
          6.825351505630751
        ],
        [
          -72.15371591666882,
          22.426154947072725
        ],
        [
          -77.02896699211932,
          38.02695838851473
        ],
        [
          -78.97906742229952,
          50.70261118468621
        ],
        [
          -77.02896699211932,
          63.37826398085773
        ],
        [
          -69.22856527139847,
          69.22856527139821
        ],
        [
          -59.47806312049715,
          74.10381634684894
        ],
        [
          -43.87725967905535,
          77.02896699211922
        ],
        [
          -27.301406022523263,
          77.02896699211946
        ],
        [
          -25.351305592343017,
          59.4780631204972
        ],
        [
          -23.401205162162803,
          50.702611184686006
        ],
        [
          -20.47605451689251,
          36.07685795833445
        ],
        [
          -11.700602581081428,
          16.575853656531987
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3K",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "text",
      "version": 1365,
      "versionNonce": 1675297980,
      "isDeleted": false,
      "id": "9shkrGyF1Na3EZVlTpPIv",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -1807.9899294523907,
      "y": -60.55190224606258,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 164.83592224121094,
      "height": 35,
      "seed": 999722172,
      "groupIds": [
        "POcCd4kOniQPQpVqBw99F"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123798599,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "KG Updater",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "KG Updater",
      "index": "b3V",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1601,
      "versionNonce": 679186692,
      "isDeleted": false,
      "id": "mhfv_RV5tOnxhgLk97BMm",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -1778.3317710891865,
      "y": -75.72403062467322,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 522032444,
      "groupIds": [
        "s7_eC5P7Urzp-kwGRxynI",
        "POcCd4kOniQPQpVqBw99F"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123795857,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3W",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1339,
      "versionNonce": 902954556,
      "isDeleted": false,
      "id": "0mDVrEqpobVnBChaQxRL7",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -1751.227557617292,
      "y": -220.86833311584917,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 2108657084,
      "groupIds": [
        "s7_eC5P7Urzp-kwGRxynI",
        "POcCd4kOniQPQpVqBw99F"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [
        {
          "id": "M5baw5WuP0xY3pvHfdBu0",
          "type": "arrow"
        }
      ],
      "updated": 1741123801707,
      "link": null,
      "locked": false,
      "index": "b3X",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1529,
      "versionNonce": 1944359612,
      "isDeleted": false,
      "id": "1UGeb68yCclkG68BEsGzj",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -1929.5346873456383,
      "y": 425.4038867739305,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 178.86392211914062,
      "height": 35,
      "seed": 1565179908,
      "groupIds": [
        "48hnc0tKreSt2K3rW6RzK"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [
        {
          "id": "3OE4rZLPqe7dPrSpDJbhR",
          "type": "arrow"
        }
      ],
      "updated": 1741123903681,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "KG Retriever",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "KG Retriever",
      "index": "b3Y",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1793,
      "versionNonce": 1857492484,
      "isDeleted": false,
      "id": "Zot2rKOU48NC-urfnojuh",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -1897.5027858859607,
      "y": 407.41211880558626,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 293347204,
      "groupIds": [
        "7fWhysQ1MZgNl4xVdGgU9",
        "48hnc0tKreSt2K3rW6RzK"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123809440,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3Z",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1530,
      "versionNonce": 518894980,
      "isDeleted": false,
      "id": "jr-_HESRaSfoFjxDPf9-t",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -1870.3985724140662,
      "y": 262.2678163144104,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 123047684,
      "groupIds": [
        "7fWhysQ1MZgNl4xVdGgU9",
        "48hnc0tKreSt2K3rW6RzK"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123809440,
      "link": null,
      "locked": false,
      "index": "b3a",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1086,
      "versionNonce": 1942095876,
      "isDeleted": false,
      "id": "ywMtwlfk10-RKA2sfPe_5",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -3204.415146715144,
      "y": 98.73212969565563,
      "strokeColor": "#000000",
      "backgroundColor": "#ffc9c9",
      "width": 111.91595458984375,
      "height": 35,
      "seed": 205928508,
      "groupIds": [
        "gxGgDTzyv6NaIRZntxMf9"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [
        {
          "id": "ibA000rY9b4XmcfFfosIZ",
          "type": "arrow"
        },
        {
          "id": "rd8a1UHauJ88fSfLGj30N",
          "type": "arrow"
        }
      ],
      "updated": 1741123985213,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "Chatbot",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Chatbot",
      "index": "b3b",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1361,
      "versionNonce": 234015548,
      "isDeleted": false,
      "id": "6BLaeWWGkOa4BeN1ncPJj",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3204.8156578387707,
      "y": 81.40920646720161,
      "strokeColor": "#000000",
      "backgroundColor": "#ffc9c9",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 600559804,
      "groupIds": [
        "3BVzPuFe3BH8PkQPrcQ5v",
        "gxGgDTzyv6NaIRZntxMf9"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123321644,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3c",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1098,
      "versionNonce": 400529028,
      "isDeleted": false,
      "id": "eW8ZPYdq7NRP5O6EGUpmo",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -3177.711444366875,
      "y": -63.73509602397428,
      "strokeColor": "#000000",
      "backgroundColor": "#ffc9c9",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 1477073212,
      "groupIds": [
        "3BVzPuFe3BH8PkQPrcQ5v",
        "gxGgDTzyv6NaIRZntxMf9"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123321644,
      "link": null,
      "locked": false,
      "index": "b3d",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1379,
      "versionNonce": 1687519236,
      "isDeleted": false,
      "id": "4QAoqOaa1Xe35YxEFGnUe",
      "fillStyle": "cross-hatch",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -2653.195546659024,
      "y": -361.17848085593937,
      "strokeColor": "#000000",
      "backgroundColor": "#ffec99",
      "width": 200.61993408203125,
      "height": 35,
      "seed": 782390460,
      "groupIds": [
        "d8cK37lNsIrEMYE58QaGM"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [
        {
          "id": "6U_w1PG5y70r_UecTcLZN",
          "type": "arrow"
        }
      ],
      "updated": 1741123720518,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "News Collector",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "News Collector",
      "index": "b3e",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1413,
      "versionNonce": 837367484,
      "isDeleted": false,
      "id": "qQth4hj-ybmDNehsnjsCz",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2608.442480538689,
      "y": -372.53425983635327,
      "strokeColor": "#000000",
      "backgroundColor": "#ffec99",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 1299209532,
      "groupIds": [
        "-6Z9K0G4zx7RmSc9yySlz",
        "d8cK37lNsIrEMYE58QaGM"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123674807,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3f",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1148,
      "versionNonce": 1233846076,
      "isDeleted": false,
      "id": "0VPYywNJiEmnrbyn1JwMT",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2581.338267066795,
      "y": -517.6785623275292,
      "strokeColor": "#000000",
      "backgroundColor": "#ffec99",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 1718179260,
      "groupIds": [
        "-6Z9K0G4zx7RmSc9yySlz",
        "d8cK37lNsIrEMYE58QaGM"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123674807,
      "link": null,
      "locked": false,
      "index": "b3g",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1397,
      "versionNonce": 2055917116,
      "isDeleted": false,
      "id": "pJOegc89AakbwbQ7SRoln",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -2228.382784425972,
      "y": -392.124027170035,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 200.08792114257812,
      "height": 35,
      "seed": 2019852036,
      "groupIds": [
        "5FrLVPaWPQ2JruQWr5LQp"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123573474,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "Bias Detector",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Bias Detector",
      "index": "b3h",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1591,
      "versionNonce": 1225631420,
      "isDeleted": false,
      "id": "OKLqFEjT79ZgaeQ86ZOk7",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2182.396945647801,
      "y": -405.9191222606365,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 1090911876,
      "groupIds": [
        "CdTN7X94UXU_yGbVIIYxu",
        "5FrLVPaWPQ2JruQWr5LQp"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123573474,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3i",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1328,
      "versionNonce": 1654746940,
      "isDeleted": false,
      "id": "_FjAvbvd7Ab6VVzNPtQoj",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2155.2927321759066,
      "y": -551.0634247518125,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 139169284,
      "groupIds": [
        "CdTN7X94UXU_yGbVIIYxu",
        "5FrLVPaWPQ2JruQWr5LQp"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123573474,
      "link": null,
      "locked": false,
      "index": "b3j",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1415,
      "versionNonce": 462354620,
      "isDeleted": false,
      "id": "R5U8ovzgIrvAZaBpMJ28A",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -2708.2915727829495,
      "y": 608.5786748180822,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 148.59593200683594,
      "height": 35,
      "seed": 2076068740,
      "groupIds": [
        "PSYTg7M0vXka9su_9ycHn"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123915244,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "Summarizer",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Summarizer",
      "index": "b3k",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 1675,
      "versionNonce": 1026064700,
      "isDeleted": false,
      "id": "XlUJgIgk4SNy9W1eVmAG7",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2690.3185254637087,
      "y": 593.4983486586718,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 1081228036,
      "groupIds": [
        "LfIWQGReL2pj4OdL114sE",
        "PSYTg7M0vXka9su_9ycHn"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123915244,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3l",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1412,
      "versionNonce": 1937570236,
      "isDeleted": false,
      "id": "fmQFkr3xnUOz7rdd65prY",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2663.214311991815,
      "y": 448.354046167496,
      "strokeColor": "#000000",
      "backgroundColor": "#a5d8ff",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 939276932,
      "groupIds": [
        "LfIWQGReL2pj4OdL114sE",
        "PSYTg7M0vXka9su_9ycHn"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123915244,
      "link": null,
      "locked": false,
      "index": "b3m",
      "frameId": null,
      "roundness": null
    },
    {
      "type": "text",
      "version": 1804,
      "versionNonce": 808818108,
      "isDeleted": false,
      "id": "3UUPtgLxK425SgIua6SJX",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "x": -2409.3219866624568,
      "y": 496.723687257693,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 180.8519287109375,
      "height": 35,
      "seed": 955459588,
      "groupIds": [
        "KzecAQ_GRS4wxY4bSY2-g"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [],
      "updated": 1741123847267,
      "link": null,
      "locked": false,
      "fontSize": 28,
      "fontFamily": 1,
      "text": "Fact Checker",
      "baseline": 18,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Fact Checker",
      "index": "b3n",
      "frameId": null,
      "roundness": null,
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "type": "line",
      "version": 2068,
      "versionNonce": 826507908,
      "isDeleted": false,
      "id": "viw7X34jXizEkdsVyi_c5",
      "fillStyle": "cross-hatch",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2372.0442441056016,
      "y": 479.5974830703831,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 107.22842033072612,
      "height": 95.48382887593164,
      "seed": 735545220,
      "groupIds": [
        "2nTJi1F5K8Rc2vU_0RYAC",
        "KzecAQ_GRS4wxY4bSY2-g"
      ],
      "strokeSharpness": "round",
      "boundElements": [],
      "updated": 1741123848359,
      "link": null,
      "locked": false,
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "startArrowhead": null,
      "endArrowhead": null,
      "points": [
        [
          0,
          0
        ],
        [
          12.009583077041317,
          -63.27241672501495
        ],
        [
          51.46964175874854,
          -95.48382887593164
        ],
        [
          90.92970044045576,
          -70.17486218592558
        ],
        [
          107.22842033072612,
          -6.570038686993841
        ],
        [
          0,
          0
        ]
      ],
      "index": "b3o",
      "frameId": null,
      "roundness": {
        "type": 2
      }
    },
    {
      "type": "ellipse",
      "version": 1809,
      "versionNonce": 433171460,
      "isDeleted": false,
      "id": "7ma9Xs-Qz1cyqBAs6L0PF",
      "fillStyle": "cross-hatch",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "x": -2344.940030633706,
      "y": 334.45318057920724,
      "strokeColor": "#000000",
      "backgroundColor": "#b2f2bb",
      "width": 54.90095120933183,
      "height": 48.038332308165515,
      "seed": 302249732,
      "groupIds": [
        "2nTJi1F5K8Rc2vU_0RYAC",
        "KzecAQ_GRS4wxY4bSY2-g"
      ],
      "strokeSharpness": "sharp",
      "boundElements": [
        {
          "id": "oLkBZN1jAGEumd28Kam19",
          "type": "arrow"
        },
        {
          "id": "SQgH0ZAR4-H0UGVNU7gko",
          "type": "arrow"
        }
      ],
      "updated": 1741123887337,
      "link": null,
      "locked": false,
      "index": "b3p",
      "frameId": null,
      "roundness": null
    },
    {
      "id": "2ZMvMtGrqS75pZNiJIO8Y",
      "type": "line",
      "x": -2497.048567274931,
      "y": -82.62122779358998,
      "width": 470.70238234565517,
      "height": 346.97990102195354,
      "angle": 0,
      "strokeColor": "#846358",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "0lELnOzHB91sgnuy4QbzP"
      ],
      "frameId": null,
      "index": "b3r",
      "roundness": {
        "type": 2
      },
      "seed": 124034492,
      "version": 6040,
      "versionNonce": 273615164,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741123225269,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          3.5761272650639557,
          204.14758359427924
        ],
        [
          8.948866961773064,
          226.37391533049072
        ],
        [
          86.54455594403643,
          253.56164141240524
        ],
        [
          200.64731089584149,
          266.4269094766324
        ],
        [
          337.16444275300466,
          259.17738824098336
        ],
        [
          428.55149049184433,
          228.93229379788667
        ],
        [
          468.540643960537,
          196.24644562671912
        ],
        [
          470.70238234565517,
          180.77787464517783
        ],
        [
          462.39198314223967,
          2.9116752203046055
        ],
        [
          459.50655696858274,
          -22.523862488378796
        ],
        [
          406.76382763386044,
          -54.34617161970275
        ],
        [
          314.11114850745975,
          -80.55299154532119
        ],
        [
          169.11890033155592,
          -76.97743143507635
        ],
        [
          65.26997048427677,
          -48.65862827218115
        ],
        [
          2.5045603280488837,
          -8.804922361191249
        ],
        [
          0,
          0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": null
    },
    {
      "id": "IUkrUMXoFweyqpaD93ZHZ",
      "type": "line",
      "x": -2487.982775381088,
      "y": -87.21827422279927,
      "width": 446.6552414847418,
      "height": 52.067609228459254,
      "angle": 0,
      "strokeColor": "#846358",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "0lELnOzHB91sgnuy4QbzP"
      ],
      "frameId": null,
      "index": "b3s",
      "roundness": {
        "type": 2
      },
      "seed": 1224836668,
      "version": 1158,
      "versionNonce": 653146244,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741123225269,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          105.67313479477782,
          34.25259798656911
        ],
        [
          183.6611093864054,
          44.544752359080135
        ],
        [
          303.6731520024274,
          44.67478893748836
        ],
        [
          383.9392708273368,
          22.46261487758126
        ],
        [
          446.6552414847418,
          -7.392820290970898
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": null
    },
    {
      "id": "oJUtCGdnB5N_3l1zt00OY",
      "type": "text",
      "x": -2431.4343165962255,
      "y": 38.207581848581256,
      "width": 320.65185546875,
      "height": 90,
      "angle": 0,
      "strokeColor": "#846358",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "0lELnOzHB91sgnuy4QbzP"
      ],
      "frameId": null,
      "index": "b3t",
      "roundness": null,
      "seed": 132996796,
      "version": 247,
      "versionNonce": 814907836,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741123225269,
      "link": null,
      "locked": false,
      "text": "Dynamic Knowledge\nGraph",
      "fontSize": 36,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Dynamic Knowledge\nGraph",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "A6yvsb1Fka_o8nElKA1VD",
      "type": "ellipse",
      "x": -2919.857642005775,
      "y": -84.28692210899294,
      "width": 219.8205551889505,
      "height": 219.8205551889505,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b3x",
      "roundness": {
        "type": 2
      },
      "seed": 788338564,
      "version": 159,
      "versionNonce": 1612902660,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "JhdG2sLjHCxFa3Kp7tCN3"
        },
        {
          "id": "sAlIbfcZt3jB1Ys8Qut5E",
          "type": "arrow"
        },
        {
          "id": "KPPkGT4CC_-JVLU8MQqnh",
          "type": "arrow"
        },
        {
          "id": "rYr-tEVRcXGqiLcmm4gUu",
          "type": "arrow"
        },
        {
          "id": "6U_w1PG5y70r_UecTcLZN",
          "type": "arrow"
        }
      ],
      "updated": 1741123720517,
      "link": null,
      "locked": false
    },
    {
      "id": "JhdG2sLjHCxFa3Kp7tCN3",
      "type": "text",
      "x": -2863.8556313148824,
      "y": -12.39494712366701,
      "width": 107.37992858886719,
      "height": 75.60000000000001,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "cross-hatch",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b3y",
      "roundness": null,
      "seed": 1600446212,
      "version": 56,
      "versionNonce": 1834396092,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123392058,
      "link": null,
      "locked": false,
      "text": "KG\nDecision",
      "fontSize": 28,
      "fontFamily": 6,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "A6yvsb1Fka_o8nElKA1VD",
      "originalText": "KG Decision",
      "autoResize": true,
      "lineHeight": 1.35
    },
    {
      "id": "X_eGKVjiyOz4ew_Dgwe9J",
      "type": "rectangle",
      "x": -3113.799683314805,
      "y": -392.66341587390656,
      "width": 78.23363791149039,
      "height": 40.389639370895566,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b40",
      "roundness": {
        "type": 3
      },
      "seed": 1732820100,
      "version": 193,
      "versionNonce": 891961660,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741124049758,
      "link": null,
      "locked": false
    },
    {
      "id": "tZTjAnD8FPDAtN0TuLEOL",
      "type": "rectangle",
      "x": -3113.799683314805,
      "y": -460.40495235195635,
      "width": 78.23363791149039,
      "height": 47.800000000000004,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffec99",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b43",
      "roundness": {
        "type": 3
      },
      "seed": 2126880388,
      "version": 226,
      "versionNonce": 964454916,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741124064258,
      "link": null,
      "locked": false
    },
    {
      "id": "GHdc97UITg7aCMoU21ETm",
      "type": "rectangle",
      "x": -3113.799683314805,
      "y": -257.18034291780697,
      "width": 78.23363791149039,
      "height": 40.389639370895566,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b44",
      "roundness": {
        "type": 3
      },
      "seed": 974142596,
      "version": 220,
      "versionNonce": 1299833476,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741124035740,
      "link": null,
      "locked": false
    },
    {
      "id": "-0Unf7M-2yFEpVHPVpCL-",
      "type": "rectangle",
      "x": -3113.799683314805,
      "y": -324.92187939585676,
      "width": 78.23363791149039,
      "height": 40.389639370895566,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b45",
      "roundness": {
        "type": 3
      },
      "seed": 383748,
      "version": 238,
      "versionNonce": 1659359236,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741124055322,
      "link": null,
      "locked": false
    },
    {
      "id": "rQMNtpxo9kfgJZGqZb0jB",
      "type": "line",
      "x": -3596.772911731288,
      "y": 60.694206613257165,
      "width": 374.6960363469593,
      "height": 0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b47",
      "roundness": {
        "type": 2
      },
      "seed": 1117265284,
      "version": 74,
      "versionNonce": 1180703492,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123602307,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          374.6960363469593,
          0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": null
    },
    {
      "id": "sAlIbfcZt3jB1Ys8Qut5E",
      "type": "arrow",
      "x": -3083.0480454423,
      "y": 23.910274041221555,
      "width": 154.0826607914105,
      "height": 2.629264977118055,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b48",
      "roundness": {
        "type": 2
      },
      "seed": 86907524,
      "version": 68,
      "versionNonce": 1128459524,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123671455,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          154.0826607914105,
          2.629264977118055
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "A6yvsb1Fka_o8nElKA1VD",
        "focus": -0.026363869281090992,
        "gap": 9.111268917143095
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "KPPkGT4CC_-JVLU8MQqnh",
      "type": "arrow",
      "x": -2690.733356037888,
      "y": 19.824602483641,
      "width": 190.3768283186896,
      "height": 3.4025782056824028,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b49",
      "roundness": {
        "type": 2
      },
      "seed": 1812543876,
      "version": 126,
      "versionNonce": 1355404860,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123649154,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          190.3768283186896,
          3.4025782056824028
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "A6yvsb1Fka_o8nElKA1VD",
        "focus": -0.07087794629214968,
        "gap": 9.444677597306468
      },
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "rYr-tEVRcXGqiLcmm4gUu",
      "type": "arrow",
      "x": -2505.988825733907,
      "y": 49.94515273621528,
      "width": 189.62929219774378,
      "height": 1.7270662104599523,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4A",
      "roundness": {
        "type": 2
      },
      "seed": 1662956732,
      "version": 119,
      "versionNonce": 2012513796,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123647028,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -189.62929219774378,
          -1.7270662104599523
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "A6yvsb1Fka_o8nElKA1VD",
        "focus": 0.19433067489713907,
        "gap": 6.630266729749223
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "tYy_dwpVMwK2SHB7CYV-S",
      "type": "arrow",
      "x": -3081.082540986366,
      "y": 51.28556233239351,
      "width": 154.0826607914105,
      "height": 2.629264977118055,
      "angle": 3.1251933150777162,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4B",
      "roundness": {
        "type": 2
      },
      "seed": 2146740868,
      "version": 235,
      "versionNonce": 1854353668,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741123667890,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          79.85103512615478,
          1.8946174099819473
        ],
        [
          154.0826607914105,
          2.629264977118055
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "6U_w1PG5y70r_UecTcLZN",
      "type": "arrow",
      "x": -2771.1192661471364,
      "y": -80.61589735303437,
      "width": 134.4276162320716,
      "height": 231.24643244830554,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4C",
      "roundness": {
        "type": 2
      },
      "seed": 1575334404,
      "version": 110,
      "versionNonce": 1538926852,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123738570,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.40561619247774,
          -131.72101993209685
        ],
        [
          134.4276162320716,
          -231.24643244830554
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "A6yvsb1Fka_o8nElKA1VD",
        "focus": 0.043439745393230575,
        "gap": 3.2020562091280733
      },
      "endBinding": {
        "elementId": "4QAoqOaa1Xe35YxEFGnUe",
        "focus": 0.4600153645570973,
        "gap": 14.316151054599459
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "p-CLrjsOGGbT74rW1TxmX",
      "type": "arrow",
      "x": -2497.134389266851,
      "y": -433.45294643924626,
      "width": 295.47009608055987,
      "height": 48.61562496906731,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4D",
      "roundness": {
        "type": 2
      },
      "seed": 1257262852,
      "version": 127,
      "versionNonce": 366812932,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123735224,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          154.70131137426233,
          -48.61562496906731
        ],
        [
          295.47009608055987,
          -34.231998917774035
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "M5baw5WuP0xY3pvHfdBu0",
      "type": "arrow",
      "x": -2069.4792853170584,
      "y": -465.6614424089462,
      "width": 285.13347592541913,
      "height": 279.56562067975665,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4E",
      "roundness": {
        "type": 2
      },
      "seed": 1075210372,
      "version": 238,
      "versionNonce": 550514308,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123805704,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          188.71420487727664,
          82.77029256398487
        ],
        [
          285.13347592541913,
          279.56562067975665
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "0mDVrEqpobVnBChaQxRL7",
        "focus": -1.6787266276595976,
        "gap": 14
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "60NTr8wSd39LZw0k3GnmL",
      "type": "arrow",
      "x": -1801.504026886643,
      "y": -109.50089945515299,
      "width": 214.64242276710706,
      "height": 47.676513556225814,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4F",
      "roundness": {
        "type": 2
      },
      "seed": 1752019076,
      "version": 292,
      "versionNonce": 1261169724,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123798599,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -214.64242276710706,
          47.676513556225814
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "oLkBZN1jAGEumd28Kam19",
      "type": "arrow",
      "x": -2323.6286778846734,
      "y": 319.9732435970145,
      "width": 6.689159427080085,
      "height": 130.63838141210726,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4G",
      "roundness": {
        "type": 2
      },
      "seed": 1825865788,
      "version": 74,
      "versionNonce": 1602513852,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123859106,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          6.689159427080085,
          -130.63838141210726
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "7ma9Xs-Qz1cyqBAs6L0PF",
        "focus": -0.28278658997501754,
        "gap": 14.889471708147283
      },
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "SQgH0ZAR4-H0UGVNU7gko",
      "type": "arrow",
      "x": -2283.944820705522,
      "y": 192.29922956106998,
      "width": 8.570888283253225,
      "height": 129.9295109525899,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4J",
      "roundness": {
        "type": 2
      },
      "seed": 955419268,
      "version": 56,
      "versionNonce": 544726148,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123887337,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -8.570888283253225,
          129.9295109525899
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "7ma9Xs-Qz1cyqBAs6L0PF",
        "focus": 0.7777880892947254,
        "gap": 14
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "N-nZXJ5SnaROvoEVWw31L",
      "type": "arrow",
      "x": -2085.963745639285,
      "y": 168.3007423679619,
      "width": 184.13876827493823,
      "height": 157.24035647471464,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4K",
      "roundness": {
        "type": 2
      },
      "seed": 1745976068,
      "version": 90,
      "versionNonce": 772097156,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123894778,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          184.13876827493823,
          157.24035647471464
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "3OE4rZLPqe7dPrSpDJbhR",
      "type": "arrow",
      "x": -1927.705193413628,
      "y": 475.7056392760287,
      "width": 627.3116910112544,
      "height": 115.95831862319733,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4L",
      "roundness": {
        "type": 2
      },
      "seed": 1634866180,
      "version": 334,
      "versionNonce": 644857220,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123925118,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -327.1497999930152,
          115.95831862319733
        ],
        [
          -627.3116910112544,
          77.71797947069945
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "1UGeb68yCclkG68BEsGzj",
        "focus": -0.03559081281064829,
        "gap": 15.301752502098225
      },
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "ibA000rY9b4XmcfFfosIZ",
      "type": "arrow",
      "x": -2693.4528408916835,
      "y": 512.9922254466317,
      "width": 398.19186994150095,
      "height": 360.95683798613595,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4M",
      "roundness": {
        "type": 2
      },
      "seed": 941976836,
      "version": 325,
      "versionNonce": 678463364,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1741123977369,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -258.8923803694747,
          -163.37530808799033
        ],
        [
          -398.19186994150095,
          -360.95683798613595
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "ywMtwlfk10-RKA2sfPe_5",
        "focus": -0.46225842464246947,
        "gap": 14
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "rd8a1UHauJ88fSfLGj30N",
      "type": "arrow",
      "x": -2363.5445290323996,
      "y": 412.98993643947506,
      "width": 696.6263333982229,
      "height": 315.51179725418115,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4O",
      "roundness": {
        "type": 2
      },
      "seed": 326956804,
      "version": 181,
      "versionNonce": 1064774020,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741123990459,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -436.09710669495416,
          -123.03413466455936
        ],
        [
          -696.6263333982229,
          -315.51179725418115
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": {
        "elementId": "ywMtwlfk10-RKA2sfPe_5",
        "focus": -1.42721564095939,
        "gap": 14
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "XCWaeTQZ3SuctQu7en0CG",
      "type": "text",
      "x": -3016.3640101444134,
      "y": -453.67508736620016,
      "width": 197.58281425730897,
      "height": 38.30226010158649,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4Q",
      "roundness": null,
      "seed": 1908261308,
      "version": 80,
      "versionNonce": 1189237380,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124151640,
      "link": null,
      "locked": false,
      "text": "Data Collection",
      "fontSize": 28.372044519693695,
      "fontFamily": 6,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Data Collection",
      "autoResize": true,
      "lineHeight": 1.35
    },
    {
      "id": "Xjx16wcQzRT3P0NtFUv5J",
      "type": "text",
      "x": -3016.3640101444134,
      "y": -388.4674662941678,
      "width": 212.50649099713087,
      "height": 38.30226010158649,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4R",
      "roundness": null,
      "seed": 931246852,
      "version": 54,
      "versionNonce": 1292175292,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124151640,
      "link": null,
      "locked": false,
      "text": "Data Annotation",
      "fontSize": 28.372044519693695,
      "fontFamily": 6,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Data Annotation",
      "autoResize": true,
      "lineHeight": 1.35
    },
    {
      "id": "mh1ARuDdmUgdp6L0KS-FY",
      "type": "text",
      "x": -3016.3640101444134,
      "y": -323.2598452221354,
      "width": 181.8646928112455,
      "height": 38.30226010158649,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4U",
      "roundness": null,
      "seed": 822503996,
      "version": 52,
      "versionNonce": 930963972,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124151640,
      "link": null,
      "locked": false,
      "text": "KG Interaction",
      "fontSize": 28.372044519693695,
      "fontFamily": 6,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "KG Interaction",
      "autoResize": true,
      "lineHeight": 1.35
    },
    {
      "id": "pYo91lgJlL52iH2Fnuxdc",
      "type": "text",
      "x": -3016.3640101444134,
      "y": -258.0522241501031,
      "width": 203.96648098193577,
      "height": 38.30226010158649,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4V",
      "roundness": null,
      "seed": 1635746436,
      "version": 59,
      "versionNonce": 319074364,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124151640,
      "link": null,
      "locked": false,
      "text": "User Interaction",
      "fontSize": 28.372044519693695,
      "fontFamily": 6,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "User Interaction",
      "autoResize": true,
      "lineHeight": 1.35
    },
    {
      "id": "INli_Qp9d7Nxl5SIqNY7o",
      "type": "rectangle",
      "x": -3372.2414158176866,
      "y": -707.0640552590594,
      "width": 1873.7379528109834,
      "height": 1416.8129431600341,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4W",
      "roundness": {
        "type": 3
      },
      "seed": 1144189060,
      "version": 66,
      "versionNonce": 1286659516,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124169790,
      "link": null,
      "locked": false
    },
    {
      "id": "yyTcAVFlme9xtHA1h_Pp9",
      "type": "text",
      "x": -2883.6936369219607,
      "y": -670.0091590108876,
      "width": 896.6423950195312,
      "height": 57.32145744178912,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b4X",
      "roundness": null,
      "seed": 13744900,
      "version": 109,
      "versionNonce": 1289920316,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1741124218866,
      "link": null,
      "locked": false,
      "text": "Multi-Agent System for News Evaluation",
      "fontSize": 45.8571659534313,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Multi-Agent System for News Evaluation",
      "autoResize": true,
      "lineHeight": 1.25
    }
  ],
  "appState": {
    "gridSize": 20,
    "gridStep": 5,
    "gridModeEnabled": false,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}





## Agent Architecture Interaction Diagram:

Anticipated Multi-Agent System Workflow:

1-  User provides  a topic or article query to the system→ **Agent7** checks for existing knowledge.

2- If knowledge is outdated, it requests fresh updates from **Agent2**.

3- **Agent3** & **Agent4** analyze the bias and fact check new data before storage.

4- **Agent5** integrates verified data into knowledge graph.

5- **Agent6** generates an unbiased, multi-source summary.

6- **Agent7** returns a response with neutral summary, bias trends, fact-checks, and balanced perspectives.


```bash
Diagram
```
## Knowledge Graph

Structure:
![project_KG_schema](https://github.com/user-attachments/assets/3a0c1cde-cd08-42c9-bdff-58ccf2b44d90)

## Tech Stack:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Pytorch-%23FF6F00.svg?style=for-the-badge&logo=Pytorch&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-3670A0?style=for-the-badge&logo=Neo4j&logoColor=ffdd54)
![Pytorch](https://img.shields.io/badge/Sql-%23FF6F00.svg?style=for-the-badge&logo=Sql&logoColor=white)
![React](https://img.shields.io/badge/Docker-%2320232a.svg?style=for-the-badge&logo=Docker&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Aws-%23FF6F00.svg?style=for-the-badge&logo=Aws&logoColor=white)


## Project Approach:
The project will proceed in several phases:

Requirement Analysis: Collaborate with lead researchers to define key components of News knowledge sharing experiences and specify chatbot performance requirements.
## Technical Phase 

1. Week1. Environment Setup and technology stack Selection
      - Setup Tech stack environment
      -  Choose LLM frameworks
      - select graph database
      - Setup project documentation 
2. Week2: Basic agent framework Implementation /Data collection 
      - Implement basic agent communication 
      - Create Basic UI prototype
      -  Setup testing environment 
      - News article scrapping/Data preprocessing/API Integration
3. Week 3: Knowledge Graph Agent 
      - Graph database setup
      - Entity Extraction 
      - Relationship Mapping 
      - Dynamic update mechanism
4. Week4: Basic Agent communication 
      - Inter-agent messaging
      - Memory sharing implementation
      - State Management 
5. Week5: Specialized Agent Development(Bias and Summarization Agent)
      - Bias Detection Agent 
      - Bias detection models
      - Pattern recognition
      - Source Credibility analysis
      - Contextual analysis
      - Text Summarization models 
      - Bias removal techniques
      - Context Preservation
      - Output formatting
6. Integration and Enhancement/UI Development
      - System Integration/Component integration
      - End-to-end testing 
      - Performance Optimization
      - user interface refinement
      - interactive features
      - Visualization components
7. Testing and Documentation 
      - Comprehensive testing 
      - Unit Testing 
      - Integration testing 
      - Performance testing 
      - User acceptance testing



## Research Writing Phase/Structure 

1. Introduction
   - Problem Statement
   - Current Challenges
   - Proposed Solution

2. Related Work
    - Existing Bias Detection Methods
    - Multi-Agent Systems in NLP
    - News Summarization Techniques

3. Methodology
     - System Architecture
     - Agent Descriptions
     - Implementation Details

4. Experiments
    - Dataset Description
    - Evaluation Metrics
    - Results Analysis

5. Discussion
   - Comparative Analysis
   - Limitations
   - Future Work


## Folder Structure


```

├── src
│   ├── component
│   
├── demo  |
│   └── fig
├── full_report
│   ├── Latex_report
│   │   └── fig
│   ├── Markdown_Report
│   └── Word_Report
├── presentation
└── research_paper
    ├── Latex
    │   └── Fig
    └── Word
```

___



## Contact
**Advisor: Amir Jafari**

   Email: ajafari@gmail.com

   The George Washington University, Washington DC

   Data Science Program

   GitHub: https://github.com/amir-jafari/Capstone


