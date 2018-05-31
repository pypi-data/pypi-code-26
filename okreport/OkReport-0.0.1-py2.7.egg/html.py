BASIC_REPORT_HTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Ok Report</title>
<style type="text/css">
		.tablerow0 {
			background: #EEEEEE;
		}

		.tablerow1 {
			background: white;
		}

		.detailrow0 {
			background: #EEEEEE;
		}

		.detailrow1 {
			background: white;
		}

		.tableheader {
			background: #b9b9fe;
			font-size: larger;
		}

		.tablerow0:hover, .tablerow1:hover {
			background: #aaffaa;
		}

		.priority-1 {
		    color: red;
		    font-weight: bold;
		}
		.priority-2 {
		    color: orange;
		    font-weight: bold;
		}
		.priority-3 {
		    color: green;
		    font-weight: bold;
		}
		.priority-4 {
		    color: blue;
		    font-weight: bold;
		}
		</style>
</head>
<body>"""

END_HTML = """    </body>
</html>"""


def addTd(value, right=False):
    if right:
        fragment = "<td align=\"right\">"
    else:
        fragment = "<td>\n"
    fragment += value
    fragment += "</td>"
    return fragment
