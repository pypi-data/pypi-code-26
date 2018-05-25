#!python3
"""
    =======
    symbols
    =======
    A library of static symbols that can be imported to your work.
    The symbols are defined in valid stream text format, so it should
    be easily extended even without the assistance of other program
"""
"""
    Reference
    =========

    # pdf generic commands
    LineTo = "LineTo"
    MoveTo = "MoveTo"
    Stroke = "Stroke"
    Close = "Close"
    Close_Stroke = "Close_Stroke"
    Fill = "Fill"
    Fill_Stroke = "Fill_Stroke"
    Close_Fill_Stroke = "Close_Fill_Stroke"

    Translate = "Translate"
    CurveTo = "CurveTo"
    RotateCoordinate = "RotateCoordinate"
    SetLineWidth = "SetLineWidth"
    SetDash = "SetDash"
    SetLineJoin = "SetLineJoin"
    SetLineColor = "SetLineColor"
    SetFillColor = "SetFillColor"
    SetFont = "SetFont"
    Text= "Text"
    Picture = "Picture"


    Important
    ~~~~~~~~~
    The end of the final operation must be terminated with EOL \n
"""
Arrow_Down = "MoveTo,0,0\n"\
           + "LineTo,10,30\n"\
           + "LineTo,-10,30\n"\
           + "Close\n"\
           + "Fill\n"

Arrow_Up = "MoveTo,0,0\n"\
         + "LineTo,10,-30\n"\
         + "LineTo,-10,-30\n"\
         + "Close\n"\
         + "Fill\n"
