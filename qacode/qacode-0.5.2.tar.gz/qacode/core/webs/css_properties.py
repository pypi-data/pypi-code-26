# -*- coding: utf-8 -*-
"""TODO: doc module"""


from enum import Enum


class CssProperty(Enum):
    """TODO: doc class"""

    # background properties
    BACKGROUND = 'background'
    BACKGROUND_COLOR = 'background-color'
    BACKGROUND_IMAGE = 'background-image'
    BACKGROUND_REPEAT = 'background-repeat'
    BACKGROUND_ATTACHMENT = 'background-attachment'
    BACKGROUND_POSITION = 'background-position'
    BACKGROUND_CLIP = 'background-clip'
    BACKGROUND_ORIGIN = 'background-origin'
    BACKGROUND_SIZE = 'background-size'
    OPACITY = 'opacity'
    BOX_SHADOW = 'box-shadow'
    BOX_SIZING = 'box-sizing'
    # border properties
    BORDER = 'border'
    BORDER_COLOR = 'border-color'
    BORDER_STYLE = 'border-style'
    BORDER_WIDTH = 'border-width'
    BORDER_RADIUS = 'border-radius'
    BORDER_TOP_LEFT_RADIUS = 'border-top-left-radius'
    BORDER_TOP_RIGHT_RADIUS = 'border-top-right-radius'
    BORDER_BOTTOM_RIGHT_RADIUS = 'border-bottom-right-radius'
    BORDER_BOTTOM_LEFT_RADIUS = 'border-bottom-left-radius'
    BORDER_TOP = 'border-top'
    BORDER_RIGHT = 'border-right'
    BORDER_BOTTOM = 'border-bottom'
    BORDER_LEFT = 'border-left	'
    BORDER_BOTTOM_COLOR = 'border-bottom-color'
    BORDER_BOTTOM_STYLE = 'border-bottom-style'
    BORDER_BOTTOM_WIDTH = 'border-bottom-width'
    BORDER_LEFT_COLOR = 'border-left-color'
    BORDER_LEFT_STYLE = 'border-left-style'
    BORDER_LEFT_WIDTH = 'border-left-width'
    BORDER_RIGHT_COLOR = 'border-right-color'
    BORDER_RIGHT_STYLE = 'border-right-style'
    BORDER_RIGHT_WIDTH = 'border-right-width'
    BORDER_TOP_COLOR = 'border-top-color'
    BORDER_TOP_STYLE = 'border-top-style'
    BORDER_TOP_WIDTH = 'border-top-width'
    # borders properties for tables
    BORDER_COLLAPSE = 'border-collapse'
    BORDER_SPACING = 'border-spacing'
    CAPTION_SIDE = 'caption-side'
    EMPTY_CELLS = 'empty-cells'
    TABLE_LAYOUT = 'table-layout'
    # borders properties for images
    BORDER_IMAGE = 'border-image'
    BORDER_IMAGE_SOURCE = 'border-image-source'
    BORDER_IMAGE_SLICE = 'border-image-slice'
    BORDER_IMAGE_WIDTH = 'border-image-width'
    BORDER_IMAGE_OUTSET = 'border-image-outset'
    BORDER_IMAGE_REPEAT = 'border-image-repeat'
    # margin properties
    MARGIN = 'margin'
    MARGIN_BOTTOM = 'margin-bottom'
    MARGIN_LEFT = 'margin-left'
    MARGIN_RIGHT = 'margin-right'
    MARGIN_TOP = 'margin-top'
    # padding properties
    PADDING = 'padding'
    PADDING_BOTTOM = 'padding-bottom'
    PADDING_LEFT = 'padding-left'
    PADDING_RIGHT = 'padding-right'
    PADDING_TOP = 'padding-top'
    # height, width properties
    HEIGHT = 'height'
    MIN_HEIGHT = 'min-height'
    MAX_HEIGHT = 'max-height'
    WIDTH = 'width'
    MIN_WIDTH = 'min-width'
    MAX_WIDTH = 'max-width'
    # outline properties
    OUTLINE = 'outline'
    OUTLINE_COLOR = 'outline-color'
    OUTLINE_OFFSET = 'outline-offset'
    OUTLINE_STYLE = 'outline-style'
    OUTLINE_WIDTH = 'outline-width'
    # text properties
    TEXT_ALIGN = 'text-align'
    TEXT_DECORATION = 'text-decoration'
    TEXT_INDENT = 'text-indent'
    TEXT_SHADOW = 'text-shadow'
    TEXT_TRANSFORM = 'text-transform'
    TEXT_OVERFLOW = 'text-overflow'
    TEXT_ALIGN_LAST = 'text-align-last'
    TEXT_JUSTIFY = 'text-justify'
    UNICODE_BIDI = 'unicode-bidi'
    VERTICAL_ALIGN = 'vertical-align'
    LETTER_SPACING = 'letter-spacing'
    LINE_HEIGHT = 'line-height'
    WHITE_SPACE = 'white-space	'
    WORD_SPACING = 'word-spacing'
    WORD_BREAK = 'word-break'
    WORD_WRAP = 'word-wrap'
    COLOR = 'color'
    DIRECTION = 'direction'
    # fonts properties
    FONT = 'font'
    FONT_FAMILY = 'font-family'
    FONT_SIZE = 'font-size'
    FONT_STYLE = 'font-style'
    FONT_VARIANT = 'font-variant'
    FONT_WEIGHT = 'font-weight'
    # lists properties
    LIST_STYLE = 'list-style'
    LIST_STYLE_IMAGE = 'list-style-image'
    LIST_STYLE_POSITION = 'list-style-position'
    LIST_STYLE_TYPE = 'list-style-type'
    # display properties
    DISPLAY = 'display'
    VISIBILITY = 'visibility'
    # position properties
    Z_INDEX = 'z-index'
    CLIP = 'clip'
    POSITION = 'position'
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'
    LEFT = 'left'
    CLEAR = 'clear'
    FLOAT = 'float'
    # overflow properties
    OVERFLOW = 'overflow'
    OVERFLOW_X = 'overflow-x'
    OVERFLOW_Y = 'overflow-y'
    # transforms properties
    TRANSFORM = 'transform'
    TRANSFORM_ORIGIN = 'transform-origin'
    TRANSFORM_STYLE = 'transform-style	'
    PERSPECTIVE = 'perspective'
    PERSPECTIVE_ORIGIN = 'perspective-origin'
    BACKFACE_VISIBILITY = 'backface-visibility'
    # transition properties
    TRANSITION = 'transition'
    TRANSITION_DELAY = 'transition-delay'
    TRANSITION_DURATION = 'transition-duration'
    TRANSITION_PROPERTY = 'transition-property'
    TRANSITION_TIMING_FUNCTION = 'transition-timing-function'
    # animations properties
    ANIMATION = 'animation'
    ANIMATION_DELAY = 'animation-delay'
    ANIMATION_DIRECTION = 'animation-direction'
    ANIMATION_DURATION = 'animation-duration'
    ANIMATION_FILL_MODE = 'animation-fill-mode'
    ANIMATION_ITERATION_COUNT = 'animation-iteration-count'
    ANIMATION_NAME = 'animation-name'
    ANIMATION_PLAY_STATE = 'animation-play-state'
    ANIMATION_TIMING_FUNCTION = 'animation-timing-function'
    # object-fit property
    OBJECT_FIT = 'object-fit'
    # content property (text as CSS, from attr data-some='content_value')
    CONTENT = 'content'
    # multi-columns properties (for tables)
    COLUMNS = 'columns'
    COLUMN_COUNT = 'column-count'
    COLUMN_FILL = 'column-fill'
    COLUMN_GAP = 'column-gap'
    COLUMN_RULE = 'column-rule'
    COLUMN_RULE_COLOR = 'column-rule-color'
    COLUMN_RULE_STYLE = 'column-rule-style'
    COLUMN_RULE_WIDTH = 'column-rule-width'
    COLUMN_SPAN = 'column-span'
    COLUMN_WIDTH = 'column-width'
    # user interface properties (behaviour editions, care)
    RESIZE = 'resize'
    # flexbox properties (CSS3)
    FLEX = 'flex'
    FLEX_DIRECTION = 'flex-direction'
    FLEX_WRAP = 'flex-wrap'
    FLEX_FLOW = 'flex-flow'
    ORDER = 'order'
    JUSTIFY_CONTENT = 'justify-content'
    ALIGN = 'align'
    ALIGN_ITEMS = 'align-items'
    ALIGN_CONTENT = 'align-content'

    @classmethod
    def get_css_property(cls):
        """Return enum values"""
        return [item.value for item in CssProperty]

    @classmethod
    def has_css_property(cls, value):
        """Returns True if enum have value"""
        return any(value == item.value for item in cls)
