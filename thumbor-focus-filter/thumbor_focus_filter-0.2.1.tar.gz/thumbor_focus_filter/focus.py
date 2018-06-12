#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from thumbor.filters import BaseFilter, filter_method, PHASE_AFTER_LOAD
from thumbor.point import FocalPoint

class Filter(BaseFilter):
    phase = PHASE_AFTER_LOAD

    @filter_method(
        BaseFilter.DecimalNumber,#percentage_width
        BaseFilter.DecimalNumber,#percentage_height
    )
    def focus(self, percentage_width, percentage_height):
        # change to percentage
        percentage_width = float(percentage_width / 100)
        percentage_height = float(percentage_height / 100)
        # missing percentage
        missing_percentage_width = 1.0 - percentage_width
        missing_percentage_height = 1.0 - percentage_height
        # retrive original image
        source_width, source_height = self.context.request.engine.size
        #logging.warn('source focus %r %r', source_width, source_height)
        # retrieve target image
        target_width = self.context.request.width
        target_height = self.context.request.height
        #logging.warn('target focus %r %r', target_width, target_height)
        
        top = (percentage_width * source_width) - ((missing_percentage_width * source_width) / 2)
        left = (percentage_height * source_height) - ((missing_percentage_height * source_height) / 2)
        bottom = (percentage_width * source_width) + ((missing_percentage_width * source_width) / 2)
        right = (percentage_height * source_height) + ((missing_percentage_height * source_height) / 2)
        
        width = right - left
        height = bottom - top
        box = (top, left, width, height)

        left, top, width, height = box
        self.context.request.focal_points.append(
            FocalPoint.from_square(int(left), int(top), int(height), int(width), origin="Explicit")
        )
