def get_panel_to_add_dashboard(title, query, y_axis_label,id_panel):
    return {
        "aliasColors": {},
        "bars": False,
        "dashLength": 10,
        "dashes": False,
        "datasource": "backend_siscorvac",
        "decimals": 3,
        "fill": 1,
        "gridPos": {
            "h": 9,
            "w": 12,
            "x": 0,
            "y": 0
        },
        "id": id_panel,
        "legend": {
            "alignAsTable": True,
            "avg": True,
            "current": True,
            "max": True,
            "min": True,
            "show": True,
            "total": False,
            "values": True
        },
        "lines": True,
        "linewidth": 1,
        "nullPointMode": "null",
        "percentage": False,
        "pointradius": 2,
        "points": True,
        "renderer": "flot",
        "seriesOverrides": [],
        "spaceLength": 10,
        "stack": False,
        "steppedLine": False,
        "targets": [
            {
                "alias": "",
                "format": "time_series",
                "rawSql": query,
                "refId": "A"
            }
        ],
        "thresholds": [],
        "timeFrom": None,
        "timeShift": None,
        "title": title,
        "tooltip": {
            "shared": True,
            "sort": 0,
            "value_type": "individual"
        },
        "type": "graph",
        "xaxis": {
            "buckets": None,
            "mode": "time",
            "name": None,
            "show": True,
            "values": []
        },
        "yaxes": [
            {
                "format": "short",
                "label": y_axis_label,
                "logBase": 1,
                "max": None,
                "min": None,
                "show": True
            },
            {
                "format": "short",
                "label": None,
                "logBase": 1,
                "max": None,
                "min": None,
                "show": True
            }
        ]
    }
    # return {
    #     "aliasColors": {},
    #     "bars": False,
    #     "dashLength": 10,
    #     "dashes": False,
    #     "datasource": "bachend_siscorvac",
    #     "decimals": 3,
    #     "fill": 1,
    #     "gridPos": {
    #         "h": 9,
    #         "w": 12,
    #         "x": 0,
    #         "y": 9
    #     },
    #     "id": None,
    #     "legend": {
    #         "alignAsTable": True,
    #         "avg": True,
    #         "current": True,
    #         "hideEmpty": True,
    #         "hideZero": False,
    #         "max": True,
    #         "min": True,
    #         "show": True,
    #         "total": False,
    #         "values": True
    #     },
    #     "lines": True,
    #     "linewidth": 1,
    #     "links": [],
    #     "nullPointMode": "null",
    #     "percentage": False,
    #     "pointradius": 2,
    #     "points": True,
    #     "renderer": "flot",
    #     "seriesOverrides": [],
    #     "spaceLength": 10,
    #     "stack": False,
    #     "steppedLine": False,
    #     "targets": [
    #         {
    #             "alias": "",
    #             "format": "time_series",
    #             "rawSql": query,
    #             "refId": "A"
    #         }
    #     ],
    #     "thresholds": [],
    #     "timeFrom": True,
    #     "timeShift": True,
    #     "title": title,
    #     "tooltip": {
    #         "shared": True,
    #         "sort": 0,
    #         "value_type": "individual"
    #     },
    #     "type": "graph",
    #     "xaxis": {
    #         "buckets": True,
    #         "mode": "time",
    #         "name": True,
    #         "show": True,
    #         "values": []
    #     },
    #     "yaxes": [
    #         {
    #             "format": format_unit_y_axes,
    #             "label": "Humedad",
    #             "logBase": 1,
    #             "max": 0,
    #             "min": 100,
    #             "show": True
    #         },
    #         {
    #             "format": "short",
    #             "label": "",
    #             "logBase": 1,
    #             "max": True,
    #             "min": True,
    #             "show": True
    #         }
    #     ]
    # }
