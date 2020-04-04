
export const treeTrueData = {
    "name": "G PHYSICS",
    "symbol": "G",
    "prob": 1,
    "true": true,
    "children": [
        {
            "name": "G06 COMPUTING; CALCULATING; COUNTING",
            "symbol": "G06",
            "prob": 0.8,
            "true": true,
            "children": [
                {
                    "name": "G06Q DATA PROCESSING SYSTEMS OR METHODS, SPECIALLY ADAPTED FOR ADMINISTRATIVE, COMMERCIAL, FINANCIAL, MANAGERIAL, SUPERVISORY OR FORECASTING PURPOSES; SYSTEMS OR METHODS SPECIALLY ADAPTED FOR ADMINISTRATIVE, COMMERCIAL, FINANCIAL, MANAGERIAL, SUPERVISORY OR FORECASTING PURPOSES, NOT OTHERWISE PROVIDED FOR",
                    "symbol": "G06Q",
                    "prob": 0.5,
                    "true": true,
                    "children": [
                        {
                            "name": "G06Q 10/00  Administration; Management",
                            "symbol": "G06Q 10/00",
                            "prob": 1,
                            "true": true,
                            "children": [
                                {
                                    "name": "G06Q 10/02 .Reservations, e.g. for tickets, services or events",
                                    "symbol": "G06Q 10/02",
                                    "prob": 1,
                                    "true": true,
                                    "children": [{
                                        "name": "G06Q 10/025  ..{Price estimation or determination}",
                                        "prob": 1,
                                        "true": true,
                                    }]
                                }
                            ]

                        },
                        {
                            "name": "G06Q 30/00  Commerce, e.g. shopping or e-commerce",
                            "symbol": "G06Q 30/00",
                            "prob": 1,
                            "true": true,
                            "children": [
                                {
                                    "name": "G06Q 30/02 .Marketing, e.g. market research and analysis, surveying, promotions, advertising, buyer profiling, customer management or rewards; Price estimation or determination",
                                    "symbol": "G06Q 30/02",
                                    "prob": 1,
                                    "true": true,
                                    "children": [{
                                        "name": "G06Q 30/0283  ..{Price estimation or determination}",
                                        "prob": 1,
                                        "true": true,
                                    }]
                                }
                            ]
                        },
                        {
                            "name": "G06Q 40/00 Finance; Insurance; Tax strategies; Processing of corporate or income taxes",
                            "symbol": "G06Q 40/00",
                            "prob": 1,
                            "true": true,
                            "children": [{
                                "name": "G06Q 40/02 .Banking, e.g. interest calculation...",
                                "prob": 1
                            }]
                        }
                    ]
                }
            ]
        },
    ]
}
export const treePredictedData =
{
    "name": "G PHYSICS",
    "symbol": "G",
    "prob": 1,
    "true": true,
    "children": [
        {
            "name": "G06 COMPUTING; CALCULATING; COUNTING",
            "symbol": "G06",
            "prob": 0.8,
            "true": true,
            "children": [
                {
                    "name": "G06Q DATA PROCESSING SYSTEMS OR METHODS, SPECIALLY ADAPTED FOR ADMINISTRATIVE, COMMERCIAL, FINANCIAL, MANAGERIAL, SUPERVISORY OR FORECASTING PURPOSES; SYSTEMS OR METHODS SPECIALLY ADAPTED FOR ADMINISTRATIVE, COMMERCIAL, FINANCIAL, MANAGERIAL, SUPERVISORY OR FORECASTING PURPOSES, NOT OTHERWISE PROVIDED FOR",
                    "symbol": "G06Q",
                    "prob": 0.5,
                    "true": true,
                    "children": [
                        {
                            "name": "G06Q 30/00  Commerce, e.g. shopping or e-commerce",
                            "symbol": "G06Q 30/00",
                            "prob": 1,
                            "true": true,
                            "children": [
                                {
                                    "name": "G06Q 30/02 .Marketing, e.g. market research and analysis, surveying, promotions, advertising, buyer profiling, customer management or rewards; Price estimation or determination",
                                    "symbol": "G06Q 30/02",
                                    "prob": 0.5,
                                    "true": true,
                                    "children": [{
                                        "name": "G06Q 30/0283  ..{Price estimation or determination}",
                                        "symbol": "G06Q 30/0283",
                                        "prob": 1,
                                        "true": true,
                                    }]
                                }
                            ]
                        }, {
                            "name": "G06Q 10/00  Administration; Management",
                            "symbol": "G06Q 10/00",
                            "prob": -1,
                            "true": true,
                            "children": [
                                {
                                    "name": "G06Q 10/02 .Reservations, e.g. for tickets, services or events",
                                    "symbol": "G06Q 10/02",
                                    "prob": -1,
                                    "true": true,
                                    "children": [{
                                        "name": "G06Q 10/025  ..{Price estimation or determination}",
                                        "symbol": "G06Q 10/025",
                                        "prob": -1,
                                        "true": true,
                                    }]
                                }
                            ]

                        }
                    ]
                },
                {
                    "name": "G06Q 40/00 Finance; Insurance; Tax strategies; Processing of corporate or income taxes",
                    "symbol": "G06Q 40/00",
                    "prob": 0.3,
                    "children": [{
                        "name": "G06Q 40/02 .Banking, e.g. interest calculation...",
                        "symbol": "G06Q 40/02",
                        "prob": 1
                    }]
                }
            ]
        },
        {
            "name": "G08 SIGNALLING",
            "symbol": "G08",
            "prob": 0.2,
            "true": false
        }
    ]
};