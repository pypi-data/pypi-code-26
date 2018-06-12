DURATION=30


SCENES = [
    #Scene(
    #    "movingslice",
    #    effects=[MovingSlice()]
    #),
    #Scene(
    #    "Letters",
    #    effects=[
    #        example.SolidBackground(color=(150,0,0)),
    #        bitmap.MidiLetterListener()
    #    ]
    #),
    """
    Scene(
        "DrumHarderRows",
        effects=[
            example.SolidBackground(color=(60, 0, 0)),
            bitmap.StaticBitmap(bitmap.CACHED_WORDS['DRUM HARDER'], (100, 100, 100), -1, 1),
            #example.MovingColor()
            MidiLauncher(midi_effects.DrumHitRow)
        ]
    ),
    Scene(
        "SuperTony",
        effects=[
            example.SolidBackground(color=(255, 0, 0)),
            FlashTony(),
            MidiLauncher(midi_effects.DrumHitRow)
        ]
    )
    """
]