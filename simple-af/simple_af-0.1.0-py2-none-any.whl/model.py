class Effect(object):
    def __init__(self):
        pass

    def next_frame(self, pixels, now):
        # type: (Pixels, float) -> None
        """Implement this method to render the next frame.

        Args:
            pixels: rgb values to be modified in place
            now: represents the time (in seconds)
            collaboration_state: a dictionary that can be modified by
                a CollaborationManager before any effects apply
            osc_data: contains the data sent in since the last frame
                (for buttons), as well as store fader states Use the
                osc data to get station clients if you need to send
                button feedback.
        """
        raise NotImplementedError("All effects must implement next_frame")
        # TODO: Use abc

    def after_all_scenes_loaded(self):
        pass

    def scene_starting(self, now):
        pass

    def scene_ended(self):
        pass

    def is_completed(self, t):
        return False


class MultiEffect(Effect):
    def __init__(self, *effects):
        Effect.__init__(self)
        self.effects = list(effects)
        self.clear_effects_after = True

    def after_all_scenes_loaded(self):
        for e in self.effects:
            e.after_all_scenes_loaded()

    def scene_starting(self, now):
        """Initialize a scene
        :param osc_data:
        """
        for e in self.effects:
            e.scene_starting(now)

    def count(self):
        return len(self.effects)

    def scene_ended(self):
        for e in self.effects:
            e.scene_ended()
        if self.clear_effects_after:
            self.effects = []

    def next_frame(self, pixels, t):
        self.before_rendering(pixels, t)

        for e in self.effects:
            e.next_frame(pixels, t)

    def before_rendering(self, pixels, t):
        self.cleanup_terminated_effects(pixels, t)

    def cleanup_terminated_effects(self, pixels, t):
        # type: (Pixel, long) -> None
        # TODO Debugging code here?
        self.effects[:] = [e for e in self.effects if not e.is_completed(t)]

    def add_effect(self, effect, before=False):
        # type: (Effect) -> None
        if effect:  # Ignore None
            if before:
                self.effects.insert(0, effect)
            else:
                self.effects.append(effect)


class Scene(MultiEffect):
    def __init__(self, name, effects=[]):
        # str, CollaborationManager, List[Effect] -> None
        MultiEffect.__init__(self, *effects)
        self.name = name
        self.clear_effects_after = False

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def render(self, pixels, t):
        # TODO Why didn't super(MultiEffect, self) work?
        self.next_frame(pixels, t)