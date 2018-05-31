#!/usr/bin/env python

# (C) Copyright 2018 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import cdsapi


c = cdsapi.Client()


c.retrieve("sis-water-quantity-swicca",{"time_aggregation": "means_for_each_month", "format": "tgz", "period": "2011-2040", "emissions_scenario": "rcp_2_6", "variable": "wetness_2", "spatial_resolution": "0_5"})
