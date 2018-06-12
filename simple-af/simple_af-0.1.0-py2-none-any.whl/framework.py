"""Framework for running animations and effects"""
from __future__ import absolute_import

import glob
import importlib
import os.path
import sys
import time
import pkg_resources
from collections import OrderedDict
from threading import Thread

from OSC import OSCServer

from simple_af._opc import Client
from simple_af.pixels import Pixels
from simple_af.state import STATE
from simple_af.osc_utils import OSCStorage
from simple_af.model import Scene

FAIL_ON_LOAD = True


class AnimationFramework(object):
    def __init__(self,
                 osc_server,
                 opc_client,
                 effects_dir,
                 scenes=None,
                 first_scene=None,):
        # type: (OSCServer, Client, List(OSCClient), {str, Scene}) -> None
        self.osc_server = osc_server
        self.opc_client = opc_client
        self.fps = STATE.fps

        # Load all scenes from effects package. Then set initial index and load it up
        loaded_scenes = load_scenes_and_fountains(effects_dir)
        if not loaded_scenes:
            raise Exception("No scenes found")
        self.scenes = scenes or loaded_scenes

        map(lambda s: s.after_all_scenes_loaded(), self.scenes.values())
        print self.scenes
        self.curr_scene = None
        self.queued_scene = self.scenes[first_scene if first_scene else self.scenes.keys()[0]]

        self.serve = False
        self.is_running = False
        STATE.osc_data = OSCStorage()
        print STATE.osc_data
        self.setup_osc_input_handlers()

    def next_scene_handler(self, path, tags, args, source):
        if not args or args[0] == "":
            self.next_scene()
        else:
            self.next_scene(int(args[0]))

    def select_scene_handler(self, path, tags, args, source):
        if args[0] == "":
            self.next_scene()
        else:
            self.pick_scene(args[0])

    def setup_osc_input_handlers(self):
        """
        :param faders: Dictionary of faders and their default values for each station
        :return:
        """

        # Set up scene control
        self.osc_server.addMsgHandler("/scene/next", self.next_scene_handler)
        self.osc_server.addMsgHandler("/scene/select", self.select_scene_handler)

        # self.osc_server.addMsgHandler("/scene/picknew", self.pick_new_scene_handler)

        print "Registering external osc handlers..."
        for ep in pkg_resources.iter_entry_points('simple_af.plugins.osc_handlers'):
            print "Registering", ep
            listener = ep.load()(self.osc_server)


        print "Registered all OSC Handlers"

    # ---- EFFECT CONTROL METHODS -----
    def poll_next_scene(self, now):
        """Change the scene by taking the queued scene and swapping it in.
        """

        if self.queued_scene:
            # Cache the scene queue locally so it can't be changed on us
            next_scene, last_scene, self.queued_scene = self.queued_scene, self.curr_scene, None
            #FIXME now?
            next_scene.scene_starting(time.time())
            #next_scene.scene_starting(self._last_scene_change_timestamp)
            self.curr_scene = next_scene  # Go!
            print '\tScene %s started\n' % self.curr_scene
            # Now give the last scene a chance to cleanup
            if last_scene:
                last_scene.scene_ended()

    def increment_osc_frame(self, clear=True):
        # type: (bool) -> None
        """Get the last frame of osc data and initialize the next frame"""
        # TODO: Do we need to explicitly synchronize here?
        STATE.osc_data.next_frame()

    def next_scene(self, increment=1):
        """ Move the selected scene forward or back from the at-large pool"""
        curr_idx = self.scenes.keys().index(self.curr_scene.name)
        new_idx = (curr_idx + increment) % len(self.scenes)
        self.pick_scene(self.scenes.keys()[new_idx])

    def pick_scene(self, scene_name):
        """ Change to a specific scene """
        if scene_name in self.scenes.keys():
            self.queued_scene = self.scenes[scene_name]
        else:
            print "Could not change scenes. Scene %s does not exist" % scene_name

    # ---- LIFECYCLE (START/STOP) METHODS ----

    def serve_in_background(self, daemon=True):
        # [function] -> Thread

        # Run scene manager in the background
        thread = Thread(target=self.serve_forever)
        thread.setName("SceneManager")
        thread.setDaemon(True)
        thread.start()
        return thread

    def serve_forever(self):
        # [function] -> None

        self.serve = True

        self.fps_frame_time = 1.0 / self.fps
        self.fps_warn_threshold = self.fps_frame_time * .2  # Warn if 20% overage

        print '\tsending pixels forever (quit or control-c to exit)...'
        self.is_running = True
        self.pixels = Pixels(STATE.layout)

        try:
            while self.serve:
                self._serve()
        finally:
            self.is_running = False
            print "Scene Manager Exited"

    def _serve(self):
        # TODO : Does this create lots of GC?
        frame_start_time = time.time()
        target_frame_end_time = frame_start_time + self.fps_frame_time
        self.increment_osc_frame()

        self.poll_next_scene(now=frame_start_time)

        # Create the pixels, set all, then put
        self.pixels[:] = 0
        self.curr_scene.render(self.pixels, frame_start_time)
        render_timestamp = time.time()

        #Now send
        self.pixels.put(self.opc_client)

        # Okay, now we're done for real. Wait for target FPS and warn if too slow
        completed_timestamp = time.time()
        sleep_amount = target_frame_end_time - completed_timestamp
        self._log_timings(frame_start_time, render_timestamp, completed_timestamp, sleep_amount)
        if sleep_amount > 0:
            time.sleep(sleep_amount)

    def _log_timings(self, frame_start_time, render_ts, completed_ts, sleep_amount):
        if sleep_amount < 0 and -sleep_amount > self.fps_warn_threshold:
            print sleep_amount, self.fps_warn_threshold
            # Note: possible change_scene() is called in between. Issue is trivial though
            msg = "WARNING: scene {} is rendering slowly. Total: {} Render: {} OPC: {}"
            print msg.format(self.curr_scene.name, completed_ts - frame_start_time,
                             render_ts - frame_start_time, completed_ts - render_ts)

    def shutdown(self):
        self.serve = False


def load_scenes_and_fountains(effects_dir=None):
    # type: (str) -> {str, Scene}
    if not effects_dir:
        pwd = os.path.dirname(__file__)
        effects_dir = os.path.abspath(os.path.join(pwd, '..', 'effects'))
    # effects might import other sub-effects from the effects directory
    # so we need it to be on the path
    sys.path.append(effects_dir)
    scenes = OrderedDict()
    fountains = []
    for filename in glob.glob(os.path.join(effects_dir, '*.py')):
        pkg_name = os.path.basename(filename)[:-3]
        if pkg_name.startswith("_"):
            continue
        load_scenes_from_file(pkg_name, scenes)
    print "Loaded %s scenes from %s directory\n" % (len(scenes), effects_dir)
    STATE.fountains = fountains
    return scenes


def load_scenes_from_file(pkg_name, scenes):
    # type: (str, {str, Scene}) -> None
    try:
        effect_dict = importlib.import_module(pkg_name)
        if hasattr(effect_dict, '__all__'):
            print('WARNING. Usage of __all__ to define scenes is deprecated. '
                  'Use the SCENES variable instead')
            return
        if not hasattr(effect_dict, 'SCENES'):
            print 'Skipping {}. No SCENES are defined'.format(pkg_name)
            return
        save_scenes(effect_dict.SCENES, scenes)
    except (ImportError, SyntaxError) as e:
        if FAIL_ON_LOAD:
            raise
        import traceback
        print "WARNING: could not load effect %s" % pkg_name
        traceback.print_exc()
        print


def save_scenes(input_scenes, output_scenes):
    for scene in input_scenes:
        if not isinstance(scene, Scene):
            print "Got scene %s not of type Scene" % scene
            continue
        if scene.name in output_scenes:
            print "Cannot register scene %s. Scene with name already exists" % scene.name
            continue

        print "Registering %s" % scene
        output_scenes[scene.name] = scene


def get_first_non_empty(pixels):
    return next(pix for pix in pixels if pix is not None)